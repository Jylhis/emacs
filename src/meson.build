# src/meson.build -- core Emacs C sources.
#
# STATUS: phase 3 in progress.  Currently wires the generators that
# produce src/globals.h and src/lisp.mk -- two artefacts that every
# src/ object file (and the eventual temacs link) depends on.
# Compilation of src/*.c, the temacs/emacs/pdumper bootstrap dance,
# native compilation, and dumping all land in subsequent commits.
# See .claude/plans/migrate-from-current-build-replicated-gadget.md.

# ----------------------------------------------------------------------
# base_obj source list (Linux/GTK3 + Cairo + inotify baseline).
# Mirrors src/Makefile.in:389-408 with the conditional groups
# expanded for window_system=x11 / with_gtk3=yes / HAVE_CAIRO=yes /
# HAVE_INOTIFY=yes (configure.ac:6369-6420 + 3313 + 3630).  Phase 3
# follow-ups can swap in NS / Android / pgtk variants by replacing
# the X11/GTK groups.
# ----------------------------------------------------------------------
base_obj_core = [
  'alloc.c', 'atimer.c', 'bidi.c', 'bignum.c', 'buffer.c', 'bytecode.c',
  'callint.c', 'callproc.c', 'casefiddle.c', 'casetab.c', 'category.c',
  'ccl.c', 'character.c', 'charset.c', 'chartab.c', 'cmds.c', 'coding.c',
  'composite.c', 'comp.c', 'data.c', 'decompress.c', 'dired.c',
  'dispnew.c', 'doc.c', 'doprnt.c', 'editfns.c', 'emacs-module.c',
  'emacs.c', 'eval.c',
  'fileio.c', 'filelock.c', 'floatfns.c', 'fns.c', 'font.c', 'frame.c',
  'gnutls.c', 'indent.c', 'insdel.c', 'intervals.c', 'itree.c', 'json.c',
  'keyboard.c', 'keymap.c', 'lcms.c', 'lread.c', 'macros.c', 'marker.c',
  'menu.c', 'minibuf.c', 'pdumper.c', 'print.c', 'process.c',
  'profiler.c', 'regex-emacs.c', 'region-cache.c', 'scroll.c',
  'search.c', 'sort.c', 'sound.c', 'sqlite.c', 'syntax.c', 'sysdep.c',
  'systhread.c', 'term.c', 'terminal.c', 'textprop.c', 'thread.c',
  'timefns.c', 'treesit.c', 'undo.c', 'window.c', 'xdisp.c', 'xfaces.c',
  'xml.c',
]

# X11 toolkit objects (configure.ac:6369: XOBJ + XMENU_OBJ).
xobj = ['xterm.c', 'xfns.c', 'xmenu.c', 'xselect.c', 'xrdb.c',
        'xsmfns.c', 'xsettings.c']

# GTK toolkit support (configure.ac:3313, 3331).
gtk_obj = ['gtkutil.c', 'emacsgtkfixed.c']

# Termcap output (configure.ac:2349, used by tty terminal driver).
cm_obj = ['cm.c']

# Dynamic library loader (dlopen wrapper, configure.ac:4660 -- we
# always need it since HAVE_NATIVE_COMP / HAVE_MODULES is set).
dynlib_obj = ['dynlib.c']

# Window-system shared (configure.ac:6655).
window_system_obj = ['fontset.c', 'fringe.c', 'image.c', 'textconv.c']

# Font backend objects (configure.ac:6370 with HAVE_CAIRO).  With
# cairo, ftcrfont.c replaces xftfont.c.
font_obj = ['xfont.c', 'ftfont.c', 'ftcrfont.c', 'hbfont.c']

# inotify (configure.ac:3630, Linux file notification).
notify_obj = ['inotify.c']

# X-glib select (configure.ac:3530).
xgselect_obj = ['xgselect.c']

base_obj_basenames = (
  base_obj_core + xobj + gtk_obj + window_system_obj
  + font_obj + notify_obj + xgselect_obj
  + cm_obj + dynlib_obj
)
base_obj_sources = files(base_obj_basenames)

# ----------------------------------------------------------------------
# globals.h -- function/variable forward declarations harvested from
# every src/*.c file by make-docfile -g.  See src/Makefile.in:600.
# ----------------------------------------------------------------------
globals_h = custom_target(
  'globals.h',
  input  : base_obj_sources,
  output : 'globals.h',
  command : [
    make_docfile,
    '-d', meson.current_source_dir(),
    '-g',
  ] + base_obj_basenames,
  capture : true,
)

# ----------------------------------------------------------------------
# lisp.mk -- list of Lisp files loadup.el will load, extracted from
# the (load "...") forms in lisp/loadup.el.  See
# src/Makefile.in:488-494.  We only need this as a Meson-side data
# structure, not a literal makefile fragment, so the script outputs a
# JSON list that meson.build can read once we wire the lisp/ subdir.
# ----------------------------------------------------------------------
make_lisp_mk = files('../meson/make_lisp_mk.py')

shortlisp_json = custom_target(
  'shortlisp.json',
  input   : '../lisp/loadup.el',
  output  : 'shortlisp.json',
  command : [py, make_lisp_mk, '@INPUT@', '@OUTPUT@'],
)

# ----------------------------------------------------------------------
# emacs-module.h -- substitute @emacs_major_version@ and inline
# module-env-NN.h snippets (mirrors AC_SUBST + AC_SUBST_FILE in
# configure.ac:4437-4452).
# ----------------------------------------------------------------------
make_emacs_module_h = files('../meson/make_emacs_module_h.py')

emacs_module_h = custom_target(
  'emacs-module.h',
  input  : 'emacs-module.in.h',
  output : 'emacs-module.h',
  command : [
    py, make_emacs_module_h,
    '--input',         '@INPUT@',
    '--output',        '@OUTPUT@',
    '--src-dir',       meson.current_source_dir(),
    '--major-version', emacs_version.split('.')[0],
  ],
)

# ----------------------------------------------------------------------
# epaths.h -- runtime path defaults baked into the binary.  The
# autotools build sed-substitutes these from variables that 'configure'
# resolves (Makefile.in:443-471).  Use a Meson-side template populated
# from get_option('prefix') etc.
# ----------------------------------------------------------------------
epaths_data = configuration_data()
prefix = get_option('prefix')
datadir = prefix / get_option('datadir')
libexecdir = prefix / get_option('libexecdir')
infodir = prefix / get_option('infodir')
localstatedir = prefix / get_option('localstatedir')

epaths_data.set_quoted('PATH_LOADSEARCH',
    datadir + '/emacs/' + emacs_version + '/lisp')
epaths_data.set_quoted('PATH_REL_LOADSEARCH', '')
epaths_data.set_quoted('PATH_SITELOADSEARCH',
    datadir + '/emacs/site-lisp')
epaths_data.set_quoted('PATH_DUMPLOADSEARCH', '../lisp')
epaths_data.set_quoted('PATH_EXEC',
    libexecdir + '/emacs/' + emacs_version + '/' +
    host_machine.cpu_family() + '-' + host_machine.system())
epaths_data.set_quoted('PATH_DATA',
    datadir + '/emacs/' + emacs_version + '/etc')
epaths_data.set_quoted('PATH_BITMAPS', '/usr/include/X11/bitmaps')
epaths_data.set_quoted('PATH_DOC',
    datadir + '/emacs/' + emacs_version + '/etc')
epaths_data.set_quoted('PATH_INFO', infodir)
epaths_data.set_quoted('PATH_GAME',
    localstatedir + '/games/emacs')
epaths_data.set_quoted('PATH_X_DEFAULTS',
    '/usr/lib/X11/%L/%T/%N%C%S:/usr/lib/X11/%l/%T/%N%C%S:'
    + '/usr/lib/X11/%T/%N%C%S:/usr/lib/X11/%L/%T/%N%S:'
    + '/usr/lib/X11/%l/%T/%N%S:/usr/lib/X11/%T/%N%S')

epaths_h = configure_file(
  input         : '../meson/epaths.h.in',
  output        : 'epaths.h',
  configuration : epaths_data,
)

# ----------------------------------------------------------------------
# buildobj.h -- the list of base_obj objects as C string literals.
# Used by doc.c to attribute primitives to their source files
# (mirrors src/Makefile.in:591).
# ----------------------------------------------------------------------
make_buildobj_h = files('../meson/make_buildobj_h.py')

buildobj_h = custom_target(
  'buildobj.h',
  output : 'buildobj.h',
  command : [py, make_buildobj_h, '@OUTPUT@'] + base_obj_basenames,
)

# ----------------------------------------------------------------------
# Compile probe: assemble the src/*.c files known to build cleanly
# (91 of 124 as of this writing) into a static library.  This isn't
# usable for linking temacs yet -- many cross-file symbols are still
# undefined -- but it forces meson + ninja to actually build src/
# objects on every CI run, so regressions are caught early.
# Phase-3 follow-ups will (a) bring the remaining 33 files online by
# wiring more feature defines, and (b) replace this probe with a real
# temacs executable() once link-time issues are addressed.
# ----------------------------------------------------------------------
src_compile_probe_sources = files(
  'alloc.c', 'atimer.c', 'bidi.c', 'bignum.c', 'buffer.c', 'bytecode.c',
  'callint.c', 'callproc.c', 'casefiddle.c', 'casetab.c', 'category.c',
  'ccl.c', 'character.c', 'charset.c', 'chartab.c', 'cmds.c', 'coding.c',
  'composite.c', 'comp.c', 'data.c', 'decompress.c', 'dired.c',
  'dispnew.c', 'doc.c', 'doprnt.c', 'editfns.c', 'emacs.c', 'eval.c',
  'fileio.c', 'filelock.c', 'floatfns.c', 'fns.c', 'font.c', 'frame.c',
  'gnutls.c', 'indent.c', 'insdel.c', 'intervals.c', 'itree.c', 'json.c',
  'keyboard.c', 'keymap.c', 'lcms.c', 'lread.c', 'macros.c', 'marker.c',
  'menu.c', 'minibuf.c', 'pdumper.c', 'print.c', 'process.c',
  'profiler.c', 'regex-emacs.c', 'region-cache.c', 'scroll.c',
  'search.c', 'sort.c', 'sound.c', 'sqlite.c', 'syntax.c', 'sysdep.c',
  'systhread.c', 'term.c', 'terminal.c', 'textprop.c', 'thread.c',
  'timefns.c', 'treesit.c', 'undo.c', 'window.c', 'xdisp.c', 'xfaces.c',
  'xml.c',
  # X11 / GTK / font / window-system files known to compile.
  'fontset.c', 'fringe.c', 'image.c', 'xfont.c', 'ftfont.c',
  'ftcrfont.c', 'hbfont.c', 'inotify.c', 'xgselect.c',
  'xrdb.c', 'xsmfns.c', 'emacs-module.c',
  # Now that HAVE_XRMSETDATABASE et al are set, the heavyweight
  # X11/GTK files compile too.
  'xterm.c', 'xfns.c', 'xmenu.c', 'xselect.c', 'xsettings.c',
  'gtkutil.c', 'emacsgtkfixed.c', 'sound.c', 'textconv.c',
  # Termcap, dynlib (configure.ac:2349, 4660).  With TERMINFO=yes,
  # terminfo.c provides tparam/BC/UP linked against -ltinfo;
  # tparam.c is the !TERMINFO alternative.
  'cm.c', 'dynlib.c', 'terminfo.c',
)

# Likewise add 'emacs-module' to the source list for libemacs_src_probe
# (mirrors src/Makefile.in $(MODULES_OBJ) inclusion when modules are
# enabled, configure.ac:4421).

src_compile_probe = static_library(
  'emacs_src_probe',
  sources : [
    src_compile_probe_sources,
    globals_h, buildobj_h, emacs_module_h, epaths_h,
  ],
  include_directories : [
    top_inc, include_directories('.', '../lib'),
  ],
  dependencies : [
    libgnu_dep, gtk3_dep, cairo_dep, cairo_ft_dep, harfbuzz_dep,
    freetype_dep, fontconfig_dep, xft_dep, gnutls_dep, treesit_dep,
    sqlite_dep, xml_dep, systemd_dep, gmp_dep,
  ],
  c_args : [
    # Mirrors EMACS_CFLAGS in src/Makefile.in:309 for the GTK3 build.
  ],
  install : false,
  build_by_default : true,
)

# TODO(phase-3): compile base_obj_sources into temacs.o objects, link
# temacs, run loadup.el via temacs --temacs=pbootstrap to produce
# bootstrap-emacs.pdmp, then re-run as --temacs=pdump for the final
# emacs binary.  See src/Makefile.in:563-895.
