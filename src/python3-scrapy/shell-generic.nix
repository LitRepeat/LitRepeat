{ pkgs ? import <nixpkgs> {} }:

pkgs.mkShell {
  buildInputs = [
    pkgs.python3
    pkgs.uv
    pkgs.python313Packages.scrapy
    pkgs.python313Packages.playwright
    pkgs.reuse
    pkgs.playwright
    pkgs.playwright-driver.browsers
  ];

  shellHook = ''
      export PLAYWRIGHT_BROWSERS_PATH=${pkgs.playwright-driver.browsers}
      export PLAYWRIGHT_SKIP_VALIDATE_HOST_REQUIREMENTS=true
      export PLAYWRIGHT_HOST_PLATFORM_OVERRIDE="ubuntu-24.04"
    '';
}
