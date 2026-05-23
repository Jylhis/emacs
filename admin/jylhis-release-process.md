# Jotain Emacs -- Release Process

This document describes how to cut a release of the Jylhis Emacs fork.
It complements `admin/release-process` (the GNU Emacs upstream process,
which this fork inherits) by describing the fork-local artifacts and
tag scheme.

## Tag scheme

Tags follow `v<emacs-version>-jylhis.<N>` where:

- `<emacs-version>` matches `project()` in `meson.build`
  (currently `31.0.50`).
- `<N>` is a monotonically increasing integer per upstream version.

Example: `v31.0.50-jylhis.1`, `v31.0.50-jylhis.2`, ...

Pre-releases use the suffix `-rcM` (`v31.0.50-jylhis.1-rc1`).

## What ships

`.github/workflows/release.yml` builds, on tag push:

| Artifact                                          | Platform | Variant       |
|---------------------------------------------------|----------|---------------|
| `emacs-VER-linux-x86_64-gtk3.tar.xz`              | Linux    | X11 (GTK 3)   |
| `emacs-VER-linux-x86_64-pgtk.tar.xz`              | Linux    | Wayland (PGTK)|
| `emacs-VER-linux-x86_64-nox.tar.xz`               | Linux    | Terminal-only |
| `emacs-VER-linux-aarch64-gtk3.tar.xz`             | Linux    | X11 (GTK 3)   |
| `emacs-VER-linux-aarch64-pgtk.tar.xz`             | Linux    | Wayland (PGTK)|
| `emacs-VER-linux-aarch64-nox.tar.xz`              | Linux    | Terminal-only |
| `Emacs-VER-universal.dmg`                         | macOS    | NS, universal |
| `nix-outputs-<system>.json` (x4 systems)          | -        | Nix metadata  |
| `ANDROID_STATUS.md`                               | -        | placeholder   |

Each binary artifact has a paired `.sha256` file.

Note: Wayland builds use the `pgtk` toolkit (GTK 3 under the hood --
this fork doesn't have a GTK 4 port yet).  X11 builds use the `gtk3`
toolkit.  Lucid, Athena, and Motif have been dropped.

Android APKs are not built; the Java/NDK glue is not yet ported to
Meson.  See `.claude/notes/build-system.md` "Parked / unsupported".

## Cutting a release

1. **Sync** with upstream and let CI go green on `dev`.

2. **Choose the tag.**  Pick `vX.Y.Z-jylhis.N` per the scheme above.

3. **Optional: write release notes.**  Drop a markdown file at
   `admin/release-notes/<tag>.md` (create the directory if it doesn't
   exist yet -- it is intentionally not tracked when empty).  If
   present, the publish job uses it verbatim as the GitHub Release
   body (prepended to the auto-generated install footer).  If absent,
   the workflow generates a commit-log summary from the previous tag.

4. **Dry-run** (optional but recommended for the first release after
   any workflow change):

   ```sh
   gh workflow run release.yml -f dry_run=true
   ```

   This runs the build matrix and uploads artifacts to the workflow
   run without publishing a release.

5. **Tag and push.**

   ```sh
   git tag -a vX.Y.Z-jylhis.N -m 'Jotain Emacs vX.Y.Z-jylhis.N'
   git push origin vX.Y.Z-jylhis.N
   ```

6. **Watch the workflow.**  The release is created as a **draft** by
   default (per the project policy of draft-first PRs and releases).

7. **Smoke-test the artifacts.**  See "Verification" below.

8. **Promote the draft.**  Edit the draft release in the GitHub UI
   (or via `gh release edit <tag> --draft=false`).

## Verification

Before promoting, smoke-test each artifact class:

```sh
# Linux nox (works under any container)
tar xJf emacs-VER-linux-x86_64-nox.tar.xz
emacs-VER/bin/emacs --batch --eval '(princ emacs-version)'

# macOS universal
xattr -dr com.apple.quarantine Emacs.app   # ad-hoc signed, no Dev ID
file Emacs.app/Contents/MacOS/Emacs        # expect both arches
ls Emacs.app/Contents/Resources/native-lisp # expect 2 subdirs

# Nix
nix run github:Jylhis/emacs/<tag>#emacs-jylhis-pgtk -- \
  --batch --eval '(princ emacs-version)'
```

## Followups (not yet implemented)

- **Apple notarization.**  When a Developer ID becomes available,
  replace `codesign --sign -` with the real identity in
  `release.yml`'s `darwin-universal` job and add a
  `notarytool submit --wait` + `stapler staple` step.

- **Android APK.**  Replace the `android-stub` job with a real
  cross-compile once the Java/NDK glue is restored under Meson.

- **GTK 4.**  Drop GTK 3 from the `pgtk` variant when upstream lands
  a GTK 4 port.
