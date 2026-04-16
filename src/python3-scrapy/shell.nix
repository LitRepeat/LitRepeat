{ pkgs ? import (fetchTarball {
    url = "https://github.com/NixOS/nixpkgs/archive/tags/25.11.tar.gz";
    # If the commit changes, to get a value for sha256:
    # $ hash=$(nix-prefetch-url --unpack --type sha256 ${url})
    # $ nix hash convert --hash-algo sha256 --to sri "${hash}"
    sha256 = "sha256-M101xMtWdF1eSD0xhiR8nG8CXRlHmv6V+VoY65Smwf4=";
  }) {} }:

import ./shell-generic.nix { inherit pkgs; }
