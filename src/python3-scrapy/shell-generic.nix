{ pkgs ? import <nixpkgs> {} }:

pkgs.mkShell {
  buildInputs = [
    pkgs.python3
    pkgs.python313Packages.scrapy
    pkgs.reuse
  ];
}
