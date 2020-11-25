with import <nixpkgs>{};
let
  poetry2nix = pkgs.callPackage ./poetry2nix.nix {};
in mkShell {
  buildInputs = [ poetry2nix.cli ];
}
