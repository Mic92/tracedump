{ pkgs, callPackage, fetchzip }:
callPackage (fetchzip {
  url = "https://github.com/Mic92/poetry2nix/archive/81948c55049c5f3716d0eea1e288eaaf4e50cdbd.tar.gz";
  sha256 = "1jsn6c1y6iagrrigzl8p6yknknkxaldb5cz2r3g8ldvgq8ykwhnl";
}) {
  inherit pkgs;
}
