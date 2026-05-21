;;; external-packages.eld --- External-development inventory  -*- lisp-data; coding: utf-8 -*-

;; Copyright (C) 2026 Free Software Foundation, Inc.

;; This file is part of GNU Emacs.

;; GNU Emacs is free software: you can redistribute it and/or modify
;; it under the terms of the GNU General Public License as published by
;; the Free Software Foundation, either version 3 of the License, or
;; (at your option) any later version.

;; GNU Emacs is distributed in the hope that it will be useful,
;; but WITHOUT ANY WARRANTY; without even the implied warranty of
;; MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
;; GNU General Public License for more details.

;; You should have received a copy of the GNU General Public License
;; along with GNU Emacs.  If not, see <https://www.gnu.org/licenses/>.

;;; Commentary:

;; Machine-readable inventory of components whose primary development
;; happens outside this repository, plus components that are vendored
;; (copied) in from upstream projects.
;;
;; Read with:
;;
;;   (with-temp-buffer
;;     (insert-file-contents "admin/external-packages.eld")
;;     (read (current-buffer)))
;;
;; Schema: a top-level list of plists.  Recognized keys:
;;
;;   :name        string  -- short identifier, kebab-case
;;   :kind        symbol  -- one of
;;       external-lisp         externally-developed Lisp package
;;       elpa-core             Lisp package marked ";; GNU ELPA :core"
;;       vendored-c            C source copied in from upstream
;;       vendored-data         text data files
;;       vendored-schema       XML / RELAX-NG schemas
;;       vendored-assets       images / icons
;;       vendored-test-data    test fixtures from upstream
;;       vendored-build-aux    autoconf / texinfo helpers
;;   :paths       list of strings -- repo-relative paths or globs
;;   :upstream    string or nil   -- canonical upstream URL
;;   :sync        symbol or string -- how it enters the tree
;;       upstream-to-emacs     manual or scripted import
;;       emacs-to-elpa         Emacs is source of truth; ELPA mirrors
;;       bidirectional         dual-maintained
;;       STRING                name of the sync script
;;   :elpa        symbol or nil   -- :core | gnu | nongnu | nil
;;   :license     string or nil   -- SPDX-ish short tag
;;   :maintainer  string or nil   -- only when listed in admin/MAINTAINERS
;;   :notes       string or nil   -- free-form
;;
;; The canonical list of externally-maintained Lisp packages is in
;; admin/MAINTAINERS section 3; entries marked with :maintainer below
;; cross-reference that list.

;;; Code:

((:name "cc-mode"
  :kind external-lisp
  :paths ("lisp/progmodes/cc-*.el")
  :upstream "https://hg.savannah.nongnu.org/hgweb/cc-mode/"
  :sync upstream-to-emacs
  :maintainer "Alan Mackenzie"
  :notes "admin/MAINTAINERS §3.  Bug reports: bug-cc-mode@gnu.org.")

 (:name "modus-themes"
  :kind external-lisp
  :paths ("etc/themes/modus-themes.el"
          "etc/themes/modus-operandi-theme.el"
          "etc/themes/modus-operandi-tinted-theme.el"
          "etc/themes/modus-operandi-deuteranopia-theme.el"
          "etc/themes/modus-operandi-tritanopia-theme.el"
          "etc/themes/modus-vivendi-theme.el"
          "etc/themes/modus-vivendi-tinted-theme.el"
          "etc/themes/modus-vivendi-deuteranopia-theme.el"
          "etc/themes/modus-vivendi-tritanopia-theme.el"
          "doc/misc/modus-themes.org")
  :upstream "https://github.com/protesilaos/modus-themes"
  :sync upstream-to-emacs
  :maintainer "Protesilaos Stavrou"
  :notes "admin/MAINTAINERS §3.")

 (:name "org"
  :kind external-lisp
  :paths ("lisp/org/*.el"
          "etc/org/"
          "etc/refcards/orgcard.tex"
          "doc/misc/org.org"
          "doc/misc/org-setup.org")
  :upstream "https://git.savannah.gnu.org/git/emacs/org-mode.git"
  :sync upstream-to-emacs
  :maintainer "Org Mode developers"
  :notes "admin/MAINTAINERS §3.  Periodically merged from the separate\
 project at https://orgmode.org/.  Bug reports: M-x org-submit-bug-report.")

 (:name "tramp"
  :kind external-lisp
  :paths ("lisp/net/tramp*.el"
          "doc/misc/tramp*.texi"
          "test/lisp/net/tramp*-tests.el")
  :upstream "https://git.savannah.gnu.org/git/tramp.git"
  :sync bidirectional
  :elpa gnu
  :maintainer "Michael Albinus"
  :notes "admin/MAINTAINERS §3.  Released as a GNU ELPA package with\
 its own release cycle; see lisp/net/trampver.el for backward-\
compatibility requirements.  Bug reports: M-x tramp-bug.")

 (:name "transient"
  :kind external-lisp
  :paths ("lisp/transient.el"
          "doc/misc/transient.texi")
  :upstream "https://github.com/magit/transient"
  :sync upstream-to-emacs
  :maintainer "Jonas Bernoulli"
  :notes "admin/MAINTAINERS §3.")

 ;; -- Lisp packages with external upstream, also released as
 ;;    GNU ELPA :core packages.  Not in admin/MAINTAINERS §3.

 (:name "eglot"
  :kind elpa-core
  :paths ("lisp/progmodes/eglot.el")
  :upstream "https://github.com/joaotavora/eglot"
  :sync upstream-to-emacs
  :elpa :core)

 (:name "use-package"
  :kind elpa-core
  :paths ("lisp/use-package/use-package.el"
          "lisp/use-package/use-package-core.el"
          "lisp/use-package/use-package-bind-key.el"
          "lisp/use-package/use-package-delight.el"
          "lisp/use-package/use-package-diminish.el"
          "lisp/use-package/use-package-ensure.el"
          "lisp/use-package/use-package-ensure-system-package.el"
          "lisp/use-package/use-package-jump.el"
          "lisp/use-package/use-package-lint.el")
  :upstream "https://github.com/jwiegley/use-package"
  :sync upstream-to-emacs
  :elpa :core)

 (:name "bind-key"
  :kind elpa-core
  :paths ("lisp/bind-key.el")
  :upstream "https://github.com/jwiegley/use-package"
  :sync upstream-to-emacs
  :elpa :core
  :notes "Part of the use-package project upstream.")

 (:name "soap-client"
  :kind elpa-core
  :paths ("lisp/net/soap-client.el"
          "lisp/net/soap-inspect.el")
  :upstream "https://github.com/alex-hhh/emacs-soap-client"
  :sync upstream-to-emacs
  :elpa :core)

 (:name "window-tool-bar"
  :kind elpa-core
  :paths ("lisp/window-tool-bar.el")
  :upstream "http://github.com/chaosemer/window-tool-bar"
  :sync upstream-to-emacs
  :elpa :core)

 ;; -- Lisp packages with external upstream, released to ELPA but
 ;;    NOT marked ":core" in their header.

 (:name "editorconfig"
  :kind external-lisp
  :paths ("lisp/editorconfig.el"
          "lisp/editorconfig-conf-mode.el"
          "lisp/editorconfig-core.el"
          "lisp/editorconfig-core-handle.el"
          "lisp/editorconfig-fnmatch.el"
          "lisp/editorconfig-tools.el")
  :upstream "https://github.com/editorconfig/editorconfig-emacs"
  :sync upstream-to-emacs
  :elpa gnu)

 (:name "compat"
  :kind external-lisp
  :paths ("lisp/emacs-lisp/compat.el")
  :upstream "https://github.com/emacs-compat/compat"
  :sync upstream-to-emacs
  :elpa gnu
  :notes "In-tree file is a stub; full package lives on GNU ELPA.")

 (:name "timeout"
  :kind external-lisp
  :paths ("lisp/emacs-lisp/timeout.el")
  :upstream "https://github.com/karthink/timeout"
  :sync upstream-to-emacs
  :elpa gnu)

 (:name "faceup"
  :kind external-lisp
  :paths ("lisp/emacs-lisp/faceup.el")
  :upstream "https://github.com/Lindydancer/faceup"
  :sync upstream-to-emacs
  :elpa gnu)

 (:name "so-long"
  :kind external-lisp
  :paths ("lisp/so-long.el")
  :upstream "https://savannah.nongnu.org/projects/so-long"
  :sync upstream-to-emacs
  :elpa gnu)

 (:name "verilog-mode"
  :kind external-lisp
  :paths ("lisp/progmodes/verilog-mode.el")
  :upstream "https://www.veripool.org"
  :sync upstream-to-emacs)

 (:name "vhdl-mode"
  :kind external-lisp
  :paths ("lisp/progmodes/vhdl-mode.el")
  :upstream "https://iis-people.ee.ethz.ch/~zimmi/emacs/vhdl-mode.html"
  :sync upstream-to-emacs)

 (:name "newsticker"
  :kind external-lisp
  :paths ("lisp/net/newsticker.el"
          "lisp/net/newst-*.el")
  :upstream "https://www.nongnu.org/newsticker"
  :sync upstream-to-emacs
  :elpa nongnu)

 (:name "reftex"
  :kind external-lisp
  :paths ("lisp/textmodes/reftex.el"
          "lisp/textmodes/reftex-auc.el"
          "lisp/textmodes/reftex-cite.el"
          "lisp/textmodes/reftex-dcr.el"
          "lisp/textmodes/reftex-global.el"
          "lisp/textmodes/reftex-index.el"
          "lisp/textmodes/reftex-parse.el"
          "lisp/textmodes/reftex-ref.el"
          "lisp/textmodes/reftex-sel.el"
          "lisp/textmodes/reftex-toc.el"
          "lisp/textmodes/reftex-vars.el")
  :upstream "https://www.gnu.org/software/auctex/reftex.html"
  :sync upstream-to-emacs
  :notes "Maintained by the AUCTeX team (auctex-devel@gnu.org).")

 (:name "erc-status-sidebar"
  :kind external-lisp
  :paths ("lisp/erc/erc-status-sidebar.el")
  :upstream "https://github.com/drewbarbs/erc-status-sidebar"
  :sync upstream-to-emacs
  :notes "Bundled with ERC but originally an external contribution.")

 ;; -- GNU ELPA :core packages whose primary development is in this
 ;;    tree; ELPA mirrors releases triggered by ;; Version: bumps.

 (:name "flymake"
  :kind elpa-core
  :paths ("lisp/progmodes/flymake.el")
  :upstream nil
  :sync emacs-to-elpa
  :elpa :core)

 (:name "project"
  :kind elpa-core
  :paths ("lisp/progmodes/project.el")
  :upstream nil
  :sync emacs-to-elpa
  :elpa :core)

 (:name "xref"
  :kind elpa-core
  :paths ("lisp/progmodes/xref.el")
  :upstream nil
  :sync emacs-to-elpa
  :elpa :core)

 (:name "python"
  :kind elpa-core
  :paths ("lisp/progmodes/python.el")
  :upstream "https://github.com/fgallina/python.el"
  :sync emacs-to-elpa
  :elpa :core
  :notes "Header URL points to historical upstream; current maintainer\
 is emacs-devel@gnu.org.")

 (:name "jsonrpc"
  :kind elpa-core
  :paths ("lisp/jsonrpc.el")
  :upstream nil
  :sync emacs-to-elpa
  :elpa :core
  :notes "Originally extracted from eglot.el.")

 (:name "external-completion"
  :kind elpa-core
  :paths ("lisp/external-completion.el")
  :upstream nil
  :sync emacs-to-elpa
  :elpa :core
  :maintainer "João Távora")

 (:name "eldoc"
  :kind elpa-core
  :paths ("lisp/emacs-lisp/eldoc.el")
  :upstream nil
  :sync emacs-to-elpa
  :elpa :core)

 (:name "let-alist"
  :kind elpa-core
  :paths ("lisp/emacs-lisp/let-alist.el")
  :upstream nil
  :sync emacs-to-elpa
  :elpa :core)

 (:name "map"
  :kind elpa-core
  :paths ("lisp/emacs-lisp/map.el")
  :upstream nil
  :sync emacs-to-elpa
  :elpa :core)

 (:name "cond-star"
  :kind elpa-core
  :paths ("lisp/emacs-lisp/cond-star.el")
  :upstream nil
  :sync emacs-to-elpa
  :elpa :core)

 (:name "svg"
  :kind elpa-core
  :paths ("lisp/svg.el")
  :upstream nil
  :sync emacs-to-elpa
  :elpa :core)

 (:name "ntlm"
  :kind elpa-core
  :paths ("lisp/net/ntlm.el")
  :upstream nil
  :sync emacs-to-elpa
  :elpa :core)

 (:name "erc"
  :kind elpa-core
  :paths ("lisp/erc/erc.el"
          "lisp/erc/erc-*.el")
  :upstream "https://www.gnu.org/software/emacs/erc.html"
  :sync emacs-to-elpa
  :elpa :core
  :notes "See erc-status-sidebar entry for an external-upstream submodule.")

 ;; -- Vendored non-Lisp dependencies.

 (:name "gnulib"
  :kind vendored-c
  :paths ("lib/" "m4/" "build-aux/")
  :upstream "https://git.savannah.gnu.org/git/gnulib.git"
  :sync "admin/merge-gnulib"
  :license nil
  :notes "GNU portability library, imported via gnulib-tool.  Module\
 license varies (LGPL-2.1-or-later or GPL-3.0-or-later); see\
 lib/COPYING and per-module headers.")

 (:name "unicode-character-database"
  :kind vendored-data
  :paths ("admin/unidata/")
  :upstream "https://www.unicode.org/Public/UNIDATA/"
  :sync upstream-to-emacs
  :license "Unicode-TOU"
  :notes "Source files for character properties, normalization,\
 emoji, bidi, IVD, IDNA mapping, and confusables tables.  See\
 admin/unidata/README and admin/unidata/copyright.html.")

 (:name "publicsuffix-list"
  :kind vendored-data
  :paths ("etc/publicsuffix.txt")
  :upstream "https://publicsuffix.org/list/public_suffix_list.dat"
  :sync upstream-to-emacs
  :license "MPL-2.0"
  :notes "Consumed by lisp/url/url-domsuf.el.")

 (:name "x11-rgb"
  :kind vendored-data
  :paths ("etc/rgb.txt")
  :upstream nil
  :sync upstream-to-emacs
  :license "X11"
  :notes "X11R6 X Consortium rgb.txt; supports color-name lookup on\
 Windows.  File header states it is not a part of GNU Emacs.")

 (:name "charset-mappings"
  :kind vendored-data
  :paths ("admin/charsets/mapfiles/"
          "etc/charsets/")
  :upstream nil
  :sync upstream-to-emacs
  :notes "Per-encoding mapping tables imported from unicode.org,\
 iana.org, Adobe, SourceForge kanji-database, and Wikipedia.  See\
 admin/charsets/mapfiles/README for per-file provenance.  Files under\
 etc/charsets/ are generated from these by admin/charsets/ scripts.")

 (:name "xml-schemas"
  :kind vendored-schema
  :paths ("etc/schema/")
  :upstream nil
  :sync upstream-to-emacs
  :notes "RELAX-NG schemas for DocBook, XHTML, XSLT, RDF/XML, OASIS\
 OpenDocument, and Microsoft .NET project files.  Provenance per-file\
 in etc/schema/README.")

 (:name "unicode-bidi-test-data"
  :kind vendored-test-data
  :paths ("test/manual/BidiCharacterTest.txt")
  :upstream "https://www.unicode.org/Public/UCD/latest/ucd/BidiCharacterTest.txt"
  :sync upstream-to-emacs
  :license "Unicode-TOU")

 (:name "unicode-idna-test-data"
  :kind vendored-test-data
  :paths ("test/lisp/net/puny-resources/IdnaTestV2.txt")
  :upstream "https://www.unicode.org/reports/tr46/"
  :sync upstream-to-emacs
  :license "Unicode-TOU")

 (:name "insight-debugger-icons"
  :kind vendored-assets
  :paths ("etc/images/gud/")
  :upstream "https://sourceware.org/insight/"
  :sync upstream-to-emacs
  :license "GPL-3.0-or-later"
  :notes "Adapted from Red Hat Insight Debugger icons; copyright\
 assigned to FSF.")

 (:name "gnome-icons"
  :kind vendored-assets
  :paths ("etc/images/")
  :upstream nil
  :sync upstream-to-emacs
  :license "GPL-2.0-or-later"
  :notes "Selected icons from the GNOME 2.x icon theme.  See\
 etc/images/README for the full list.")

 (:name "gtk-icons"
  :kind vendored-assets
  :paths ("etc/images/")
  :upstream nil
  :sync upstream-to-emacs
  :license "LGPL-2.0-or-later"
  :notes "Selected icons from the GTK+ 2.x toolkit.  See\
 etc/images/README for the full list."))

;;; external-packages.eld ends here
