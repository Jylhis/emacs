# leim/meson.build -- regenerate Quail input-method tables and
# leim-list.el.  Mirrors leim/Makefile.in at anchor 08a22b8965ec.
#
# Each step writes its outputs into the source tree (lisp/leim/quail/,
# lisp/leim/ja-dic/, lisp/language/pinyin.el) because byte-compile,
# loaddefs extraction, and the final pdumper image expect them there
# (mirrors the autotools `leimdir = ${srcdir}/../lisp/leim` decision).
#
# Stamp targets gate the regeneration on bootstrap-emacs +
# bootstrap-emacs.pdmp; loaddefs_stamp consumes leim_list_stamp so
# `lisp/leim/leim-list.el` exists before autoload extraction.

run_leim = files('../meson/run_leim.py')

_leim_dir = meson.global_source_root() / 'leim'
_cxterm_dir = _leim_dir / 'CXTERM-DIC'
_misc_dir = _leim_dir / 'MISC-DIC'
_skk_dic = _leim_dir / 'SKK-DIC' / 'SKK-JISYO.L'
_leim_ext = _leim_dir / 'leim-ext.el'

_leim_common = [
  '--bootstrap-emacs', bootstrap_emacs.full_path(),
  '--dump-file',       bootstrap_pdmp.full_path(),
  '--source-root',     meson.global_source_root(),
]

# --- TIT files (CXTERM-DIC) -- 14 files producing TIT_GB + TIT_BIG5 in
# leim/Makefile.in.
leim_tit_stamp = custom_target(
  'leim-tit-stamp',
  output  : 'leim-tit.stamp',
  command : [
    py, run_leim,
    _leim_common,
    '--tit', _cxterm_dir,
    '--stamp', '@OUTPUT@',
  ],
  depends : [bootstrap_emacs, bootstrap_pdmp, charsets_stamp],
  build_by_default : true,
)

# --- MISC-DIC files: HTML/map/cin/cangjie-table.* -> tsang/quick/PY/
# CTLau/ZIRANMA quail outputs.
leim_misc_stamp = custom_target(
  'leim-misc-stamp',
  output  : 'leim-misc.stamp',
  command : [
    py, run_leim,
    _leim_common,
    '--misc', _misc_dir,
    '--stamp', '@OUTPUT@',
  ],
  depends : [bootstrap_emacs, bootstrap_pdmp, charsets_stamp],
  build_by_default : true,
)

# --- pinyin.el (lives under lisp/language/, not lisp/leim/quail/).
leim_pinyin_stamp = custom_target(
  'leim-pinyin-stamp',
  output  : 'leim-pinyin.stamp',
  command : [
    py, run_leim,
    _leim_common,
    '--pinyin', _misc_dir / 'pinyin.map',
    '--stamp', '@OUTPUT@',
  ],
  depends : [bootstrap_emacs, bootstrap_pdmp, charsets_stamp],
  build_by_default : true,
)

# --- ja-dic (slow; ~30s with default --no-reduction).
leim_ja_dic_args = [
  py, run_leim,
  _leim_common,
  '--skk-dic', _skk_dic,
  '--stamp', '@OUTPUT@',
]
if get_option('small-ja-dic')
  leim_ja_dic_args += '--small-ja-dic'
endif
leim_ja_dic_stamp = custom_target(
  'leim-ja-dic-stamp',
  output  : 'leim-ja-dic.stamp',
  command : leim_ja_dic_args,
  depends : [bootstrap_emacs, bootstrap_pdmp, charsets_stamp],
  build_by_default : true,
)

# --- leim-list.el aggregates every quail-package registration.  Must
# run after every other generation step, since update-leim-list-file
# walks lisp/leim/.
leim_list_stamp = custom_target(
  'leim-list-stamp',
  output  : 'leim-list.stamp',
  command : [
    py, run_leim,
    _leim_common,
    '--leim-list',
    '--leim-ext', _leim_ext,
    '--stamp', '@OUTPUT@',
  ],
  depends : [
    bootstrap_emacs, bootstrap_pdmp, charsets_stamp,
    leim_tit_stamp, leim_misc_stamp,
    leim_pinyin_stamp, leim_ja_dic_stamp,
  ],
  build_by_default : true,
)
