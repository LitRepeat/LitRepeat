{
  description = "A flake for Hreyfan";

  inputs = {
    nixpkgs.url = "github:nixos/nixpkgs/25.11";
  };

  outputs = { self, nixpkgs }:
  let
    system = "x86_64-linux";
    pkgs = nixpkgs.legacyPackages.${system};
    shell = import ./shell-generic.nix { inherit pkgs; };
  in {
    devShells.${system}.default = shell;
  };
}
