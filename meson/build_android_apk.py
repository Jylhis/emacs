#!/usr/bin/env python3
"""End-to-end Android APK builder for the Emacs Android port.

Driven by meson's `apk` alias target.  Invokes the Android SDK
build-tools (aapt2, d8, zipalign, apksigner) plus the JDK (javac) and
m4 in sequence.  All paths are passed explicitly so the same script
works in interactive shells and inside Nix sandboxes.

Steps (mirrors the deleted autotools java/Makefile.in flow):
  1. m4-substitute AndroidManifest.xml from AndroidManifest.xml.in
  2. aapt2 compile + link res/ + manifest -> base.apk + R.java
  3. javac all .java + R.java -> classes/
  4. d8 classes/ -> classes.dex
  5. assemble: copy libemacs.so into lib/arm64-v8a/, dex into root,
     staged assets into assets/, then zip into base.apk
  6. zipalign -p 4 -> aligned.apk
  7. apksigner sign with the configured keystore -> <out>.apk
"""

from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path


def run(cmd, cwd: Path | None = None, env: dict | None = None) -> None:
    pretty = " ".join(str(c) for c in cmd)
    sys.stderr.write(f"+ {pretty}\n")
    subprocess.run(cmd, cwd=cwd, env=env, check=True)


def find_jar(sdk: Path, api: int) -> Path:
    # SDK ships android.jar under platforms/android-<api>/android.jar;
    # accept the closest available API >= requested, then fall back to
    # the highest available.
    plats = sdk / "platforms"
    candidates = sorted(plats.glob("android-*"))
    if not candidates:
        sys.exit(f"build_android_apk: no platforms/ under {sdk}")
    exact = plats / f"android-{api}" / "android.jar"
    if exact.exists():
        return exact
    # Highest available.
    for d in reversed(candidates):
        jar = d / "android.jar"
        if jar.exists():
            return jar
    sys.exit(f"build_android_apk: no android.jar in {plats}")


def find_build_tools(sdk: Path) -> Path:
    bt = sdk / "build-tools"
    versions = sorted([d for d in bt.glob("*") if d.is_dir()])
    if not versions:
        sys.exit(f"build_android_apk: no build-tools under {sdk}")
    return versions[-1]


def m4_manifest(m4: str, template: Path, out: Path, version: str,
                min_api: int, target_api: int) -> None:
    cmd = [
        m4,
        f"-Dversion={version}",
        f"-DANDROID_MIN_SDK={min_api}",
        f"-DANDROID_TARGET_SDK={target_api}",
        # The shared user id macros expand to empty strings in the
        # default (non-Termux) configuration.
        "-DANDROID_SHARED_USER_ID=",
        "-DANDROID_SHARED_USER_NAME=",
        str(template),
    ]
    sys.stderr.write(f"+ {' '.join(cmd)} > {out}\n")
    with open(out, "wb") as fh:
        subprocess.run(cmd, check=True, stdout=fh)


def aapt2_compile(aapt2: Path, res_root: Path, out_dir: Path) -> list[Path]:
    out_dir.mkdir(parents=True, exist_ok=True)
    compiled = []
    # aapt2 compile takes either a single file or a --dir.  Use --dir
    # so we don't have to enumerate every drawable / values file.
    run([str(aapt2), "compile", "--dir", str(res_root),
         "-o", str(out_dir)])
    for p in out_dir.glob("*.flat"):
        compiled.append(p)
    return compiled


def aapt2_link(aapt2: Path, compiled: list[Path], manifest: Path,
               android_jar: Path, min_api: int, target_api: int,
               version_name: str, gen_java_dir: Path,
               out_apk: Path, assets_dir: Path | None) -> None:
    gen_java_dir.mkdir(parents=True, exist_ok=True)
    cmd = [
        str(aapt2), "link",
        "-I", str(android_jar),
        "--manifest", str(manifest),
        "--min-sdk-version", str(min_api),
        "--target-sdk-version", str(target_api),
        "--version-name", version_name,
        "--version-code", "30",
        "--java", str(gen_java_dir),
        "-o", str(out_apk),
    ]
    if assets_dir is not None:
        cmd += ["-A", str(assets_dir)]
    cmd += [str(p) for p in compiled]
    run(cmd)


def javac_all(javac: str, java_src_root: Path, gen_java_dir: Path,
              android_jar: Path, classes_dir: Path) -> None:
    classes_dir.mkdir(parents=True, exist_ok=True)
    java_files = sorted(java_src_root.rglob("*.java"))
    java_files += sorted(gen_java_dir.rglob("*.java"))
    if not java_files:
        sys.exit(f"build_android_apk: no .java sources under {java_src_root}")
    cmd = [
        javac, "-source", "1.8", "-target", "1.8",
        "-bootclasspath", str(android_jar),
        "-classpath", str(android_jar),
        "-d", str(classes_dir),
        "-Xlint:-options",
    ] + [str(f) for f in java_files]
    run(cmd)


def d8_dex(d8: str, classes_dir: Path, android_jar: Path,
           out_dir: Path, min_api: int) -> Path:
    out_dir.mkdir(parents=True, exist_ok=True)
    class_files = sorted(classes_dir.rglob("*.class"))
    if not class_files:
        sys.exit("build_android_apk: javac produced no .class files")
    cmd = [
        d8,
        "--min-api", str(min_api),
        "--lib", str(android_jar),
        "--output", str(out_dir),
    ] + [str(c) for c in class_files]
    run(cmd)
    dex = out_dir / "classes.dex"
    if not dex.exists():
        sys.exit("build_android_apk: d8 did not emit classes.dex")
    return dex


def assemble_apk(base_apk: Path, dex: Path, libemacs_so: Path,
                 abi: str, out_apk: Path) -> None:
    # aapt2 link already produced a base apk holding manifest +
    # compiled resources.  Append classes.dex and the native library;
    # python's zipfile preserves the central directory order aapt2
    # set up.
    shutil.copy2(base_apk, out_apk)
    with zipfile.ZipFile(out_apk, "a", zipfile.ZIP_DEFLATED) as zf:
        zf.write(dex, "classes.dex")
        zf.write(libemacs_so, f"lib/{abi}/libemacs.so")


def zipalign(zipalign_bin: Path, in_apk: Path, out_apk: Path) -> None:
    run([str(zipalign_bin), "-p", "-f", "4", str(in_apk), str(out_apk)])


def require_env(name: str) -> str:
    value = os.environ.get(name)
    if value is None:
        sys.exit(f"build_android_apk: {name} must be set for APK signing")
    return value


def apksign(apksigner: Path, keystore: Path, in_apk: Path,
            out_apk: Path) -> None:
    # The APK signing key is part of the app identity on Android.
    # Require callers to supply an explicit keystore and credentials,
    # and pass passwords through apksigner's env: mechanism so they do
    # not appear in process argv or the echoed build command.
    if not keystore.exists():
        sys.exit(f"build_android_apk: signing keystore not found: {keystore}")

    storepass = require_env("EMACS_APK_STOREPASS")
    alias = require_env("EMACS_APK_KEYALIAS")
    keypass = os.environ.get("EMACS_APK_KEYPASS", storepass)

    signer_env = os.environ.copy()
    signer_env["EMACS_APK_STOREPASS"] = storepass
    signer_env["EMACS_APK_KEYPASS"] = keypass
    cmd = [
        str(apksigner), "sign",
        "--ks", str(keystore),
        "--ks-pass", "env:EMACS_APK_STOREPASS",
        "--ks-key-alias", alias,
        "--key-pass", "env:EMACS_APK_KEYPASS",
        "--out", str(out_apk),
        str(in_apk),
    ]
    run(cmd, env=signer_env)


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--source-root", required=True, type=Path)
    p.add_argument("--build-root", required=True, type=Path)
    p.add_argument("--libemacs-so", required=True, type=Path)
    p.add_argument("--assets-stamp", required=True, type=Path)
    p.add_argument("--assets-dir", required=True, type=Path)
    p.add_argument("--ndk", required=True, type=Path)
    p.add_argument("--sdk", required=True, type=Path)
    p.add_argument("--api", required=True, type=int)
    p.add_argument("--abi", required=True)
    p.add_argument("--version", required=True)
    p.add_argument("--keystore", required=True, type=Path)
    p.add_argument("--javac", default="javac")
    p.add_argument("--m4", default="m4")
    p.add_argument("--output", required=True, type=Path)
    args = p.parse_args()

    sdk = args.sdk.resolve()
    bt = find_build_tools(sdk)
    aapt2 = bt / "aapt2"
    d8 = bt / "d8"
    zipalign_bin = bt / "zipalign"
    apksigner = bt / "apksigner"
    for tool in (aapt2, d8, zipalign_bin, apksigner):
        if not tool.exists():
            sys.exit(f"build_android_apk: missing SDK tool {tool}")

    target_api = 35
    android_jar = find_jar(sdk, target_api)

    if not args.assets_stamp.exists():
        sys.exit(
            "build_android_apk: assets staging stamp missing; "
            f"expected {args.assets_stamp}"
        )

    if not args.libemacs_so.exists():
        sys.exit(
            "build_android_apk: native library missing; "
            f"expected {args.libemacs_so}"
        )

    work = args.build_root / "apk-work"
    if work.exists():
        shutil.rmtree(work)
    work.mkdir(parents=True)

    manifest = work / "AndroidManifest.xml"
    m4_manifest(args.m4,
                args.source_root / "java" / "AndroidManifest.xml.in",
                manifest, args.version, args.api, target_api)

    compiled_res = aapt2_compile(aapt2, args.source_root / "java" / "res",
                                 work / "res-compiled")

    gen_java = work / "gen-java"
    base_apk = work / "base.apk"
    aapt2_link(aapt2, compiled_res, manifest, android_jar,
               args.api, target_api, args.version, gen_java,
               base_apk, args.assets_dir)

    classes_dir = work / "classes"
    javac_all(args.javac, args.source_root / "java" / "org",
              gen_java, android_jar, classes_dir)

    dex = d8_dex(str(d8), classes_dir, android_jar, work / "dex",
                 args.api)

    assembled = work / "assembled.apk"
    assemble_apk(base_apk, dex, args.libemacs_so, args.abi, assembled)

    aligned = work / "aligned.apk"
    zipalign(zipalign_bin, assembled, aligned)

    args.output.parent.mkdir(parents=True, exist_ok=True)
    apksign(apksigner, args.keystore, aligned, args.output)

    sys.stderr.write(f"-- APK: {args.output}\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
