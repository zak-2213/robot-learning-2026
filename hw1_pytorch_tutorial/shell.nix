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
    (python312.withPackages (
      pypkgs: with pypkgs; [
        jupytext
        torch
        torchvision
        jupyter
        matplotlib
      ]
    ))
  ];
}
