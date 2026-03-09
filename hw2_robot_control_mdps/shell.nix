let
  nixpkgs = fetchTarball "https://github.com/NixOS/nixpkgs/tarball/nixos-25.11";
  pkgs = import nixpkgs {
    config = { };
    overlays = [ ];
  };
in
pkgs.mkShellNoCC {
  packages = with pkgs; [
    #cudatoolkit
    ruff
    mujoco
    basedpyright
    (python312.withPackages (
      pypkgs: with pypkgs; [
        numpy
        jedi-language-server
        jupytext
        jupyter
        matplotlib
        tensorboard
        gymnasium
        stable-baselines3
        setuptools
        mujoco
      ]
    ))
  ];
  shellHook=''eval $(zoxide init bash)'';
 }
