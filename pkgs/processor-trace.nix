{ stdenv, fetchFromGitHub, cmake }:

stdenv.mkDerivation rec {
  name = "processor-trace-${version}";
  version = "2.0";
  src = fetchFromGitHub {
    owner = "01org";
    repo = "processor-trace";
    rev = "v${version}";
    sha256 = "1qhrsycxqjm9xmhi3zgkq9shzch54dp4nc83d1gk5xs0287wsw5p";
  };
  nativeBuildInputs = [ cmake ];
  cmakeFlags = ["-DCMAKE_BUILD_TYPE=RelWithDebInfo"];
  dontStrip=1;
}
