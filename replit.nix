{ pkgs }: {
    deps = [
        pkgs.gh
        pkgs.python310
        pkgs.nodePackages.gitmoji-cli
        pkgs.python38Packages.python-language-server
    ];
}