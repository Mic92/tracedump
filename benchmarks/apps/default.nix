with import (builtins.fetchTarball {
  url = "https://github.com/NixOS/nixpkgs/archive/493562c72dd9060f06bdc47d0d29c95177e02c77.tar.gz";
  sha256 = "089xdacgvxxz617zs7q1j8nsspg9k7l2vpxdzlcqhhq8sclccx87";
}) {};
rec {
  inherit nginx mysql sqlite redis netcat sysbench;
  ycsb = pkgs.callPackage ./ycsb {};
  mysqlDatadir = "/var/lib/mysql";
  buildImage = callPackage ./build-image.nix {};
  iotest-image = pkgs.callPackage ./iotest-image.nix {
    inherit mysql mysqlDatadir buildImage;
  };
}
