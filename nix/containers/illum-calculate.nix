{
  pkgs,
  nix2container,
  outputs,
  ...
}:
pkgs.dockerTools.buildImage {
  name = "ghcr.io/broadinstitute/starrynight-illum-calculate";
  tag = "dev";
  config = {
    Cmd = [
      "${outputs.packages.${pkgs.system}.starrynight}/bin/starrynight"
      "illum"
    ];
  };
}
