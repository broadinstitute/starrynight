{
  inputs,
  outputs,
  ...
}:
{
  illum_calculate = inputs.nix2container.buildImage {
    name = "starrynight-illum-calculate";
    config = {
      entrypoint = [
        "${outputs.packages.starrynight}/bin/starrynight"
        "illum"
      ];
    };
  };
}
