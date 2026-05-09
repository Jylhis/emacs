# src/meson.build -- core Emacs C sources.
#
# STATUS: phase 3 in progress.  Currently wires the generators that
# produce src/globals.h and src/lisp.mk -- two artefacts that every
# src/ object file (and the eventual temacs link) depends on.
# Compilation of src/*.c, the temacs/emacs/pdumper bootstrap dance,
# native compilation, and dumping all land in subsequent commits.
#
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

# File notification backend (configure.ac:3630-3679).
if conf_data.has('HAVE_INOTIFY')
  notify_obj = ['inotify.c']
elif conf_data.has('HAVE_KQUEUE')
  notify_obj = ['kqueue.c']
elif conf_data.has('HAVE_GFILENOTIFY')
  notify_obj = ['gfilenotify.c']
else
  notify_obj = []
endif

# X-glib select (configure.ac:3530).
xgselect_obj = ['xgselect.c']

# Conditional source files driven by feature probes (mirror the
# _OBJ variables in the deleted src/Makefile.in at 5d78a4c:
# DBUS_OBJ, XWIDGETS_OBJ, ...).  src/emacs.c references syms_of_dbusbind
# / init_dbusbind / syms_of_xwidget when HAVE_DBUS / HAVE_XWIDGETS
# is set, so the matching .c file must be compiled.
feature_obj = []
if conf_data.has('HAVE_DBUS')
  feature_obj += 'dbusbind.c'
endif
if conf_data.has('HAVE_XWIDGETS')
  feature_obj += 'xwidget.c'
endif

# Assemble base_obj depending on whether we have a GUI toolkit.
if gtk3_dep.found()
  base_obj_basenames = (
    base_obj_core + xobj + gtk_obj + window_system_obj
    + font_obj + notify_obj + xgselect_obj
    + cm_obj + dynlib_obj + feature_obj
  )
else
  # Terminal-only or NS build (NS sources not yet wired).
  base_obj_basenames = (
    base_obj_core + notify_obj
    + cm_obj + dynlib_obj + feature_obj
  )
endif
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
# etc/DOC -- doc strings extracted from base_obj sources by
# make-docfile -d.  Snarf-documentation in loadup.el reads it during
# the final pdump (loadup.el calls (Snarf-documentation "DOC")).
# Mirrors src/Makefile.in:583.
# ----------------------------------------------------------------------
etc_doc = custom_target(
  'etc-DOC',
  input  : base_obj_sources,
  output : 'DOC',
  command : [
    make_docfile,
    '-d', meson.current_source_dir(),
  ] + base_obj_basenames,
  capture : true,
  build_by_default : true,
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
  install : true,
  install_dir : get_option('includedir'),
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

# PATH_SITELOADSEARCH -- the colon-separated default list of site-lisp
# directories (configure.ac at anchor 08a22b8965ec sets locallisppath
# to '${datadir}/emacs/${version}/site-lisp:${datadir}/emacs/site-lisp'
# unless --enable-locallisppath=PATH overrides it).
_locallisppath = get_option('locallisppath')
if _locallisppath == ''
  _locallisppath = (datadir + '/emacs/' + emacs_version + '/site-lisp'
                    + ':' + datadir + '/emacs/site-lisp')
endif
epaths_data.set_quoted('PATH_SITELOADSEARCH', _locallisppath)
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
# Compile probe / temacs source list.  Built from base_obj_basenames
# (which is already platform-conditional) plus emacs-module.c and
# terminfo.c.
# ----------------------------------------------------------------------
src_compile_probe_sources = files(
  base_obj_basenames + ['emacs-module.c', 'terminfo.c'],
)

# Extra X11 / terminfo libraries that pkg-config doesn't list but
# xterm.c, xfns.c, etc. directly call (XFixesSelectSelectionInput,
# XShapeQueryExtension, XRender* ...).
extra_x_libs = []
if gtk3_dep.found()
  extra_x_libs = [
    cc.find_library('X11',        required : true),
    cc.find_library('Xfixes',     required : true),
    cc.find_library('Xrender',    required : true),
    cc.find_library('Xrandr',     required : true),
    cc.find_library('Xcomposite', required : true),
    cc.find_library('Xinerama',   required : true),
    cc.find_library('Xi',         required : true),
    cc.find_library('Xext',       required : true),
    cc.find_library('Xtst',       required : true),
    cc.find_library('SM',         required : true),  # X Session Mgmt
    cc.find_library('ICE',        required : true),  # X ICE
  ]
endif
# terminfo (ncurses).
tinfo_dep = cc.find_library('tinfo', required : false)
if not tinfo_dep.found()
  tinfo_dep = cc.find_library('ncurses', required : true)
endif

src_deps = [
  libgnu_dep, gnutls_dep, treesit_dep,
  sqlite_dep, xml_dep, gmp_dep,
  dependency('threads'),
  tinfo_dep,
] + extra_x_libs
if gtk3_dep.found()
  src_deps += [gtk3_dep, cairo_dep, cairo_ft_dep,
               harfbuzz_dep, freetype_dep, fontconfig_dep, xft_dep]
else
  # Without GTK, still link harfbuzz/freetype if found (used by hbfont.c etc.).
  if harfbuzz_dep.found()
    src_deps += harfbuzz_dep
  endif
  if freetype_dep.found()
    src_deps += freetype_dep
  endif
endif
if systemd_dep.found()
  src_deps += systemd_dep
endif
if libgccjit_dep.found()
  src_deps += libgccjit_dep
endif

# B2 -- silent option probes wired in meson.build add new deps here so
# their consumers (src/image.c, src/sound.c, src/dbusbind.c, ...)
# link.  Each `if dep.found()` keeps the link line clean when the
# option resolves to disabled.
foreach _dep : [
  jpeg_dep, tiff_dep, png_dep, gif_dep, rsvg_dep, webp_dep, xpm_dep,
  imagemagick_dep, lcms2_dep, dbus_dep, gpm_dep, gio_dep, selinux_dep,
  zlib_dep, libotf_dep, m17n_flt_dep, alsa_dep, webkit_dep,
]
  if _dep.found()
    src_deps += _dep
  endif
endforeach

src_args = ['-DEMACS_CORE=1']

# --enable-profiling at anchor 08a22b8965ec configure.ac: adds -pg to
# both compile and link, plus -DPROFILING=1 so src/emacs.c's main()
# stops the profiler in the right place (cf. src/emacs.c:101).
profiling_args = []
profiling_link_args = []
if get_option('profiling')
  src_args += ['-DPROFILING=1', '-pg']
  profiling_link_args = ['-pg']
endif

src_compile_probe = static_library(
  'emacs_src_probe',
  sources : [
    src_compile_probe_sources,
    globals_h, buildobj_h, emacs_module_h, epaths_h,
  ],
  include_directories : [
    top_inc, include_directories('.', '../lib'),
  ],
  c_args : src_args,
  dependencies : src_deps,
  install : false,
  build_by_default : false,
)

# Phase-3 milestone: link temacs from the same source set.  This is
# the C-only stage of the bootstrap (src/Makefile.in:624-643).
temacs = executable(
  'temacs',
  sources : [
    src_compile_probe_sources,
    globals_h, buildobj_h, emacs_module_h, epaths_h,
  ],
  include_directories : [
    top_inc, include_directories('.', '../lib'),
  ],
  c_args : src_args,
  dependencies : src_deps,
  link_args : (is_linux ? ['-ldl', '-lm'] : ['-lm']) + profiling_link_args,
  install : false,
)

# ----------------------------------------------------------------------
# Bootstrap dump cycle.  Mirrors src/Makefile.in:872-895:
#
#     bootstrap-emacs := cp temacs
#     bootstrap-emacs.pdmp := bootstrap-emacs --batch -l loadup
#                                             --temacs=pbootstrap
#
# Then phase 4 byte-compiles compile-first lisp using bootstrap-emacs,
# phase 5 native-compiles, and finally:
#
#     emacs := cp temacs
#     emacs.pdmp := emacs --batch -l loadup --temacs=pdump
#
# At this point the dump cycle does NOT successfully run end-to-end:
# loadup.el wants byte-compiled .elc files (phase 4) and the
# generated etc/charsets/ map files (phase 6).  The custom_targets
# below capture the dependency chain so phases 4 and 6 can plug in.
# ----------------------------------------------------------------------
bootstrap_emacs = custom_target(
  'bootstrap-emacs',
  output  : 'bootstrap-emacs',
  command : ['cp', '-f', temacs.full_path(), '@OUTPUT@'],
  depends : [temacs],
  build_by_default : true,
)

# bootstrap-emacs.pdmp -- the workhorse dumped image.  Generated
# WITHOUT unidata so the chicken-and-egg (uni-*.el needs a working
# emacs to generate; loadup.el calls (load "charprop.el" t) which is
# silent on missing) is broken.  bootstrap-emacs.pdmp drives every
# subsequent script (run_unidata, run_loaddefs, byte_compile_batch);
# undumped temacs segfaults on those workloads.
run_dump = files('../meson/run_dump.py')
_bootstrap_dump_args = [
  py, run_dump,
  '--bootstrap-emacs', bootstrap_emacs.full_path(),
  '--source-root',     meson.global_source_root(),
  '--output-pdmp',     '@OUTPUT@',
  '--mode',            'pbootstrap',
  '--charscript',      charscript_el.full_path(),
  '--emoji-zwj',       emoji_zwj_el.full_path(),
]
if not build_details_opt
  _bootstrap_dump_args += '--no-build-details'
endif
bootstrap_pdmp = custom_target(
  'bootstrap-emacs.pdmp',
  output  : 'bootstrap-emacs.pdmp',
  command : _bootstrap_dump_args,
  depends : [bootstrap_emacs, charscript_el, emoji_zwj_el,
             charsets_stamp],
  build_by_default : false,
)

# Unicode tables -- runs admin/unidata/unidata-gen.el against
# bootstrap-emacs.pdmp to generate lisp/international/uni-*.el and
# charprop.el.  Mirrors admin/unidata/Makefile.in.
unidata_stamp = custom_target(
  'unidata-stamp',
  output  : 'unidata.stamp',
  command : [
    py, run_unidata,
    '--bootstrap-emacs', bootstrap_emacs.full_path(),
    '--dump-file',       bootstrap_pdmp.full_path(),
    '--source-root',     meson.global_source_root(),
    '--stamp',           '@OUTPUT@',
    '--charscript',      charscript_el.full_path(),
    '--emoji-zwj',       emoji_zwj_el.full_path(),
  ],
  depends : [bootstrap_emacs, bootstrap_pdmp, charsets_stamp,
             charscript_el, emoji_zwj_el],
  build_by_default : true,
)

# ----------------------------------------------------------------------
# Final dump.  Mirrors src/Makefile.in:563-573:
#
#     emacs := cp temacs
#     emacs.pdmp := emacs --batch -l loadup --temacs=pdump
#
# Differs from the bootstrap dump in that loadup.el reads .elc files
# rather than .el sources, so the full lisp/ byte-compile must
# precede this.  emacs.pdmp itself is defined in lisp/meson.build
# (it depends on compile_main_elcs and loaddefs_stamp).
# ----------------------------------------------------------------------
emacs = custom_target(
  'emacs',
  output  : 'emacs',
  command : ['cp', '-f', temacs.full_path(), '@OUTPUT@'],
  depends : [temacs],
  build_by_default : true,
)

# emacs.pdmp -- defined in lisp/meson.build because it depends on
# compile_main_elcs and loaddefs_stamp (lisp/meson.build is loaded
# after src/meson.build).
