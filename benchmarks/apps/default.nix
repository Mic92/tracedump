{ pkgs ? import ./nixpkgs.nix {} }:
rec {
  inherit (pkgs) nginx mysql redis netcat sysbench wrk;
  ycsb = pkgs.callPackage ./ycsb.nix {};
  mysqlDatadir = "/var/lib/mysql";
  buildImage = pkgs.callPackage ./build-image.nix {};
  iotest-image = pkgs.callPackage ./iotest-image.nix {
    inherit mysql mysqlDatadir buildImage;
  };
  sqlite-speedtest = pkgs.sqlite.overrideAttrs (old: {
    src = pkgs.fetchFromGitHub {
      owner = "harshanavkis";
      repo = "sqlite-speedtest-custom";
      rev = "591be835b8e73bc79f1e6d7766a78e20b915d94f";
      sha256 = "08wpy6739hgbcf7jyklq66vjhy28yyyaxmfdlgzgcy1y584zmh3g";
    };
    buildInputs = [ pkgs.tcl ];
    outputs = [ "out" ];
    makeFlags = [ "speedtest1" ];
    installPhase = ''
      install -D speedtest1 $out/bin/speedtest1
    '';
  });
}
