{ stdenv, fetchurl, python2, jre, makeWrapper }:

stdenv.mkDerivation rec {
  pname = "ycsb";
  version = "0.17.0";

  src = fetchurl {
    url = "https://github.com/harshanavkis/YCSB/releases/download/1/ycsb-0.17.0.tar.gz";
    sha256 = "0l4npcw1wcm2glj2i71p8c8w585bbgh1kj74kayby7xrg3zp9kx1";
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
