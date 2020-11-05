with import <nixpkgs> {};
let
  processor-trace = stdenv.mkDerivation rec {
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
  };
  poetry2nix = pkgs.callPackage (pkgs.fetchzip {
    url = "https://github.com/Mic92/poetry2nix/archive/81948c55049c5f3716d0eea1e288eaaf4e50cdbd.tar.gz";
    sha256 = "1jsn6c1y6iagrrigzl8p6yknknkxaldb5cz2r3g8ldvgq8ykwhnl";
  }) {};
in poetry2nix.mkPoetryApplication {
  projectDir = ./.;
  buildInputs = [
    processor-trace
  ];
  overrides = [
    (import ./poetry-git-overlay.nix { inherit pkgs; })
    poetry2nix.defaultPoetryOverrides
  ];
}
