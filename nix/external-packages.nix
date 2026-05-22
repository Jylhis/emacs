# nix/external-packages.nix --- inventory of externally-developed code
#
# Single source of truth for components whose primary development lives
# outside this repository and that we either currently vendor in the tree
# (and want to stop versioning here) or already fetch from upstream.
#
# Consumed by nix/external-sources.nix to materialize a flat staging
# directory; that directory is passed into the Meson build via
# -D external-sources-dir=... and copied into the source tree by
# meson/stage_external_packages.py.
#
# Schema (per attribute):
#   kind         "external-lisp" | "elpa-core" | "vendored-c"
#              | "vendored-data" | "vendored-schema"
#              | "vendored-test-data" | "vendored-assets"
#              | "vendored-build-aux"
#   upstream     canonical upstream URL, or null
#   paths        repo-relative paths (or globs) currently occupied
#                in the source tree
#   sync         "upstream-to-emacs" | "emacs-to-elpa"
#              | "bidirectional"
#   elpa         "core" | "gnu" | "nongnu" | null
#   license      SPDX-style short tag, or null
#   maintainer   set only when the package is listed in
#                admin/MAINTAINERS section 3
#   notes        free-form
#   src          fetched derivation (added per-package as each
#                package migrates off the in-tree copy; null
#                until then so the inventory remains complete)
#   destination  destination subdir/file in the Emacs source tree,
#                used by the staging step (null until src is set)
#   files        optional include glob list within src
#   modules      gnulib-only: list of gnulib module names imported
#                via gnulib-tool
#
# Function form: consumers pass `pkgs` so `src` slots can use
# `pkgs.fetchFromGitHub`, `pkgs.fetchurl`, etc.
#
# Drift policy.  When an external Lisp package is merged into the Emacs
# tree, the Emacs maintainers "Emacs-ify" it -- the file's license
# header is rewritten ("This file is part of GNU Emacs"), copyright is
# reassigned to the FSF, Package-Requires entries are normalised
# against in-tree library versions, and assorted small textual edits
# are applied.  Re-fetching upstream verbatim would silently undo all
# of that.  Therefore `src` stays null for Lisp packages even where an
# active upstream exists; the inventory tracks provenance only.  Data
# files (publicsuffix list, Unicode UCD, test fixtures, ...) are not
# Emacs-ified and so are safe to fetch live.
_:
# Phase 5+ entries reference `pkgs.fetchurl`, `pkgs.fetchzip`, etc.
# directly at the point of use; no `inherit` here keeps the lint
# clean while no fetchers are wired.
{
  ## =====================================================================
  ## Lisp packages listed in admin/MAINTAINERS section 3 (externally
  ## maintained as separate projects, merged in periodically).
  ## =====================================================================

  cc-mode = {
    kind = "external-lisp";
    upstream = "https://hg.savannah.nongnu.org/hgweb/cc-mode/";
    paths = [ "lisp/progmodes/cc-*.el" ];
    sync = "upstream-to-emacs";
    elpa = null;
    license = null;
    maintainer = "Alan Mackenzie";
    notes = ''
      admin/MAINTAINERS section 3.  Bug reports: bug-cc-mode@gnu.org.
      In-tree v5.35.2 carries the Emacs-ified license header.
      See "Drift policy" in the file header.  No src fetcher.
    '';
    src = null;
    destination = null;
  };

  modus-themes = {
    kind = "external-lisp";
    upstream = "https://github.com/protesilaos/modus-themes";
    paths = [
      "etc/themes/modus-themes.el"
      "etc/themes/modus-operandi-theme.el"
      "etc/themes/modus-operandi-tinted-theme.el"
      "etc/themes/modus-operandi-deuteranopia-theme.el"
      "etc/themes/modus-operandi-tritanopia-theme.el"
      "etc/themes/modus-vivendi-theme.el"
      "etc/themes/modus-vivendi-tinted-theme.el"
      "etc/themes/modus-vivendi-deuteranopia-theme.el"
      "etc/themes/modus-vivendi-tritanopia-theme.el"
      "doc/misc/modus-themes.org"
    ];
    sync = "upstream-to-emacs";
    elpa = null;
    license = null;
    maintainer = "Protesilaos Stavrou";
    notes = ''
      admin/MAINTAINERS section 3.  In-tree matches upstream 5.2.0
      modulo Emacs-side edits (copyright reassignment, a typo fix,
      and a comment-block rewrite around `completion-preview' face
      inheritance).  See "Drift policy" in the file header --
      no src fetcher.
    '';
    src = null;
    destination = null;
  };

  org = {
    kind = "external-lisp";
    upstream = "https://git.savannah.gnu.org/git/emacs/org-mode.git";
    paths = [
      "lisp/org/*.el"
      "etc/org/"
      "etc/refcards/orgcard.tex"
      "doc/misc/org.org"
      "doc/misc/org-setup.org"
    ];
    sync = "upstream-to-emacs";
    elpa = null;
    license = null;
    maintainer = "Org Mode developers";
    notes = ''
      admin/MAINTAINERS section 3.  Periodically merged from the
      separate project at https://orgmode.org/.
      Bug reports: M-x org-submit-bug-report.
      In-tree v9.8.3 carries the Emacs-ified license header; the
      upstream tree is multi-file (~130 .el under lisp/org) and the
      merge process applies systematic edits.  See "Drift policy"
      in the file header.  No src fetcher.
    '';
    src = null;
    destination = null;
  };

  tramp = {
    kind = "external-lisp";
    upstream = "https://git.savannah.gnu.org/git/tramp.git";
    paths = [
      "lisp/net/tramp*.el"
      "doc/misc/tramp*.texi"
      "test/lisp/net/tramp*-tests.el"
    ];
    sync = "bidirectional";
    elpa = "gnu";
    license = null;
    maintainer = "Michael Albinus";
    notes = ''
      admin/MAINTAINERS section 3.  Released as a GNU ELPA package with
      its own release cycle; see lisp/net/trampver.el for backward-
      compatibility requirements.  Bug reports: M-x tramp-bug.
      In-tree files (lisp/net/tramp*.el, doc/misc/tramp*.texi,
      test/lisp/net/tramp*-tests.el) carry the Emacs-ified license
      header.  See "Drift policy" in the file header.  No src
      fetcher.
    '';
    src = null;
    destination = null;
  };

  transient = {
    kind = "external-lisp";
    upstream = "https://github.com/magit/transient";
    paths = [
      "lisp/transient.el"
      "doc/misc/transient.texi"
    ];
    sync = "upstream-to-emacs";
    elpa = null;
    license = null;
    maintainer = "Jonas Bernoulli";
    notes = ''
      admin/MAINTAINERS section 3.  In-tree v0.13.3 carries the
      Emacs-ified license header.  See "Drift policy" in the file
      header.  No src fetcher.
    '';
    src = null;
    destination = null;
  };

  ## =====================================================================
  ## Externally-upstream Lisp packages also released as GNU ELPA :core.
  ## Not in admin/MAINTAINERS section 3.
  ## =====================================================================

  eglot = {
    kind = "elpa-core";
    upstream = "https://github.com/joaotavora/eglot";
    paths = [ "lisp/progmodes/eglot.el" ];
    # GitHub repo declares ;; Version: 1.21 on master while the in-tree
    # copy is ahead at ;; Version: 1.23; emacs.git is now upstream and
    # ELPA mirrors from here.  Leave src = null permanently.
    sync = "emacs-to-elpa";
    elpa = "core";
    license = null;
    notes = ''
      Header URL points to the historical upstream
      (github.com/joaotavora/eglot) but emacs.git has been the
      effective upstream since at least the 1.22 bump; that repo's
      master branch trails the in-tree file.  No src fetcher.
    '';
    src = null;
    destination = null;
  };

  use-package = {
    kind = "elpa-core";
    upstream = "https://github.com/jwiegley/use-package";
    paths = [
      "lisp/use-package/use-package.el"
      "lisp/use-package/use-package-core.el"
      "lisp/use-package/use-package-bind-key.el"
      "lisp/use-package/use-package-delight.el"
      "lisp/use-package/use-package-diminish.el"
      "lisp/use-package/use-package-ensure.el"
      "lisp/use-package/use-package-ensure-system-package.el"
      "lisp/use-package/use-package-jump.el"
      "lisp/use-package/use-package-lint.el"
    ];
    # github.com/jwiegley/use-package was archived 2025-08-23 at
    # ;; Version: 2.4.4; in-tree is 2.4.6, maintained in emacs.git.
    sync = "emacs-to-elpa";
    elpa = "core";
    license = null;
    notes = ''
      Upstream repo jwiegley/use-package was archived 2025-08-23.
      Header URL kept for historical attribution; emacs.git is the
      effective upstream.  No src fetcher.
    '';
    src = null;
    destination = null;
  };

  bind-key = {
    kind = "elpa-core";
    upstream = "https://github.com/jwiegley/use-package";
    paths = [ "lisp/bind-key.el" ];
    sync = "emacs-to-elpa";
    elpa = "core";
    license = null;
    notes = ''
      Shipped with the use-package project upstream, which was
      archived 2025-08-23.  emacs.git is the effective upstream.
      No src fetcher.
    '';
    src = null;
    destination = null;
  };

  soap-client = {
    kind = "elpa-core";
    upstream = "https://github.com/alex-hhh/emacs-soap-client";
    paths = [
      "lisp/net/soap-client.el"
      "lisp/net/soap-inspect.el"
    ];
    # alex-hhh/emacs-soap-client was archived 2018-06-17 at
    # ;; Version: 3.1.4; in-tree is 3.2.3, maintained in emacs.git.
    sync = "emacs-to-elpa";
    elpa = "core";
    license = null;
    notes = ''
      Upstream repo alex-hhh/emacs-soap-client was archived
      2018-06-17.  emacs.git is the effective upstream.  No src
      fetcher.
    '';
    src = null;
    destination = null;
  };

  window-tool-bar = {
    kind = "elpa-core";
    upstream = "https://github.com/chaosemer/window-tool-bar";
    paths = [ "lisp/window-tool-bar.el" ];
    sync = "upstream-to-emacs";
    elpa = "core";
    license = null;
    notes = ''
      In-tree matches upstream v0.3 modulo Emacs-side edits; see
      "Drift policy" in the file header.  No src fetcher.
    '';
    src = null;
    destination = null;
  };

  ## =====================================================================
  ## Externally-upstream Lisp packages released to ELPA but NOT marked
  ## ":core" in their header.
  ## =====================================================================

  editorconfig = {
    kind = "external-lisp";
    upstream = "https://github.com/editorconfig/editorconfig-emacs";
    paths = [
      "lisp/editorconfig.el"
      "lisp/editorconfig-conf-mode.el"
      "lisp/editorconfig-core.el"
      "lisp/editorconfig-core-handle.el"
      "lisp/editorconfig-fnmatch.el"
      "lisp/editorconfig-tools.el"
    ];
    sync = "upstream-to-emacs";
    elpa = "gnu";
    license = null;
    notes = ''
      In-tree matches upstream v0.11.0 modulo Emacs-ification (license
      header rewrite, FSF copyright assignment, Package-Requires
      adjustments).  See "Drift policy" in the file header.  No src
      fetcher.
    '';
    src = null;
    destination = null;
  };

  compat = {
    kind = "external-lisp";
    upstream = "https://github.com/emacs-compat/compat";
    paths = [ "lisp/emacs-lisp/compat.el" ];
    sync = "upstream-to-emacs";
    elpa = "gnu";
    license = null;
    notes = ''
      In-tree file is a documented stub of the Compatibility Library;
      the full package lives on GNU ELPA.  Replacing the stub would
      require evaluating the runtime resolution policy and is out of
      scope.  No src fetcher.
    '';
    src = null;
    destination = null;
  };

  timeout = {
    kind = "external-lisp";
    upstream = "https://github.com/karthink/timeout";
    paths = [ "lisp/emacs-lisp/timeout.el" ];
    sync = "upstream-to-emacs";
    elpa = "gnu";
    license = null;
    notes = ''
      In-tree matches upstream v2.1.6 modulo Emacs-ification; see
      "Drift policy" in the file header.  No src fetcher.
    '';
    src = null;
    destination = null;
  };

  faceup = {
    kind = "external-lisp";
    upstream = "https://github.com/Lindydancer/faceup";
    paths = [ "lisp/emacs-lisp/faceup.el" ];
    sync = "upstream-to-emacs";
    elpa = "gnu";
    license = null;
    notes = ''
      Upstream is dormant (last commit 2017-09-25 on master, tagged
      version 0.0.5).  In-tree version is 0.0.6 with an Emacs-ified
      license header and dropped cl require -- Emacs.git has been
      the de facto upstream since the original ingestion.  No src
      fetcher.
    '';
    src = null;
    destination = null;
  };

  so-long = {
    kind = "external-lisp";
    upstream = "https://savannah.nongnu.org/projects/so-long";
    paths = [ "lisp/so-long.el" ];
    sync = "upstream-to-emacs";
    elpa = "gnu";
    license = null;
    notes = ''
      In-tree v1.1.2 carries the Emacs-ified license header
      ("GNU Emacs is free software ...") so does not match the
      upstream tarball verbatim; see "Drift policy" in the file
      header.  No src fetcher.
    '';
    src = null;
    destination = null;
  };

  verilog-mode = {
    kind = "external-lisp";
    upstream = "https://www.veripool.org";
    paths = [ "lisp/progmodes/verilog-mode.el" ];
    sync = "upstream-to-emacs";
    elpa = null;
    license = null;
    notes = ''
      Upstream releases as a date-stamped version (currently
      2026.01.18.088738971); in-tree carries the Emacs-ified license
      header.  See "Drift policy" in the file header.  No src
      fetcher.
    '';
    src = null;
    destination = null;
  };

  vhdl-mode = {
    kind = "external-lisp";
    upstream = "https://iis-people.ee.ethz.ch/~zimmi/emacs/vhdl-mode.html";
    paths = [ "lisp/progmodes/vhdl-mode.el" ];
    sync = "upstream-to-emacs";
    elpa = null;
    license = null;
    notes = ''
      Upstream ships as a per-release tarball at the ETH project
      page; in-tree carries the Emacs-ified license header.  See
      "Drift policy" in the file header.  No src fetcher.
    '';
    src = null;
    destination = null;
  };

  newsticker = {
    kind = "external-lisp";
    upstream = "https://www.nongnu.org/newsticker";
    paths = [
      "lisp/net/newsticker.el"
      "lisp/net/newst-*.el"
    ];
    # The www.nongnu.org/newsticker page is the historical project
    # home; there is no separate maintained git tree distinct from
    # emacs.git, and the in-tree file declares "This file is part of
    # GNU Emacs".  Treat as emacs-upstream.
    sync = "emacs-to-elpa";
    elpa = "nongnu";
    license = null;
    notes = ''
      The nongnu.org URL is a project page; there is no separate
      upstream repository.  emacs.git is the effective upstream.
      No src fetcher.
    '';
    src = null;
    destination = null;
  };

  reftex = {
    kind = "external-lisp";
    upstream = "https://www.gnu.org/software/auctex/reftex.html";
    paths = [
      "lisp/textmodes/reftex.el"
      "lisp/textmodes/reftex-auc.el"
      "lisp/textmodes/reftex-cite.el"
      "lisp/textmodes/reftex-dcr.el"
      "lisp/textmodes/reftex-global.el"
      "lisp/textmodes/reftex-index.el"
      "lisp/textmodes/reftex-parse.el"
      "lisp/textmodes/reftex-ref.el"
      "lisp/textmodes/reftex-sel.el"
      "lisp/textmodes/reftex-toc.el"
      "lisp/textmodes/reftex-vars.el"
    ];
    sync = "upstream-to-emacs";
    elpa = null;
    license = null;
    notes = ''
      Maintained by the AUCTeX team (auctex-devel@gnu.org).
      In-tree files carry the Emacs-ified license header.  See
      "Drift policy" in the file header.  No src fetcher.
    '';
    src = null;
    destination = null;
  };

  erc-status-sidebar = {
    kind = "external-lisp";
    upstream = "https://github.com/drewbarbs/erc-status-sidebar";
    paths = [ "lisp/erc/erc-status-sidebar.el" ];
    sync = "upstream-to-emacs";
    elpa = null;
    license = null;
    notes = ''
      Bundled with ERC but originally an external contribution.
      In-tree carries the Emacs-ified license header.  See
      "Drift policy" in the file header.  No src fetcher.
    '';
    src = null;
    destination = null;
  };

  ## =====================================================================
  ## GNU ELPA :core packages whose primary development is in this tree;
  ## ELPA mirrors releases triggered by ;; Version: bumps.  Listed here
  ## for inventory completeness; they are NOT removed by this work since
  ## Emacs is upstream.
  ## =====================================================================

  flymake = {
    kind = "elpa-core";
    upstream = null;
    paths = [ "lisp/progmodes/flymake.el" ];
    sync = "emacs-to-elpa";
    elpa = "core";
    license = null;
    src = null;
    destination = null;
  };

  project = {
    kind = "elpa-core";
    upstream = null;
    paths = [ "lisp/progmodes/project.el" ];
    sync = "emacs-to-elpa";
    elpa = "core";
    license = null;
    src = null;
    destination = null;
  };

  xref = {
    kind = "elpa-core";
    upstream = null;
    paths = [ "lisp/progmodes/xref.el" ];
    sync = "emacs-to-elpa";
    elpa = "core";
    license = null;
    src = null;
    destination = null;
  };

  python = {
    kind = "elpa-core";
    upstream = "https://github.com/fgallina/python.el";
    paths = [ "lisp/progmodes/python.el" ];
    sync = "emacs-to-elpa";
    elpa = "core";
    license = null;
    notes = "Header URL points to historical upstream; current maintainer is emacs-devel@gnu.org.";
    src = null;
    destination = null;
  };

  jsonrpc = {
    kind = "elpa-core";
    upstream = null;
    paths = [ "lisp/jsonrpc.el" ];
    sync = "emacs-to-elpa";
    elpa = "core";
    license = null;
    notes = "Originally extracted from eglot.el.";
    src = null;
    destination = null;
  };

  external-completion = {
    kind = "elpa-core";
    upstream = null;
    paths = [ "lisp/external-completion.el" ];
    sync = "emacs-to-elpa";
    elpa = "core";
    license = null;
    maintainer = "João Távora";
    src = null;
    destination = null;
  };

  eldoc = {
    kind = "elpa-core";
    upstream = null;
    paths = [ "lisp/emacs-lisp/eldoc.el" ];
    sync = "emacs-to-elpa";
    elpa = "core";
    license = null;
    src = null;
    destination = null;
  };

  let-alist = {
    kind = "elpa-core";
    upstream = null;
    paths = [ "lisp/emacs-lisp/let-alist.el" ];
    sync = "emacs-to-elpa";
    elpa = "core";
    license = null;
    src = null;
    destination = null;
  };

  map = {
    kind = "elpa-core";
    upstream = null;
    paths = [ "lisp/emacs-lisp/map.el" ];
    sync = "emacs-to-elpa";
    elpa = "core";
    license = null;
    src = null;
    destination = null;
  };

  cond-star = {
    kind = "elpa-core";
    upstream = null;
    paths = [ "lisp/emacs-lisp/cond-star.el" ];
    sync = "emacs-to-elpa";
    elpa = "core";
    license = null;
    src = null;
    destination = null;
  };

  svg = {
    kind = "elpa-core";
    upstream = null;
    paths = [ "lisp/svg.el" ];
    sync = "emacs-to-elpa";
    elpa = "core";
    license = null;
    src = null;
    destination = null;
  };

  ntlm = {
    kind = "elpa-core";
    upstream = null;
    paths = [ "lisp/net/ntlm.el" ];
    sync = "emacs-to-elpa";
    elpa = "core";
    license = null;
    src = null;
    destination = null;
  };

  erc = {
    kind = "elpa-core";
    upstream = "https://www.gnu.org/software/emacs/erc.html";
    paths = [
      "lisp/erc/erc.el"
      "lisp/erc/erc-*.el"
    ];
    sync = "emacs-to-elpa";
    elpa = "core";
    license = null;
    notes = "See erc-status-sidebar entry for an external-upstream submodule.";
    src = null;
    destination = null;
  };

  ## =====================================================================
  ## Vendored non-Lisp dependencies.
  ## =====================================================================

  gnulib = {
    kind = "vendored-c";
    upstream = "https://git.savannah.gnu.org/git/gnulib.git";
    paths = [
      "lib/"
      "m4/"
      "build-aux/"
    ];
    sync = "admin/merge-gnulib";
    elpa = null;
    license = null;
    notes = ''
      GNU portability library, imported via gnulib-tool.  Module
      license varies (LGPL-2.1-or-later or GPL-3.0-or-later); see
      lib/COPYING and per-module headers.  After Phase 7 of the
      removal plan the module list moves here as `modules = [ ... ]`.
    '';
    src = null;
    destination = null;
    modules = [ ];
  };

  unicode-character-database = {
    kind = "vendored-data";
    upstream = "https://www.unicode.org/Public/UNIDATA/";
    paths = [ "admin/unidata/" ];
    sync = "upstream-to-emacs";
    elpa = null;
    license = "Unicode-TOU";
    notes = ''
      Source files for character properties, normalization, emoji,
      bidi, IVD, IDNA mapping, and confusables tables.  See
      admin/unidata/README and admin/unidata/copyright.html.
    '';
    src = null;
    destination = null;
  };

  publicsuffix-list = {
    kind = "vendored-data";
    upstream = "https://publicsuffix.org/list/public_suffix_list.dat";
    paths = [ "etc/publicsuffix.txt" ];
    sync = "upstream-to-emacs";
    elpa = null;
    license = "MPL-2.0";
    notes = "Consumed by lisp/url/url-domsuf.el.";
    src = null;
    destination = null;
  };

  x11-rgb = {
    kind = "vendored-data";
    upstream = null;
    paths = [ "etc/rgb.txt" ];
    sync = "upstream-to-emacs";
    elpa = null;
    license = "X11";
    notes = ''
      X11R6 X Consortium rgb.txt; supports color-name lookup on
      Windows.  File header states it is not a part of GNU Emacs.
    '';
    src = null;
    destination = null;
  };

  charset-mappings = {
    kind = "vendored-data";
    upstream = null;
    paths = [
      "admin/charsets/mapfiles/"
      "etc/charsets/"
    ];
    sync = "upstream-to-emacs";
    elpa = null;
    license = null;
    notes = ''
      Per-encoding mapping tables imported from unicode.org,
      iana.org, Adobe, SourceForge kanji-database, and Wikipedia.
      See admin/charsets/mapfiles/README for per-file provenance.
      Files under etc/charsets/ are generated from these by
      admin/charsets/ scripts.
    '';
    src = null;
    destination = null;
  };

  xml-schemas = {
    kind = "vendored-schema";
    upstream = null;
    paths = [ "etc/schema/" ];
    sync = "upstream-to-emacs";
    elpa = null;
    license = null;
    notes = ''
      RELAX-NG schemas for DocBook, XHTML, XSLT, RDF/XML, OASIS
      OpenDocument, and Microsoft .NET project files.  Provenance
      per-file in etc/schema/README.  Likely split into one entry
      per upstream during Phase 5.
    '';
    src = null;
    destination = null;
  };

  unicode-bidi-test-data = {
    kind = "vendored-test-data";
    upstream = "https://www.unicode.org/Public/UCD/latest/ucd/BidiCharacterTest.txt";
    paths = [ "test/manual/BidiCharacterTest.txt" ];
    sync = "upstream-to-emacs";
    elpa = null;
    license = "Unicode-TOU";
    src = null;
    destination = null;
  };

  unicode-idna-test-data = {
    kind = "vendored-test-data";
    upstream = "https://www.unicode.org/reports/tr46/";
    paths = [ "test/lisp/net/puny-resources/IdnaTestV2.txt" ];
    sync = "upstream-to-emacs";
    elpa = null;
    license = "Unicode-TOU";
    src = null;
    destination = null;
  };

  insight-debugger-icons = {
    kind = "vendored-assets";
    upstream = "https://sourceware.org/insight/";
    paths = [ "etc/images/gud/" ];
    sync = "upstream-to-emacs";
    elpa = null;
    license = "GPL-3.0-or-later";
    notes = ''
      Adapted from Red Hat Insight Debugger icons; copyright
      assigned to FSF.  Upstream is dormant; recommendation is to
      keep these in the tree (see plan §7).
    '';
    src = null;
    destination = null;
  };

  gnome-icons = {
    kind = "vendored-assets";
    upstream = null;
    paths = [ "etc/images/" ];
    sync = "upstream-to-emacs";
    elpa = null;
    license = "GPL-2.0-or-later";
    notes = ''
      Selected icons from the GNOME 2.x icon theme.  See
      etc/images/README for the full list.  Upstream is end-of-life;
      recommendation is to keep these in the tree.
    '';
    src = null;
    destination = null;
  };

  gtk-icons = {
    kind = "vendored-assets";
    upstream = null;
    paths = [ "etc/images/" ];
    sync = "upstream-to-emacs";
    elpa = null;
    license = "LGPL-2.0-or-later";
    notes = ''
      Selected icons from the GTK+ 2.x toolkit.  See
      etc/images/README for the full list.  Upstream is end-of-life;
      recommendation is to keep these in the tree.
    '';
    src = null;
    destination = null;
  };
}
