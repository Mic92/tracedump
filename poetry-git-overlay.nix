{ pkgs }:
self: super: {

  intervaltree = super.intervaltree.overridePythonAttrs (
    _: {
      src = pkgs.fetchzip {
        url = "https://github.com/chaimleib/intervaltree/archive/6a731f2ce9f658cd6b8da2f7e23e96642643be54.zip";
        sha256 = "1rn5w2j9ap5jh7lx8cqr23ssx7pcmp8f2y80r2h1di031wy1lf71";
      };
    }
  );

  pwntools = super.pwntools.overridePythonAttrs (
    _: {
      src = pkgs.fetchzip {
        url = "https://github.com/hase-project/pwntools/archive/51645530f281930c03936a3a1cd886e0ed481bc3.zip";
        sha256 = "1fimgx46h468877cfq2qfnd795sllzfpiar71jh368sfxb87xr39";
      };
    }
  );

}
