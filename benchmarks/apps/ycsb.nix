{ stdenv, fetchurl, python2, jre, makeWrapper }:

stdenv.mkDerivation rec {
  pname = "ycsb";
  version = "0.17.0";

  src = fetchurl {
    url = "https://github.com/brianfrankcooper/YCSB/releases/download/0.17.0/ycsb-0.17.0.tar.gz";
    sha256 = "sha256-2A2LZ8Sx2px9ncDUDN2aZR8MD0TlgK6gD7P4bP+29cw=";
  };

  buildInputs = [ python2 ];
  nativeBuildInputs = [ makeWrapper ];

  installPhase = ''
    mkdir -p $out/{bin,share/ycsb}
    cp -r * $out/share/ycsb
    makeWrapper $out/share/ycsb/bin/ycsb $out/bin/ycsb \
      --prefix PATH : ${stdenv.lib.makeBinPath [ jre ]}
  '';
}
