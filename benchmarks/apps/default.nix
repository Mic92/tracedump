{ pkgs ? import ./nixpkgs.nix {} }:
rec {
  inherit (pkgs) nginx mysql sqlite redis netcat sysbench;
  ycsb = pkgs.callPackage ./ycsb {};
  mysqlDatadir = "/var/lib/mysql";
  buildImage = pkgs.callPackage ./build-image.nix {};
  iotest-image = pkgs.callPackage ./iotest-image.nix {
    inherit mysql mysqlDatadir buildImage;
  };
}
