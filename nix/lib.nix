# Convenience wrappers over emacs-overlay's package-set machinery, scoped to
# the local Emacs build.  Exposed as the flake's `lib`.
{ emacs-overlay }:

{
  emacsPackagesFor = pkgs: emacs: pkgs.emacsPackagesFor emacs;

  withPackages =
    pkgs: emacs: packagesFn:
    (pkgs.emacsPackagesFor emacs).emacsWithPackages packagesFn;

  emacsWithPackagesFromUsePackage =
    pkgs: args:
    emacs-overlay.lib.${pkgs.system}.emacsWithPackagesFromUsePackage (
      { package = pkgs.emacs-jylhis; } // args
    );
}
