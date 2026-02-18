let
  nixpkgs = fetchTarball "https://github.com/NixOS/nixpkgs/tarball/nixos-25.11";
  pkgs = import nixpkgs {
    config = { };
    overlays = [ ];
  };
in
pkgs.mkShellNoCC {
  packages = with pkgs; [
    (python312.withPackages (
      pypkgs: with pypkgs; [
        torch
        torchvision
        jupyter
      ]
    ))
  ];
}
