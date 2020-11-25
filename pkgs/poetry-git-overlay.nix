{ pkgs }:
self: super: {

  pwntools = super.pwntools.overridePythonAttrs (
    _: {
      src = pkgs.fetchzip {
        url = "https://github.com/hase-project/pwntools/archive/59fbeb767ede61c8a54292daad3fa07cb996b805.tar.gz";
        sha256 = "1mcz0sifici186w67kbrks0qm2y3w35c1z40xx85g51gn88i5z28";
      };
    }
  );

}
