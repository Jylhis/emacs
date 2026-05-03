# doc/meson.build -- Texinfo manuals.
#
# STATUS: phase 6 finish.  Builds the four core manuals' .info files
# via makeinfo.  See .claude/plans/migrate-from-current-build-replicated-gadget.md.
#
# `meson compile -C build info` emits all info files into build/info/.
# pdf/html targets are autotools-only for now -- low priority during
# migration.

makeinfo = find_program('makeinfo', required : false)

if not makeinfo.found()
  message('makeinfo not found; doc/*.info targets disabled')
  subdir_done()
endif

info_dir = meson.current_build_dir() / '..' / 'info'

# docstyle.texi and emacsver.texi live in doc/emacs/ and are
# included by the other manuals.  Add doc/emacs to every -I path.
shared_inc = meson.global_source_root() / 'doc/emacs'

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
               '--no-split',
               '-o', '@OUTPUT@',
               src],
    install : true,
    install_dir : get_option('infodir'),
    build_by_default : true,
  )
endforeach

alias_target('info', manuals)
