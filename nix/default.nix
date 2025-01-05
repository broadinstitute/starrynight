{
  lib,
  pkgs,
  inputs,
  outputs,
  python3Packages,
  ...
}:

let
  # tools
  inherit (inputs.nix2container.packages.${pkgs.system}) nix2container;
  # Apps
  packages = rec {
    cp-pkgs = inputs.cp-flake.packages.${pkgs.system};
    pipecraft = python3Packages.callPackage ./pipecraft.nix { };
    cpgparser = python3Packages.callPackage ./cpgparser.nix { };
    cpgdata = python3Packages.callPackage ./cpgdata.nix { inherit cpgparser; };
    starrynight = python3Packages.callPackage ./starrynight.nix {
      inherit cpgdata pipecraft;
      inherit (cp-pkgs) cellprofiler cellprofiler-core cellprofiler-library;
    };

    # Containers
    container_illum_calculate = pkgs.callPackage ./containers/illum-calculate.nix {
      inherit nix2container outputs;
    };
  };

in
packages
