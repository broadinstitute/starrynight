{
  pkgs,
  inputs,
  outputs,
  ...
}:
{
  imports = [
    (import pkgs.callPackage ./illum-calculate.nix { })
  ];
}
