{ pkgs ? import <nixpkgs> { } }:

pkgs.mkShell rec {

  buildInputs = [
    pkgs.python3
    pkgs.python310Packages.psycopg2
    pkgs.poetry
    pkgs.zlib
  ];

  shellHook = ''
    export LD_LIBRARY_PATH="${pkgs.lib.makeLibraryPath buildInputs}:$LD_LIBRARY_PATH"
    export LD_LIBRARY_PATH="${pkgs.stdenv.cc.cc.lib.outPath}/lib:$LD_LIBRARY_PATH"
  '';
}
