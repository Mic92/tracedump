{ stdenv, stdenvAdapters, closureInfo
, e2fsprogs, lkl, lib
}:

{ pkg
, extraFiles ? {}
, extraCommands ? ""
, debugSymbols ? true
, diskSize ? "1G"
}:
let
  closure = closureInfo { rootPaths = [ ]; };
  files = {
    "etc/group" = ''
      root:x:0:
      nogroup:x:65534:
    '';
    "etc/passwd" = ''
      root:x:0:0:Root:/:/bin/sh
      nobody:x:65534:65534:Nobody:/:/noshell
    '';
    "etc/hosts" = ''
      127.0.0.1 localhost
      ::1 localhost
    '';
  } // extraFiles;
in stdenv.mkDerivation {
  name = "image";
  nativeBuildInputs = [ e2fsprogs lkl ];
  dontUnpack = true;

  installPhase = ''
    mkdir -p root/{nix/store,tmp,etc}
    root=$(readlink -f root)
    ${lib.concatMapStrings (file: ''
      dir="$root/$(dirname ${file})"
      if [ ! -d "$dir" ]; then
        mkdir -p "$dir"
      fi
      ${if builtins.isString files.${file} then ''
        cat > "$root/${file}" <<'EOF'
        ${files.${file}}
        EOF
      '' else ''
        install -D ${files.${file}.path} "$root/${file}"
      ''}
    '') (lib.attrNames files)}

    ${extraCommands}

    # FIXME calculate storage requirement
    truncate -s ${diskSize}  $out
    mkfs.ext4 $out
    cptofs -t ext4 -i $out $root/* $root/.* /
  '';
}
