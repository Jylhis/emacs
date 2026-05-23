# doc/meson.build -- Texinfo manuals.
#
# Builds the three core manuals (emacs, elisp, eintr) plus the
# 60+ doc/misc/ manuals into infodir.  Mirrors INFO_INSTALL from
# the deleted doc/misc/Makefile.in at 5d78a4c.

makeinfo = find_program('makeinfo', required : false)

if not makeinfo.found()
  message('makeinfo not found; doc/*.info targets disabled')
  subdir_done()
endif

# docstyle.texi and emacsver.texi live in doc/emacs/ and are
# included by the other manuals.  Add doc/emacs to every -I path.
shared_inc = meson.global_source_root() / 'doc/emacs'

# emacsver.texi is the @include'd version stamp under doc/emacs;
# autotools generates it from emacsver.texi.in via configure.
# Reproduce the substitution here so doc/lispintro (which @includes
# emacsver.texi) builds.
emacsver_data = configuration_data()
emacsver_data.set('version', meson.project_version())
emacsver_texi = configure_file(
  input         : meson.global_source_root() / 'doc/emacs/emacsver.texi.in',
  output        : 'emacsver.texi',
  configuration : emacsver_data,
)
emacsver_dir = meson.current_build_dir()  # build/doc/

manuals = []
# Aggregated spec list for the dvi/html/pdf/ps format loops below.
# Each entry: [output_name, src_dir, src_path, install_subdir].
manual_specs = []
foreach manual : [
  ['emacs',      'doc/emacs',      'emacs.texi'],
  ['elisp',      'doc/lispref',    'elisp.texi'],
  ['eintr',      'doc/lispintro',  'emacs-lisp-intro.texi'],
]
  name = manual[0]
  src_dir = meson.global_source_root() / manual[1]
  src = src_dir / manual[2]
  manual_specs += [[name, src_dir, src, '']]
  manuals += custom_target(
    name + '.info',
    output  : name + '.info',
    command : [makeinfo,
               '--force',
               '--enable-encoding',
               '-I', src_dir,
               '-I', shared_inc,
               '-I', emacsver_dir,
               '--no-split',
               '-o', '@OUTPUT@',
               src],
    depend_files : [emacsver_texi],
    install : true,
    install_dir : get_option('infodir'),
    build_by_default : true,
  )
endforeach

# doc/misc/ manuals.  Pairs are [<output_basename>, <source_basename>];
# almost all are name-to-name, the one exception is `cc-mode.texi`
# which `@setfilename`s to `ccmode.info` (autotools'
# INFO_INSTALL:ccmode=cc-mode substitution).  The list mirrors
# INFO_COMMON in the deleted doc/misc/Makefile.in at 5d78a4c.
misc_dir = meson.global_source_root() / 'doc/misc'

# ----------------------------------------------------------------------
# org and modus-themes -- their .texi sources are generated from .org
# via emacs -l ox-texinfo.  Mirrors the org_template macro in the
# deleted doc/misc/Makefile.in at anchor 08a22b8965ec.  Requires the
# built emacs + emacs.pdmp (bootstrap-emacs lacks ox-texinfo deps),
# so the custom_targets here depend on the binary at src/emacs and
# the dumped image at lisp/emacs.pdmp.
# ----------------------------------------------------------------------
run_org_to_texi = files('../meson/run_org_to_texi.py')
org_texi_targets = {}
foreach name : ['org', 'modus-themes']
  org_texi_targets += {
    name: custom_target(
      name + '.texi',
      output  : name + '.texi',
      command : [
        py, run_org_to_texi,
        '--emacs',       emacs.full_path(),
        '--dump-file',   emacs_pdmp.full_path(),
        '--source-root', meson.global_source_root(),
        '--input',       misc_dir / (name + '.org'),
        '--output',      '@OUTPUT@',
      ],
      depends : [emacs, emacs_pdmp],
      build_by_default : true,
    ),
  }
endforeach

foreach pair : [
  ['auth',          'auth'],
  ['autotype',      'autotype'],
  ['bovine',        'bovine'],
  ['calc',          'calc'],
  ['ccmode',        'cc-mode'],
  ['cl',            'cl'],
  ['dbus',          'dbus'],
  ['dired-x',       'dired-x'],
  ['ebrowse',       'ebrowse'],
  ['ede',           'ede'],
  ['ediff',         'ediff'],
  ['edt',           'edt'],
  ['efaq',          'efaq'],
  ['eglot',         'eglot'],
  ['eieio',         'eieio'],
  ['emacs-gnutls',  'emacs-gnutls'],
  ['emacs-mime',    'emacs-mime'],
  ['epa',           'epa'],
  ['erc',           'erc'],
  ['ert',           'ert'],
  ['eshell',        'eshell'],
  ['eudc',          'eudc'],
  ['eww',           'eww'],
  ['flymake',       'flymake'],
  ['forms',         'forms'],
  ['gnus',          'gnus'],
  ['htmlfontify',   'htmlfontify'],
  ['idlwave',       'idlwave'],
  ['ido',           'ido'],
  ['info',          'info'],
  ['mairix-el',     'mairix-el'],
  ['message',       'message'],
  ['mh-e',          'mh-e'],
  ['modus-themes',  'modus-themes'],  # generated from .org
  ['newsticker',    'newsticker'],
  ['nxml-mode',     'nxml-mode'],
  ['octave-mode',   'octave-mode'],
  ['org',           'org'],            # generated from .org
  ['pcl-cvs',       'pcl-cvs'],
  ['rcirc',         'rcirc'],
  ['reftex',        'reftex'],
  ['remember',      'remember'],
  ['sasl',          'sasl'],
  ['sc',            'sc'],
  ['semantic',      'semantic'],
  ['ses',           'ses'],
  ['sieve',         'sieve'],
  ['smtpmail',      'smtpmail'],
  ['speedbar',      'speedbar'],
  ['srecode',       'srecode'],
  ['todo-mode',     'todo-mode'],
  ['tramp',         'tramp'],
  ['transient',     'transient'],
  ['url',           'url'],
  ['use-package',   'use-package'],
  ['vhdl-mode',     'vhdl-mode'],
  ['viper',         'viper'],
  ['vtable',        'vtable'],
  ['widget',        'widget'],
  ['wisent',        'wisent'],
  ['woman',         'woman'],
]
  out = pair[0]
  src_name = pair[1]
  if org_texi_targets.has_key(src_name)
    # Generated .texi: source is the org_to_texi custom_target output.
    _texi_target = org_texi_targets[src_name]
    _texi_path = _texi_target.full_path()
    _info_deps = [_texi_target]
  else
    _texi_target = []
    _texi_path = misc_dir / (src_name + '.texi')
    _info_deps = []
  endif
  manual_specs += [[out, misc_dir, _texi_path, '']]
  manuals += custom_target(
    out + '.info',
    output  : out + '.info',
    command : [makeinfo,
               '--force',
               '--enable-encoding',
               '-I', misc_dir,
               '-I', shared_inc,
               '-I', emacsver_dir,
               '--no-split',
               '-o', '@OUTPUT@',
               _texi_path],
    depend_files : [emacsver_texi],
    depends : _info_deps,
    install : true,
    install_dir : get_option('infodir'),
    build_by_default : true,
  )
endforeach


# ----------------------------------------------------------------------
# doc/translations/ -- localized info pages.  The autotools tree at
# anchor 08a22b8965ec built ses-fr.info from doc/translations/fr/misc/
# and installed it under $infodir/fr.  Add new languages by
# extending this list.
# ----------------------------------------------------------------------
translations = [
  ['fr', 'misc', 'ses-fr'],
]
foreach t : translations
  lang = t[0]
  subdir_path = t[1]
  basename = t[2]
  src_dir = (meson.global_source_root()
             / 'doc/translations' / lang / subdir_path)
  manual_specs += [[basename, src_dir,
                    src_dir / (basename + '.texi'), lang]]
  manuals += custom_target(
    basename + '.info',
    output  : basename + '.info',
    command : [makeinfo,
               '--force',
               '--enable-encoding',
               '-I', src_dir,
               '-I', shared_inc,
               '-I', emacsver_dir,
               '--no-split',
               '-o', '@OUTPUT@',
               src_dir / (basename + '.texi')],
    depend_files : [emacsver_texi],
    install : true,
    install_dir : get_option('infodir') / lang,
    build_by_default : true,
  )
endforeach

alias_target('info', manuals)

# ----------------------------------------------------------------------
# Optional non-info doc formats (dvi/html/pdf/ps).  Each format
# requires a different external tool (texi2dvi for dvi/ps, texi2pdf
# for pdf, makeinfo --html for html).  Skip silently when the tool
# isn't installed -- packagers who want them install the matching
# texlive bundle.
# Reference: anchor 08a22b8965ec doc/{emacs,lispref,...}/Makefile.in
# all-other-formats targets.
# ----------------------------------------------------------------------
texi2dvi = find_program('texi2dvi', required : false)
texi2pdf = find_program('texi2pdf', required : false)

# Common include flags for all non-info formats; --no-split keeps the
# output a single file rather than a directory tree.
_doc_inc = ['-I', shared_inc, '-I', emacsver_dir]

foreach fmt : [
  # --force / --no-validate let makeinfo emit output even when
  # cross-references span manuals (e.g. emacs.texi -> elisp.texi),
  # matching autotools' tolerance for the same warnings.
  ['html', makeinfo, ['--html', '--no-split',
                       '--force', '--no-validate'], '.html'],
  ['dvi',  texi2dvi, ['--quiet', '--clean'],   '.dvi'],
  ['pdf',  texi2pdf, ['--quiet', '--clean'],   '.pdf'],
  ['ps',   texi2dvi, ['--quiet', '--clean', '--ps'], '.ps'],
]
  fmt_name = fmt[0]
  fmt_tool = fmt[1]
  fmt_args = fmt[2]
  fmt_ext  = fmt[3]
  if not fmt_tool.found()
    continue
  endif
  fmt_targets = []
  foreach spec : manual_specs
    out_name  = spec[0]
    spec_dir  = spec[1]
    spec_src  = spec[2]
    fmt_targets += custom_target(
      out_name + fmt_ext,
      output  : out_name + fmt_ext,
      command : [fmt_tool, fmt_args,
                 '-I', spec_dir, _doc_inc,
                 '-o', '@OUTPUT@',
                 spec_src],
      depend_files : [emacsver_texi],
      build_by_default : false,
    )
  endforeach
  alias_target(fmt_name, fmt_targets)
endforeach
