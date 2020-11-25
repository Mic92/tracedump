{ pkgs ? import <nixpkgs> {}
, python ? pkgs.python3
, cmake ? pkgs.cmake
, stdenv ? pkgs.stdenv
, fetchFromGitHub ? pkgs.fetchFromGitHub
, fetchzip ? pkgs.fetchzip
, callPackage ? pkgs.callPackage
}:

let
  poetry2nix = pkgs.callPackage ./pkgs/poetry2nix.nix {};
  processor-trace = pkgs.callPackage ./pkgs/processor-trace.nix {};
in poetry2nix.mkPoetryApplication {
  projectDir = ./.;
  inherit python;
  buildInputs = [
    processor-trace
  ];
  overrides = [
    (import ./pkgs/poetry-git-overlay.nix { inherit pkgs; })
    poetry2nix.defaultPoetryOverrides
  ];
}
