{
  pkgs ? import <nixpkgs> { },
}:
(
  let
    base = pkgs.appimageTools.defaultFhsEnvArgs;
  in
  pkgs.buildFHSEnv (
    base
    // {
      name = "rl-hw3";
      targetPkgs =
        pkgs:
        (with pkgs; [
          gcc
          glibc
          zlib
          ruff
          mujoco
          uv
          python312
        ]);
      runScript = "zsh";
      extraOutputsToInstall = [ "dev" ];
      shellHook = ''
        if [ ! -d .venv ]; then
            uv venv
        fi
        source .venv/bin/activate
      '';
    }
  )
).env
