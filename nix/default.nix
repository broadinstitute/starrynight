{
  lib,
  pkgs,
  inputs,
  outputs,
  python3Packages,
  ...
}:

let
  # Apps
  packages = rec {
    pipecraft = python3Packages.callPackage ./pipecraft.nix { };
    cpgparser = python3Packages.callPackage ./cpgparser.nix { };
    # cpgdata = python3Packages.callPackage ./cpgdata.nix { };
    # starrynight = python3Packages.callPackage ./starrynight.nix { inherit pipecraft cpgdata; };
  };

in
# Containers
# containers = import pkgs.callPackage ./containers { };
packages
