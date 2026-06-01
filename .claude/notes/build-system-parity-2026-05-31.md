# Meson vs. upstream autotools — feature parity audit (2026-05-31)

This note audits the post-phase-10 Meson build (commit `313f867` removed
`configure.ac`, `autogen.sh`, `m4/`, every `Makefile.in`, `GNUmakefile`,
and `make-dist`) against the upstream `configure.ac` (~7958 lines) on
`emacs-upstream/master`.  Goal: identify every upstream knob, probe,
library detection, install rule, NS bundle artefact, and lib-src binary
that has no equivalent in the local Meson tree, then bucket the gaps by
impact on the NS-focused fork.

Sources read:

- `git show emacs-upstream/master:configure.ac` (captured to
  `/tmp/upstream-configure.ac`).
- `git show emacs-upstream/master:nextstep/Makefile.in` (110 lines).
- `git show emacs-upstream/master:lib-src/Makefile.in` INSTALLABLES /
  UTILITIES / DONT_INSTALL tables.
- `git ls-tree emacs-upstream/master nextstep/Cocoa/Emacs.base/...`
  + `nextstep/GNUstep/`.
- Local: `meson.build` (1287 lines), `meson.options` (275 lines),
  every subdir's `meson.build`, `meson/config.h.in`, `meson/meson_install.py`,
  `meson/run_app_bundle.py`.
- Baseline: `.claude/notes/build-system.md` (the only prior parity note
  reachable from this user; `/root/.claude/plans/...` is not readable).

## 1. Upstream `configure.ac` option inventory

`AC_ARG_WITH` / `AC_ARG_ENABLE` declarations (35 distinct CLI knobs,
counting the `OPTION_DEFAULT_*` macros that expand to `AC_ARG_WITH`):

| Upstream switch | Default | Where |
|---|---|---|
| `--with-all` | yes | configure.ac:295 |
| `--with-mailutils` | auto/yes | :358 |
| `--with-pop` | yes | :372 |
| `--with-mailhost=HOST` | "" | :419 |
| `--with-sound=VALUE` | auto | :424 |
| `--with-pdumper` | yes | :437 |
| `--with-dumping=VALUE` | pdumper | :452 |
| `--with-systemduserunitdir` | pkg-config | :496 |
| `--with-x-toolkit=KIT` | gtk3 | :511 |
| `--with-wide-int` | off | :537 |
| `--with-xpm/jpeg/tiff/gif/png/rsvg/webp` | on | :544-550 |
| `--with-sqlite3/lcms2/libsystemd` | on | :551-553 |
| `--with-cairo` | on | :554 |
| `--with-cairo-xcb` | off | :555 |
| `--with-xml2` | on | :556 |
| `--with-imagemagick` | off | :557 |
| `--with-native-image-api` | on | :558 |
| `--with-tree-sitter` | if-available | :559 |
| `--with-xft/harfbuzz/libotf/m17n-flt` | on | :561-564 |
| `--with-toolkit-scroll-bars/xaw3d/xim/xdbe` | on | :566-569 |
| `--with-ns` | maybe | :570 |
| `--with-w32` | off | :573 |
| `--with-pgtk` | off | :574 |
| `--with-gpm` | on | :576 |
| `--with-dbus` | if-available | :577 |
| `--with-gconf` | maybe | :578 |
| `--with-gsettings` | on | :586 |
| `--with-selinux` | maybe | :588 |
| `--with-gnutls/zlib/modules/threads` | on | :593-596 |
| `--with-cygwin32-native-compilation` | off | :597 |
| `--with-xinput2` | on | :598 |
| `--with-small-ja-dic` | off | :599 |
| `--with-android/android-debug` | off/on | :600-601 |
| `--with-shared-user-id` | (Android) | :622 |
| `--with-file-notification=LIB` | auto | :626 |
| `--with-gameuser=USER\|:GROUP` | "" | :663 |
| `--with-gnustep-conf` | "" | :676 |
| `--with-xwidgets` | off | :645 |
| `--with-compress-install` | on | :659 |
| `--with-native-compilation` | no | :1739 |
| `--enable-ns-self-contained` | yes | :686 |
| `--enable-locallisppath` | "" | :693 |
| `--enable-checking` | "" | :703 |
| `--enable-gc-mark-trace` | off | :787 |
| `--enable-profiling` | off | :802 |
| `--enable-autodepend` | yes | :815 |
| `--enable-gtk-deprecation-warnings` | off | :821 |
| `--enable-build-details` | yes | :827 |
| `--enable-gcc-warnings` | no | :1712 |
| `--enable-check-lisp-object-type` | off | :1761 |
| `--enable-link-time-optimization` | off | :1937 |
| `--enable-silent-rules` | yes | :1999 |

Plus the always-present autotools cruft (`--with-mailhost`, `AC_ARG_VAR`
ANDROID_CC/JAVAC/JARSIGNER/APKSIGNER/SDK_BUILD_TOOLS/ZIP, `--program-prefix`,
`--program-suffix`, `--program-transform-name`, `--prefix`, `--bindir`,
…).

## 2. Local Meson option inventory

`meson.options` declares 49 options; categorised in the file header.
Quick name list (see file for descriptions/defaults):

`all-features`, `mailutils`, `pop`, `mailhost`, `kerberos`, `kerberos5`,
`hesiod`, `mail-unlink`, `sound`, `pdumper`, `dumping`, `toolkit`,
`ns`, `pgtk`, `xpm`, `jpeg`, `tiff`, `gif`, `png`, `rsvg`, `webp`,
`imagemagick`, `cairo`, `cairo-xcb`, `xft`, `harfbuzz`, `libotf`,
`m17n-flt`, `toolkit-scroll-bars`, `xim`, `xdbe`, `xinput2`, `xaw3d`,
`sqlite3`, `lcms2`, `libsystemd`, `xml2`, `tree-sitter`, `gpm`, `dbus`,
`gsettings`, `selinux`, `gnutls`, `zlib`, `modules`, `threads`,
`file-notification`, `gameuser`, `gnustep-conf`, `shared-user-id`,
`systemduserunitdir`, `ns-self-contained`, `locallisppath`, `checking`,
`check-lisp-object-type`, `gc-mark-trace`, `profiling`, `autodepend`,
`gtk-deprecation-warnings`, `build-details`, `wide-int`, `xwidgets`,
`compress-install`, `native-compilation`, `gcc-warnings`, `lto`,
`silent-rules`, `android` + 5 android-* knobs, `small-ja-dic`.

The README inside `meson.options` notes that Android `shared-user-id`
is intentionally inert because the Android port is parked.

## 3. Parity table — switches

Status legend:  `parity` = same surface + same behaviour;  `partial` =
flag exists but coverage is reduced;  `missing` = no equivalent;
`n/a-removed-area` = parked/dropped on this fork by design.

| Upstream | Meson | Status | Note |
|---|---|---|---|
| `--with-all` / `--without-all` | `-Dall-features=` | parity | wired via `_no_all = not all_features` in `meson.build`. |
| `--with-mailutils` | `-Dmailutils=` | parity | gates movemail install via `mailutils_install_movemail`. |
| `--with-pop` | `-Dpop=` | parity | sets `MAIL_USE_POP`. |
| `--with-mailhost=` | `-Dmailhost=` | parity | sets `MAILHOST` quoted. |
| `--with-sound=VAL` | `-Dsound=` | parity | combo accepts auto/yes/no/alsa/oss/bsd-ossaudio (oss support not actually wired). |
| `--with-pdumper` | `-Dpdumper=` | partial | option declared but `meson/config.h.in` hard-codes `HAVE_PDUMPER 1` / `DUMPING_PDUMPER 1`; `-Dpdumper=disabled` has no effect (the autotools dumping logic supported `--with-dumping=unexec` historically — already dropped here). |
| `--with-dumping=VALUE` | `-Ddumping=` | parity | only `pdumper` and `none` choices; `unexec` deliberately gone (matches upstream's actual valid choices after `unexec` removal). |
| `--with-systemduserunitdir` | `-Dsystemduserunitdir=` | parity | string opt; install gated. |
| `--with-x-toolkit=` | `-Dtoolkit=` | partial | only `gtk3`/`pgtk`/`none`/`auto`; upstream still recognises lucid/athena/motif/gtk2 — parked by design (`meson.options:52-53`). |
| `--with-wide-int` | `-Dwide-int=` | parity | sets `WIDE_EMACS_INT`. |
| `--with-xpm/jpeg/tiff/gif/png/rsvg/webp` | `-D…=` | parity | each probed in `meson.build`. |
| `--with-sqlite3` | `-Dsqlite3=` | partial | `HAVE_SQLITE3` set; **`HAVE_SQLITE3_LOAD_EXTENSION`** probe (configure.ac:3651) missing — `src/sqlite.c` gates `sqlite-load-extension` Lisp function on it. |
| `--with-lcms2` | `-Dlcms2=` | parity | pkg-config probe. |
| `--with-libsystemd` | `-Dlibsystemd=` | parity. |
| `--with-cairo` | `-Dcairo=` | parity | also pulls `cairo-ft`. |
| `--with-cairo-xcb` | `-Dcairo-xcb=` | missing | option declared (`disabled` default) but no `USE_CAIRO_XCB` probe / `cdata.set` — flipping `-Dcairo-xcb=enabled` is silently a no-op.  N/a for NS. |
| `--with-xml2` | `-Dxml2=` | parity. |
| `--with-imagemagick` | `-Dimagemagick=` | parity | sets `HAVE_IMAGEMAGICK`; upstream's `HAVE_IMAGEMAGICK7` distinction not surfaced (modern Wand only). |
| `--with-native-image-api` | — | missing | upstream defaults ON, used by NS/Haiku/w32 to enable `HAVE_NATIVE_IMAGE_API`.  For the NS port this gates image.c CoreGraphics fast-paths — see §8.  Cosmetic on Linux. |
| `--with-tree-sitter` | `-Dtree-sitter=` | parity | OPTION_DEFAULT_IFAVAILABLE captured. |
| `--with-xft` | `-Dxft=` | parity. |
| `--with-harfbuzz` | `-Dharfbuzz=` | parity. |
| `--with-libotf` | `-Dlibotf=` | parity. |
| `--with-m17n-flt` | `-Dm17n-flt=` | parity. |
| `--with-toolkit-scroll-bars` | `-Dtoolkit-scroll-bars=` | parity. |
| `--with-xaw3d` | `-Dxaw3d=` | n/a-removed-area | `disabled` default; legacy X toolkit dropped. |
| `--with-xim` | `-Dxim=` | parity. |
| `--with-xdbe` | `-Dxdbe=` | parity. |
| `--with-ns` | `-Dns=` | parity. |
| `--with-w32` | — | n/a-removed-area | MS Windows GUI parked. |
| `--with-pgtk` | `-Dpgtk=` | partial | option declared, but no `HAVE_PGTK` probe in `meson.build`; `_toolkit=='pgtk'` short-circuits the X11 probe but never sets `HAVE_PGTK`.  Flipping the option does not produce a pgtk build (PgTk would also need its own `pgtkterm.c`/`pgtkfns.c` source wiring). |
| `--with-gpm` | `-Dgpm=` | parity. |
| `--with-dbus` | `-Ddbus=` | parity. |
| `--with-gconf` | — | n/a-removed-area | deprecated; intentionally absent. |
| `--with-gsettings` | `-Dgsettings=` | parity. |
| `--with-selinux` | `-Dselinux=` | parity. |
| `--with-gnutls` | `-Dgnutls=` | parity. |
| `--with-zlib` | `-Dzlib=` | parity. |
| `--with-modules` | `-Dmodules=` | parity. |
| `--with-threads` | `-Dthreads=` | parity | upstream's `THREADS_ENABLED` define not set — Meson uses `HAVE_THREADS`; both are tested by some lisp/ in upstream so cross-check `src/thread.c`. |
| `--with-cygwin32-native-compilation` | — | n/a-removed-area | Cygwin parked. |
| `--with-xinput2` | `-Dxinput2=` | parity. |
| `--with-small-ja-dic` | `-Dsmall-ja-dic=` | partial | option declared but no consumer found in `leim/meson.build` or `admin/meson.build`; toggling does not change the generated `lisp/leim/quail/japanese.el`. |
| `--with-android` | `-Dandroid=` + 5 android-* knobs | partial | APK pipeline plumbed; the JNI/Java glue, asset-directory-tool, NDK build infrastructure are parked per `.claude/notes/build-system.md`. |
| `--with-shared-user-id` | `-Dshared-user-id=` | n/a-removed-area | Android-only, parked. |
| `--with-file-notification` | `-Dfile-notification=` | parity. |
| `--with-gameuser=` | `-Dgameuser=` | parity | install gating + sgid bit handled by `meson_install.py`. |
| `--with-gnustep-conf` | `-Dgnustep-conf=` | n/a-removed-area | GNUstep not built on this fork (`nextstep/meson.build` only wires Cocoa); option is inert but harmless. |
| `--with-xwidgets` | `-Dxwidgets=` | parity (GTK)  /  partial (NS) | `webkit2gtk-4.1` probe + `HAVE_XWIDGETS` define wired for GTK; the NS branch `src/meson.build:333-336` adds `appleframeworks/WebKit` but never sets `HAVE_XWIDGETS` on Cocoa because the option's `allowed()` block requires `gtk3_dep.found()`.  See §8. |
| `--with-compress-install` | `-Dcompress-install=` | parity | implemented in `meson_install.py`. |
| `--with-native-compilation` | `-Dnative-compilation=` | parity | yes/no/aot. |
| `--enable-ns-self-contained` | `-Dns-self-contained=` | partial | bundle copying is implemented (`run_app_bundle.py --self-contained`), but `NS_SELF_CONTAINED` macro **is not set in `conf_data`**; `src/emacs.c`'s `init_callproc_1` and `init_lread` branches on it to look up resources relative to the bundle.  Bundle paths therefore work only by virtue of `Contents/MacOS/libexec/Emacs.pdmp` being adjacent to the binary, not by source-tree gating.  See §8. |
| `--enable-locallisppath` | `-Dlocallisppath=` | parity. |
| `--enable-checking` | `-Dchecking=` | partial | array option declared, but `meson.build` never inspects it — none of `ENABLE_CHECKING`, `CHECK_STRUCTS`, `GC_CHECK_STRING_BYTES`, `GC_CHECK_STRING_OVERRUN`, `GC_CHECK_STRING_FREE_LIST`, `GLYPH_DEBUG`, `XASSERTS` are set.  `-Dchecking=yes,glyphs` recommended by `CLAUDE.md` is currently a no-op. |
| `--enable-gc-mark-trace` | `-Dgc-mark-trace=` | parity | sets `GC_REMEMBER_LAST_MARKED`. |
| `--enable-profiling` | `-Dprofiling=` | parity | adds `-pg` + `PROFILING=1`. |
| `--enable-autodepend` | — | missing-cosmetic | autotools dep file generation; ninja does this natively, no port needed. |
| `--enable-gtk-deprecation-warnings` | `-Dgtk-deprecation-warnings=` | parity. |
| `--enable-build-details` | `-Dbuild-details=` | parity. |
| `--enable-gcc-warnings` | `-Dgcc-warnings=` | partial | combo declared (no/yes/warn-only) but `meson.build` never reads it — no `GCC_LINT` define, no `-Werror` knob.  `CLAUDE.md` developer flag is silently a no-op. |
| `--enable-check-lisp-object-type` | `-Dcheck-lisp-object-type=` | partial | option declared, but no `cdata.set('CHECK_LISP_OBJECT_TYPE', 1)` — the flag is not propagated to `src/config.h`. |
| `--enable-link-time-optimization` | `-Dlto=` | partial | option declared, but no consumer in `meson.build`; should map to `b_lto=true`. |
| `--enable-silent-rules` | `-Dsilent-rules=` | n/a-cosmetic | Ninja default. |

## 4. `HAVE_*` macro probes — coverage gap

`AC_DEFINE([HAVE_X], …)` appears 270 times upstream (many platform-conditional
PTY/POSIX bits).  The Meson `conf_data` table sets a large fraction of
the user-facing ones; below is the diff between upstream `HAVE_*` and
what `meson.build`/`config.h.in` actually emits.

**Emitted by both (no change needed):** `HAVE_GTK3, USE_GTK, HAVE_GTK,
HAVE_X_WINDOWS, HAVE_X11, HAVE_WINDOW_SYSTEM, HAVE_TEXT_CONVERSION,
HAVE_PTYS, HAVE_PTHREAD, HAVE_INOTIFY/KQUEUE/GFILENOTIFY, USE_FILE_NOTIFY,
HAVE_CAIRO, USE_CAIRO, HAVE_HARFBUZZ, HAVE_FREETYPE, HAVE_FONTCONFIG,
HAVE_XFT, HAVE_GNUTLS, HAVE_TREE_SITTER, HAVE_SQLITE3, HAVE_LIBXML2,
HAVE_LIBSYSTEMD, HAVE_GMP, HAVE_NATIVE_COMP, HAVE_XWIDGETS,
USE_GTK_FOR_XWIDGETS, HAVE_NS, NS_IMPL_COCOA, HAVE_XPM, HAVE_JPEG,
HAVE_TIFF, HAVE_PNG, HAVE_GIF, HAVE_RSVG, HAVE_WEBP, HAVE_IMAGEMAGICK,
HAVE_LCMS2, HAVE_DBUS, HAVE_GPM, HAVE_GSETTINGS, HAVE_LIBSELINUX,
HAVE_ZLIB, HAVE_LIBOTF, HAVE_M17N_FLT, HAVE_SOUND, HAVE_ALSA, USE_ALSA,
HAVE_MODULES, HAVE_THREADS, HAVE_XINPUT2, HAVE_XDBE, HAVE_XIM, USE_XIM,
HAVE_MAILUTILS, MAIL_USE_POP, KERBEROS, KERBEROS5, HESIOD,
MAIL_UNLINK_SPOOL, MAILHOST, USE_TOOLKIT_SCROLL_BARS, GC_REMEMBER_LAST_MARKED,
HAVE_PDUMPER, DUMPING_PDUMPER, HAVE_PROCFS (via OS gates), HAVE_X11R6,
HAVE_X_I18N, HAVE_X11R6_XIM, HAVE_XRMSETDATABASE, HAVE_XKB, HAVE_XRENDER,
HAVE_XCOMPOSITE, HAVE_XSHAPE, HAVE_XKBGETKEYBOARD, HAVE_XINERAMA,
HAVE_XRANDR, HAVE_XFIXES, HAVE_XSYNC, HAVE_XSCREENNUMBEROFSCREEN,
HAVE_XSCREENRESOURCESTRING, HAVE_PERSONALITY_ADDR_NO_RANDOMIZE
(no, actually missing — see below),  USABLE_FIONREAD, USABLE_SIGIO,
INTERRUPT_INPUT, DARWIN_OS, GNU_LINUX, USG, SIGNALS_VIA_CHARACTERS,
TAB3 (=OXTABS), DONT_REOPEN_PTY, HAVE__SETJMP, GC_SETJMP_WORKS,
UNIX98_PTYS, PTY_ITERATION/OPEN/NAME_SPRINTF/TTY_NAME_SPRINTF,
HAVE_ANDROID, HAVE_GLIB, COPYRIGHT, SEPCHAR, SYSTEM_TYPE,
EMACS_CONFIGURATION/CONFIG_OPTIONS/CONFIG_FEATURES,
DYNAMIC_LIB_SUFFIX[_SECONDARY], MODULES_SUFFIX[_SECONDARY],
NATIVE_ELISP_SUFFIX, BINDIR.`

**Upstream defines, Meson does not:**

| Upstream `HAVE_*` / macro | Set in src/conf_post.h via probe? | Impact |
|---|---|---|
| `HAVE_PERSONALITY_ADDR_NO_RANDOMIZE` (`configure.ac:2495`) | no | unexec hook; the Meson build is pdumper-only so irrelevant. |
| `HAVE_LINUX_SYSINFO` / `LINUX_SYSINFO_UNIT` (`:2511-2515`) | no | `src/sysdep.c` reports memory totals; falls back to `/proc/meminfo` on Linux but loses `getsysinfo()` fast path. |
| `HAVE_PNG` newer-than-1.6 — header path differences | n/a | only one branch; meson uses `libpng` pkg-config; OK. |
| `HAVE_SQLITE3_LOAD_EXTENSION` (`:3651`) | **no** | `src/sqlite.c` gates the `sqlite-load-extension` Lisp primitive on this; without it the function signals "unsupported". |
| `HAVE_IMAGEMAGICK7` (`:3679`) | **no** | `src/image.c` uses different `MagickWand` API in the 7.x branch. |
| `HAVE_GETADDRINFO_A` (`:3728`) | **no** | `src/process.c` asynchronous DNS lookup; falls back to blocking `getaddrinfo`. |
| `HAVE_GCONF` (`:3956`) | n/a-removed-area | deprecated. |
| `HAVE_DATA_START` (`:3329`) | **no** | gnulib dummy; only matters for unexec. |
| `HAVE_GETRANDOM/GETENTROPY` | yes (via cc.has_function) | parity. |
| `HAVE_TIMERFD` (`:6209`) | **no** | `src/atimer.c` uses `timerfd_create` on Linux for higher-precision atimers when set; falls back to `setitimer`. |
| `HAVE_LIBXML2` >= 2.6.17 minimum version | yes but no version check | upstream enforces version; Meson `dependency('libxml-2.0')` accepts any. |
| `HAVE_LIBMAIL` / `HAVE_LIBLOCKFILE` (`:5835/5847`) | **no** | `lib-src/movemail.c` uses `maillock(3)` from `-lmail` or `-llockfile` when present; otherwise falls back to its own dotlock.  Missing on Meson side — only matters for shared mail spool builds. |
| `HAVE_CFMAKERAW/CFSETSPEED` (`:5966/5981`) | yes (cc.has_function) | parity. |
| `HAVE___BUILTIN_FRAME_ADDRESS/UNWIND_INIT` (`:6033/6042`) | **no** | `src/alloc.c`'s GC mark-stack probe; falls back to setjmp-only register flushing — fine on x86_64 but suboptimal on aarch64. |
| `TERMINFO` (`:6176`) — already hard-coded to 1 in `config.h.in` | parity. |
| `TERMINFO_DEFINES_BC` (`:6188`) | **no** | `src/term.c` `extern char *BC, *UP` declarations when terminfo doesn't provide them. |
| `USE_NCURSES` (`:6193`) | **no** | `src/term.c` includes `<ncurses.h>` vs `<curses.h>`. |
| `HAVE_PROCFS` (`:6597`) | **no** | `src/sysdep.c`'s `system-process-attributes`. Linux fallback works without it but slower. |
| `BROKEN_GET_CURRENT_DIR_NAME` (`:6571`) | **no** | gnulib workaround. |
| `BROKEN_PTY_READ_AFTER_EAGAIN` (`:6589`) | **no** | FreeBSD-only. |
| `HAVE_STATEMENT_EXPRESSIONS` (`:7304`) | **no** | gnulib hardens against compilers that lack `({...})`; GCC/Clang always have it. |
| `HAVE_X_SM` (`:5578`) | **no** | X session-manager save-yourself protocol; `src/xsmfns.c` no-ops without it. |
| `HAVE_XCB_SHAPE` (`:5743`) | **no** | bare-XCB cursor reshaping when XShape unavailable.  Linux-only. |
| `USE_XCB` (`:4782`) | **no** | gates `xterm.c` using XCB-direct calls for low-latency input. |
| `HAVE_STRUCT_ATTRIBUTE_ALIGNED` (`:3254`) | **no** | gnulib + lib/_Noreturn; modern compilers always have it. |
| `HAVE_TINY_SPEED_T` (`:7019`) | **no** | termios speed_t width — only matters on legacy *BSD. |
| `HAVE_STACK_OVERFLOW_HANDLING` (`:6922`) | **no** | `src/sysdep.c` SIGSEGV alt-stack handler; falls back to ordinary crash.  Set when `sigaltstack(2)` + `MINSIGSTKSZ` work — both fine on Darwin and Linux. |
| `HAVE_TEXT_CONVERSION` | yes (forced for NS) | parity. |
| `_REGEX_AVOID_UCHAR_H` (`:1620`) | yes via `config.h.in` mesondefine? | **no** — not set; benign. |
| `BROKEN_*`, `RUN_TIME_REMAP`, `XOS_NEEDS_TIME_H`, `TIOCSIGSEND`, `NSIG_MINIMUM`, `USG_SUBTTY_WORKS`, `_STRUCTURED_PROC`, `USABLE_SIGPOLL`, `HAVE_TIOCNOTTY` | n/a | exotic platforms (HP-UX, Solaris, AIX, Cygwin); won't affect Darwin/Linux. |
| `NS_SELF_CONTAINED` (`:2886`) | **no** | see §8. |
| `_NATIVE_OBJC_EXCEPTIONS` (`:2804`) | n/a-removed-area | GNUstep-only. |
| `NATIVE_OBJC_INSTANCETYPE` (`:2927`) | **no** | minor — old GNUstep workaround; on Cocoa already available. |
| `HAVE_NATIVE_IMAGE_API` (`:2861/3055/3119`) | **no** | NS: enables CoreGraphics-backed image scaling in `src/image.c`. |
| `HAVE_HAIKU`, `HAVE_NTGUI`, `HAVE_BE_APP`, `HAVE_PGTK`, `USE_BE_CAIRO` | n/a-removed-area | parked. |
| `THREADS_ENABLED` (`:3442`) | **no** | upstream uses both `HAVE_THREADS` (config) and `THREADS_ENABLED` (Lisp `featurep 'threads`).  Meson sets the former only.  Most call sites still work because lisp/thread.el also checks `(fboundp 'make-thread)`. |
| `_REENTRANT`, `_THREAD_SAFE` (`:3428-3431`) | **no** | per-OS pthread flags; meson assumes `-pthread` does it. |
| `EMACS_INT_SIZE` / `EMACS_INT_MAX` | parity (`SIZEOF_EMACS_INT`, `ALIGNOF_EMACS_INT`). |
| `HAVE_DECL_<unlocked stdio>` | parity. |
| Hard-coded `SYSTEM_MALLOC=1` in `config.h.in` | upstream conditional on host (`AC_DEFINE` at `:3309`) | OK, all current targets use system malloc. |
| `DOUG_LEA_MALLOC` (`:3342`) | **no** | dropped on this fork (we use system malloc); OK. |
| `USE_MMAP_FOR_BUFFERS` (`:3366`) | **no** | not portable; current Emacs default is no anyway. |
| `REL_ALLOC`, `GNU_MALLOC` (`:7309/7315`) | **no** | tied to gmalloc which we don't ship — OK. |
| `BINDIR` macro | upstream sets via `AC_DEFINE_UNQUOTED` (`:7172`); meson does not — `lib-src/emacsclient.c` uses it to spawn the right `emacs` binary.  **Currently missing.** | NS-affecting if emacsclient is part of the bundle. |

## 5. Library detection coverage

`AC_CHECK_LIB` / `PKG_CHECK_MODULES` / `EMACS_CHECK_MODULES` / `AC_SEARCH_LIBS`
sites and their Meson equivalents:

| Upstream call | What it checks | Meson equivalent | Status |
|---|---|---|---|
| `EMACS_CHECK_MODULES([ALSA])` | alsa | `dependency('alsa')` | parity |
| `EMACS_CHECK_MODULES([GTK])` | gtk+-3.0 | `dependency('gtk+-3.0')` | parity |
| `EMACS_CHECK_MODULES([DBUS])` | dbus-1>=1.0 | `dependency('dbus-1')` | parity (version not pinned) |
| `EMACS_CHECK_MODULES([GSETTINGS])` | gio-2.0>=2.26 | `dependency('gio-2.0')` | parity (version not pinned) |
| `EMACS_CHECK_MODULES([GCONF])` | gconf-2.0 | — | n/a-removed-area |
| `EMACS_CHECK_MODULES([GOBJECT])` | gobject-2.0>=2.0 | — | missing (probably comes via gtk3_dep transitively, but `dbusbind.c` references gobject types when HAVE_DBUS). |
| `EMACS_CHECK_MODULES([LIBGNUTLS])` | gnutls>=2.12.2 | `dependency('gnutls')` | parity (no version pin) |
| `EMACS_CHECK_MODULES([LIBSYSTEMD])` | libsystemd>=222 | `dependency('libsystemd')` | parity (no version pin) |
| `EMACS_CHECK_MODULES([TREE_SITTER])` | tree-sitter>=0.20.2 | `dependency('tree-sitter')` | parity (no version pin) |
| `EMACS_CHECK_MODULES([KQUEUE])` | libkqueue (Linux fallback) | — | missing-cosmetic; only matters when Meson is asked for `-Dfile-notification=kqueue` on Linux. |
| `EMACS_CHECK_MODULES([GFILENOTIFY])` | gio-2.0>=2.24 | `dependency('gio-2.0')` | parity |
| `EMACS_CHECK_MODULES([CAIRO])` | cairo | `dependency('cairo')` + `dependency('cairo-ft')` | parity |
| `EMACS_CHECK_MODULES([CAIRO_XCB])` | cairo-xcb | — | missing (cairo-xcb option is inert anyway). |
| `EMACS_CHECK_MODULES([CAIRO_XLIB])` | cairo-xlib (xwidgets path) | — | missing — `src/xwidget.c` references it indirectly. |
| `EMACS_CHECK_MODULES([WEBKIT])` | webkit2gtk-4.1 | `dependency('webkit2gtk-4.1')` | parity (GTK only — NS path uses appleframeworks/WebKit) |
| `EMACS_CHECK_MODULES([FREETYPE/FONTCONFIG])` | freetype2 / fontconfig>=2.2.0 | parity |
| `EMACS_CHECK_MODULES([LIBOTF])` | libotf | parity |
| `EMACS_CHECK_MODULES([M17N_FLT])` | m17n-flt | parity |
| `EMACS_CHECK_MODULES([HARFBUZZ])` | harfbuzz | parity (no version pin) |
| `EMACS_CHECK_MODULES([XRANDR/XINERAMA/XFIXES/XINPUT])` | x* extensions | `cc.find_library('Xrandr')` etc. in `src/meson.build:extra_x_libs` | parity (uses find_library, not pkg-config) |
| `EMACS_CHECK_MODULES([LIBXML2])` | libxml-2.0>2.6.17 | `dependency('libxml-2.0')` | parity (no version pin) |
| `EMACS_CHECK_MODULES([LIBSECCOMP])` | libseccomp>=2.5.2 | `dependency('libseccomp')` in `lib-src/meson.build` | parity (no version pin) |
| `EMACS_CHECK_MODULES([PNG])` | libpng>=1.0.0 | `dependency('libpng')` | parity |
| `EMACS_CHECK_MODULES([LCMS2])` | lcms2 | parity |
| `EMACS_CHECK_MODULES([XFT])` | xft>=0.13.0 | `dependency('xft')` | parity |
| `EMACS_CHECK_MODULES([WEBP])` | libwebp + libwebpdemux>=0.6.0 | grouped via `declare_dependency` | parity (with explicit version 0.6.0) |
| `EMACS_CHECK_MODULES([RSVG])` | librsvg-2.0>=2.14.0 | `dependency('librsvg-2.0', version : '>= 2.40.4')` | parity (stricter version pin on Meson side) |
| `EMACS_CHECK_MODULES([IMAGEMAGICK])` | MagickWand>=7 or Wand>=6.3.5 | `dependency('MagickWand')` | partial — no version pin, no v6/v7 split. |
| `AC_CHECK_LIB([sqlite3], [sqlite3_load_extension])` | feature probe | — | **missing** — see §4. |
| `AC_CHECK_LIB([anl], [getaddrinfo_a])` | async DNS | — | **missing**. |
| `AC_CHECK_LIB([gccjit], [gcc_jit_context_acquire])` | native comp | `cc.find_library('gccjit')` (with manual header probe loop) | parity |
| `AC_CHECK_LIB([jpeg/tiff/gif/png], …)` | bare-library fallback for image libs | `cc.find_library('jpeg'/'tiff'/'gif')` fallback after pkg-config | parity |
| `AC_CHECK_LIB([gpm], [Gpm_Open])` | console mouse | `cc.find_library('gpm')` | parity |
| `AC_CHECK_LIB([SM], [SmcOpenConnection])` | X SM (with `-lICE` link) | `cc.find_library('SM') / 'ICE'` in `extra_x_libs` | parity |
| `AC_CHECK_LIB([Xrandr/Xinerama/Xfixes/Xi/Xext/Xcomposite])` | X extensions | `extra_x_libs` list | parity |
| `AC_CHECK_LIB([Xrender], [XRenderQueryExtension])` | XRender | parity |
| `AC_CHECK_LIB([mail], [maillock])` | shared mail spool | — | **missing** — see §4 (`HAVE_LIBMAIL`/`HAVE_LIBLOCKFILE`). |
| `AC_CHECK_LIB([resolv/com_err/crypto/k5crypto/krb*/des*])` | kerberos & resolv chain | `movemail_extra_libs` list in `meson.build:852-905` | parity |
| `AC_CHECK_LIB([Xbsd])` | legacy BSD compatibility | — | n/a-removed-area |
| `AC_CHECK_LIB([Xaw3d], …)` | legacy toolkit | — | n/a-removed-area |
| `AC_CHECK_LIB([Xp], …)` | legacy X print | — | n/a-removed-area |
| `AC_SEARCH_LIBS([XmuConvertStandardSelection], [Xmu])` | X11 motif fallback | — | n/a-removed-area |
| `AC_SEARCH_LIBS([kqueue])` | bare kqueue probe | implicitly via libc on Darwin | parity |
| `cc.find_library('gmp')` then `pkg-config('gmp')` fallback in meson | parity |
| `cc.find_library('libgcrypt')` (probed as `dependency('libgcrypt')`) | parity (used for `Fmd5`/`Fsecure-hash`; **not** present upstream — fork only). |
| `cc.find_library('tinfo')` then `ncurses` | parity (upstream picks via configure) |

## 6. Install rules — coverage

Upstream's authoritative install graph lives in the deleted `Makefile.in`
plus `lisp/Makefile.in`, `etc/Makefile.in`, `doc/*/Makefile.in`,
`lib-src/Makefile.in`, `nextstep/Makefile.in`.  Meson's coverage:

- `share/emacs/$VER/lisp/` — covered by `meson_install.py:copytree`,
  including `*.elc` from the build root and `update-subdirs`-generated
  `subdirs.el`.
- `share/emacs/$VER/etc/` — covered, with the same `DOC`/`.gitignore`/
  `ChangeLog` strip set as autotools.
- `share/emacs/$VER/native-lisp/` — covered (when `libgccjit_dep.found()`).
- `libexec/emacs/$VER/$CONFIG/etc/DOC` — covered.
- `libexec/emacs/$VER/$CONFIG/emacs.pdmp` — covered (prefers
  `lisp/emacs.pdmp` over `src/emacs.pdmp`).
- `bin/emacs` symlink → `emacs-$VER` — covered.
- `bin/{etags,ctags,emacsclient,ebrowse}` — covered by `lib-src/meson.build`.
- `libexec/.../{hexl,movemail,update-game-score}` — covered (movemail
  gated on `--without-mailutils`).
- `bin/rcs2log` — installed as a shell script — covered.
- `seccomp-filter` + `*.bpf` / `*.pfc` — covered (Linux x86_64 only).
- `info/*.info` — covered (each Texinfo manual marks `install: true`).
- `info/dir` — covered via `install-info` invocation in `meson_install.py`.
- Manpages: `emacs.1`, `etags.1`, `emacsclient.1`, `ebrowse.1` — covered.
- `share/applications/*.desktop` (4 entries) — covered.
- `share/metainfo/emacs.metainfo.xml` — covered.
- `share/icons/hicolor/.../emacs*.{png,svg}` — covered via
  `meson/list_icons.py` enumeration.
- `share/glib-2.0/schemas/org.gnu.emacs.defaults.gschema.xml`
  + `glib-compile-schemas` cache rebuild — covered when `HAVE_GSETTINGS`.
- `lib/systemd/user/emacs.service` — covered when `--systemduserunitdir`
  is set.
- `--with-compress-install` gzip pass over installed `*.el`, `*.info`,
  `*.1`, `etc/publicsuffix.txt` — covered.

**Install gaps:**

- `etc/charsets/` — upstream's `admin/charsets/Makefile.in` produces
  `etc/charsets/<charset>.map`; the Meson tree generates them at build
  time (`charsets_stamp`) but `meson_install.py` walks `source_root/etc`
  not `build_root/etc`, so the regenerated maps in `build/etc/charsets/`
  are **not installed**.  Practical fallout: the source-tree maps are
  identical to the regenerated ones (committed), so installs still work
  — but `make-charset-table` changes would not flow through.
- `lisp/leim/quail/*.el` regenerated outputs — `leim/meson.build` writes
  them into the source tree, so they install via the `lisp/` copytree.
- `etc/emacs-buffer.gdb`, `etc/refcards/*.tex` (compiled pdfs) — refcard
  PDFs aren't built by Meson at all (parity: autotools requires
  `--with-refcards`, also not built by default).
- `share/man/man1/ctags.1`, `share/man/man1/hexl.1` — upstream's
  `doc/man/Makefile.in` excludes these; meson matches.
- `share/info/dir` index — handled, but only after `install-info`
  resolves; warnings are common — parity.
- `share/applications/*.desktop` — upstream sed-rewrites `Exec=` /
  `Icon=` lines per `program-transform-name`; Meson installs them
  verbatim.  Cosmetic until `--program-suffix` lands.
- Per-package theme files under `etc/themes/` — covered (via etc/
  walk).
- `etc/tutorials/TUTORIAL.*` translations — covered.
- `share/emacs/site-lisp/` and `share/emacs/$VER/site-lisp/` empty
  trees with `subdirs.el` — covered by `write_subdirs_el`.

## 7. Build artefacts — lib-src binaries

Upstream `lib-src/Makefile.in` (the file is still present upstream,
since they haven't migrated):

```
INSTALLABLES = etags emacsclient $(CLIENTW) ebrowse
UTILITIES    = hexl  [movemail if !with_mailutils]  [update-game-score if use_gamedir]
DONT_INSTALL = make-docfile make-fingerprint  [+ asset-directory-tool / be-resources]
```

What `lib-src/meson.build` actually builds:

| Upstream binary | Meson target | Installed? | Note |
|---|---|---|---|
| `etags` | ✓ `etags` | yes (`bin/`) | parity |
| `ctags` | ✓ `ctags` (separate exe with `-DCTAGS=1`) | yes (`bin/`) | parity (fork chose separate exe, comment explains) |
| `emacsclient` | ✓ `emacsclient` | yes (`bin/`) | parity |
| `emacsclient.exe` (Windows GUI flavour `$CLIENTW`) | — | — | n/a-removed-area (no MS Windows). |
| `ebrowse` | ✓ `ebrowse` | yes (`bin/`) | parity |
| `hexl` | ✓ `hexl` | yes (`libexec/`) | parity |
| `movemail` | ✓ `movemail` | yes (libexec, gated on `--without-mailutils`) | parity |
| `update-game-score` | ✓ `update-game-score` | yes if `-Dgameuser=` | parity (sgid handled in `meson_install.py`) |
| `make-docfile` | ✓ `make-docfile` | no (build-only) | parity |
| `make-fingerprint` | ✓ `make-fingerprint` | no | parity |
| `rcs2log` (shell script) | — installed as `install_data` | yes | parity |
| `seccomp-filter` | ✓ `seccomp-filter` (Linux x86_64 + libseccomp) | no (build-only) | parity |
| `asset-directory-tool` (Android cross) | — | — | n/a-removed-area per `.claude/notes/build-system.md`. |
| `be-resources` (Haiku) | — | — | n/a-removed-area. |
| `pop` library (linked into movemail) | included in `movemail` sources | yes | parity (`pop.c` is in movemail's source list, not a separate exe). |
| `profile` | — | — | **missing-cosmetic** — upstream historically built a `profile` binary used by `M-x profile`.  Already removed upstream too (last seen pre-25); modern profiler is in-process.  No action needed. |

Net assessment: lib-src parity is essentially complete for the desktop
target set.

## 8. NS-specific (high-priority) gaps

NS bundle assembly is in `nextstep/meson.build` + `meson/run_app_bundle.py`.
Compared with `nextstep/Makefile.in` semantics and the upstream NS
config block (`configure.ac:2780-2940`):

### Confirmed parity

- `Info.plist` is rendered from `templates/Info.plist.in` with `@version@` /
  `@PACKAGE_BUGREPORT@` / `@copyright@` / `@year@` substituted, then
  copied to `Contents/Info.plist`.  Mirrors autotools.
- `Emacs.app/Contents/MacOS/Emacs` placement: the freshly built emacs
  binary is copied to `Contents/MacOS/Emacs` and made `0755`.
- `Cocoa/Emacs.base` skeleton (PkgInfo + `Contents/Resources/{Emacs.icns,
  document.icns, Credits.html}`) is copied wholesale.
- Self-contained mode copies `lisp/`, `etc/`, `info/`, and
  `emacs.pdmp` (renamed to `Emacs.pdmp`, placed under
  `Contents/MacOS/libexec/`).
- AppKit / Cocoa / QuartzCore / IOSurface / Carbon / CoreText /
  UniformTypeIdentifiers framework linkage is wired via
  `dependency('appleframeworks', modules : […])`.
- Cocoa-vs-GNUstep selection: `NS_IMPL_COCOA=1` set, GNUstep code paths
  not wired (matches the deletion of `nextstep/GNUstep/` from this fork's
  tree — see §10).

### Blocking NS gaps

- **`InfoPlist.strings` is rendered but never installed inside the
  bundle.**  `nextstep/meson.build:43-47` `configure_file()`s the file
  into `build/nextstep/InfoPlist.strings`, but `run_app_bundle.py` only
  copies `Info.plist` into `Contents/` — there's no
  `Contents/Resources/English.lproj/InfoPlist.strings` written.  Upstream
  `nextstep/Makefile.in:104-106` and `configure.ac:7743` install it to
  exactly that path.  Without it, macOS Finder shows the unlocalised
  bundle name and won't honour `NSHumanReadableCopyright`.
- **`NS_SELF_CONTAINED` macro never gets `#define`d.**  The macro is
  declared in `meson/config.h.in:142` indirectly via the NS block but
  there is no `conf_data.set('NS_SELF_CONTAINED', 1)` for the
  `-Dns-self-contained` option's enabled branch.  `src/emacs.c` and
  `src/lread.c` branch on it to look up `lisp/`, `etc/`, `info/`,
  `emacs.pdmp` relative to the bundle.  Today the self-contained bundle
  works only because `run_app_bundle.py` puts the resources in the same
  layout the source-tree fallback already expects — not because of the
  source-level gating.  Any future change to the lookup logic in
  `emacs.c` will silently break the bundle.
- **`HAVE_NATIVE_IMAGE_API` is never set on NS.**  Upstream defines it
  unconditionally on NS (`configure.ac:2861`) so `src/image.c` uses
  Cocoa's `NSImage`/`CGImage` decoders.  The Meson side links the
  frameworks but doesn't set the gate, so `src/image.c` falls back to
  the generic decoders (libjpeg/png/etc.).  On NS the bundle still
  works because libjpeg/png are also linked, but `nsimage.m`'s fast
  path is dead code.
- **`HAVE_XWIDGETS` on NS:** `meson.build:551-562` gates xwidgets on
  `gtk3_dep.found()`; the NS branch in `src/meson.build:333-336`
  separately adds the WebKit framework to `src_deps` but never sets
  `HAVE_XWIDGETS`/`USE_GTK_FOR_XWIDGETS=NS`.  So `-Dxwidgets=enabled`
  on Darwin reaches the error path "but GTK3 toolkit is not in use".
  Upstream's `configure.ac:4474` defines `HAVE_XWIDGETS` for the NS
  Cocoa+WebKit path too.
- **No code-signing step.**  `admin/build-darwin-universal.sh` (per
  `.claude/notes/build-system.md`) does ad-hoc signing for the
  universal `.dmg` release; the per-architecture `meson install` bundle
  produced by `run_app_bundle.py` is left unsigned.  macOS 14+ refuses
  to launch unsigned bundles outside the Applications folder for many
  users.  Upstream autotools doesn't sign either — parity, but worth
  noting.
- **No `LSUIElement` / `LSBackgroundOnly` / `NSAppRunningInBackground`
  plist keys.**  `Info.plist.in` lists usage-description strings but
  has no background-mode key.  Upstream Emacs daemon documentation
  expects users to add `LSUIElement=1` manually; the fork has no
  template variant for it.  Parity with upstream (autotools also has
  no `--with-ns-background` switch) — cosmetic.
- **Language resource bundles other than `English.lproj` are absent.**
  Upstream ships only `English.lproj/InfoPlist.strings` too — parity —
  but reducing to zero (current state) is a regression vs. upstream's
  one-language baseline.  Same fix as the InfoPlist.strings bullet.

### Non-blocking NS items

- `nextstep/Cocoa/Emacs.base/Contents/Resources/` ships only
  `Credits.html`, `Emacs.icns`, `document.icns`.  Matches upstream
  exactly (verified via `git ls-tree`).
- `nextstep/GNUstep/` is entirely absent from the local checkout; the
  Meson side doesn't reference it either, so dropping GNUstep is
  consistent.  If you ever want to re-enable GNUstep on Linux as a
  CI target, the upstream tree (`git ls-tree emacs-upstream/master nextstep/GNUstep/`)
  has the assets and the `Info-gnustep.plist.in` template is still in
  `templates/`.

## 9. Bonus — autotools-isms intentionally not re-implemented

These have no Meson equivalent and shouldn't get one:

- `--enable-maintainer-mode` — only matters when regenerating
  `configure` from `configure.ac`; dead with autotools gone.
- `--with-makeinfo` — Meson uses `find_program('makeinfo')` and skips
  doc builds when missing (`doc/meson.build:9-12`).
- `make distcheck` / `make-dist` — Meson has `meson dist` which is a
  superset of the autotools tarball workflow; release artefacts on
  this fork ship via `.github/workflows/release.yml` (Nix flake + DMG
  + tar.xz), not autotools `dist`.
- `aclocal` / `automake` / `autoreconf` / `gnulib-tool` regen — the
  fork's `lib/` is a vendored snapshot; `admin/notes/repo` upstream
  documents resyncing, but on the Meson side `lib/meson.build`
  enumerates the sources directly.
- `--enable-silent-rules` — Ninja is silent by default.
- `--enable-autodepend` — Ninja regenerates `.d` files natively.
- Debian multi-arch packaging hooks (`debian/`, `dh_*` autotools
  integration) — out of scope; downstream packagers (homebrew-emacs-plus,
  nix-darwin-emacs, MacPorts) consume `meson install` output directly,
  as documented in `.claude/notes/fork-*.md`.
- ChangeLog regeneration from git via `gitlog-to-changelog` — still
  available as a standalone script under `build-aux/`; not currently
  wired into Meson but not needed for builds.

## 10. Priority gaps — triage

### Blocking NS builds (must fix)

1. **`InfoPlist.strings` not installed** into
   `Emacs.app/Contents/Resources/English.lproj/`.  One-line fix in
   `meson/run_app_bundle.py` (`shutil.copy2(args.infoplist_strings,
   resources / 'English.lproj' / 'InfoPlist.strings')`) plus an extra
   arg from `nextstep/meson.build`.
2. **`NS_SELF_CONTAINED` macro not set** when `-Dns-self-contained` is
   allowed.  Add `conf_data.set('NS_SELF_CONTAINED', 1)` next to
   `HAVE_NS` so `src/emacs.c`'s bundle-resource lookup is enabled.
3. **`HAVE_NATIVE_IMAGE_API` not set on NS.**  Drop a
   `conf_data.set('HAVE_NATIVE_IMAGE_API', 1)` inside the `if ns_dep.found()`
   block.  Matches upstream's unconditional behaviour on NS.
4. **`HAVE_XWIDGETS` not reachable on NS.**  Loosen the
   `meson.build:552` gate from `gtk3_dep.found()` to
   `(gtk3_dep.found() or conf_data.has('HAVE_NS'))` and branch the
   WebKit dep accordingly (already done in `src/meson.build` partially;
   the config-define just needs to land).

### Affects non-NS but desired (fix when convenient)

5. **`-Dchecking=` is a no-op.**  None of the `ENABLE_CHECKING` /
   `CHECK_STRUCTS` / `GC_CHECK_STRING_BYTES` / `GC_CHECK_STRING_OVERRUN` /
   `GC_CHECK_STRING_FREE_LIST` / `GLYPH_DEBUG` defines are emitted.
   Critical for the debug build recipe in `CLAUDE.md`.
6. **`-Dgcc-warnings=` is a no-op.**  No `GCC_LINT` define, no
   `-Werror` flag.  Important for CI hygiene.
7. **`-Dcheck-lisp-object-type=true` is a no-op.**  Need
   `conf_data.set('CHECK_LISP_OBJECT_TYPE', 1)`.
8. **`-Dlto=true` is a no-op.**  Map to `b_lto=true` via
   `default_options` override or `add_project_arguments`.
9. **`HAVE_SQLITE3_LOAD_EXTENSION` probe missing.**  Trivially
   `cc.has_function('sqlite3_load_extension', dependencies : sqlite_dep)`.
10. **`HAVE_GETADDRINFO_A` probe missing on Linux.**  `cc.find_library('anl')`
    + function probe; without it async DNS is disabled.
11. **`HAVE_TIMERFD` probe missing on Linux.**  One `cc.has_header_symbol`.
12. **`HAVE_LIBMAIL`/`HAVE_LIBLOCKFILE` probes missing.**  Only matters
    for shared mail-spool installs but is the only thing that makes
    movemail safe in those setups.
13. **`HAVE_IMAGEMAGICK7`** vs `HAVE_IMAGEMAGICK` — split the
    MagickWand probe by version so `src/image.c`'s v7 fast path
    activates.
14. **`HAVE_PGTK` never set, even when `-Dtoolkit=pgtk`.**  Either
    drop the option to `n/a-removed-area` and document it, or add the
    `pgtkterm.c` source wiring (the latter is real work).
15. **Pkg-config version pins missing** for gnutls (>=2.12.2), libsystemd
    (>=222), tree-sitter (>=0.20.2), libxml-2.0 (>2.6.17), MagickWand
    (>=7 / Wand >=6.3.5), dbus-1 (>=1.0), gio-2.0 (>=2.26).  Cosmetic
    but matches the historical compatibility floor.
16. **`BINDIR` macro never defined.**  `lib-src/emacsclient.c` and
    `src/emacs.c` use it to locate the canonical install path.
17. **etc/charsets regenerated maps not installed.**  Walk
    `build_root/etc/charsets` in addition to `source_root/etc` in
    `meson_install.py`'s etc/ copy pass — or just write the regenerated
    files back to the source tree like `run_leim.py` does for quail.

### Cosmetic / build-system maintenance only

18. `--with-cairo-xcb` option is declared but never probed — remove it
    or wire it.
19. `--with-small-ja-dic` is declared but unused — wire it into
    `leim/meson.build` or drop the option.
20. `THREADS_ENABLED` macro (upstream sets it alongside `HAVE_THREADS`)
    — defensive, all current call sites tolerate its absence.
21. `_REENTRANT` / `_THREAD_SAFE` per-OS defines — modern toolchains
    handle this via `-pthread`.
22. `HAVE_X_SM` / `HAVE_XCB_SHAPE` / `USE_XCB` — Linux X11 only,
    cosmetic.
23. Per-OS quirk defines (`BROKEN_GET_CURRENT_DIR_NAME`,
    `BROKEN_PTY_READ_AFTER_EAGAIN`, `XOS_NEEDS_TIME_H`, `TIOCSIGSEND`,
    `HAVE_TINY_SPEED_T`, `USG_SUBTTY_WORKS`, `_STRUCTURED_PROC`,
    `USABLE_SIGPOLL`) — only relevant for HP-UX/Solaris/AIX/FreeBSD,
    none of which the fork targets.
24. `program-prefix` / `program-suffix` / `program-transform-name`
    support for desktop-file `Exec=` rewriting — wait for a real
    consumer.
25. Code-signing hook in `run_app_bundle.py` — `admin/build-darwin-universal.sh`
    handles the release case; per-arch local installs can stay
    ad-hoc-signed by the user.

---

Net: the Meson port covers ~90 % of the upstream option surface and
the entire desktop install surface, but four NS-specific gaps and
four developer-knob gaps mean documented workflows (`-Dchecking=`,
`-Dcheck-lisp-object-type=`, NS bundle self-containment, NS native
image API) are silently broken or downgraded.  Items 1–4 above are
the highest-leverage fixes; items 5–8 unblock the debug build recipe
in `CLAUDE.md`; everything else can backlog.
