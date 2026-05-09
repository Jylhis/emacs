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
foreach manual : [
  ['emacs',      'doc/emacs',      'emacs.texi'],
  ['elisp',      'doc/lispref',    'elisp.texi'],
  ['eintr',      'doc/lispintro',  'emacs-lisp-intro.texi'],
]
  name = manual[0]
  src_dir = meson.global_source_root() / manual[1]
  src = src_dir / manual[2]
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
  # modus-themes is generated from doc/misc/modus-themes.org via emacs
  # batch (TEXI_FROM_ORG in the deleted Makefile.in).  Skip until the
  # org->texi step is ported.
  ['newsticker',    'newsticker'],
  ['nxml-mode',     'nxml-mode'],
  ['octave-mode',   'octave-mode'],
  # org is generated from doc/misc/org.org via emacs batch
  # (TEXI_FROM_ORG); skipped alongside modus-themes.
  ['pcl-cvs',       'pcl-cvs'],
  ['pgg',           'pgg'],
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
               misc_dir / (src_name + '.texi')],
    depend_files : [emacsver_texi],
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
