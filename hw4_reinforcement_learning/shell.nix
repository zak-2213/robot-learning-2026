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
      name = "rl-hw4";
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
                eval $(zoxide init bash)
        [ -d .venv ] || uv venv
        source .venv/bin/activate

      '';
    }
  )
).env
