{ pkgs ? import ./nixpkgs.nix {} }:
let
  poetry2nix = pkgs.callPackage ../../pkgs/poetry2nix.nix {};
  processor-trace = pkgs.callPackage ../../pkgs/processor-trace.nix {};
  env = poetry2nix.mkPoetryEnv {
    projectDir = ./.;
    overrides = [
      poetry2nix.defaultPoetryOverrides
      (import ../../pkgs/poetry-git-overlay.nix { inherit pkgs; })
      (self: super: {
        tracedump = super.tracedump.overrideAttrs (old: {
          buildInputs = [
            processor-trace
          ];
        });
      })
    ];
  };
in pkgs.mkShell {
  buildInputs = [ env ];
}
