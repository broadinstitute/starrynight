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
    cp-pkgs = inputs.cp-flake.packages.${pkgs.system}.override { inherit python3Packages; };
    pipecraft = python3Packages.callPackage ./pipecraft.nix { };
    cpgparser = python3Packages.callPackage ./cpgparser.nix { };
    cpgdata = python3Packages.callPackage ./cpgdata.nix { inherit cpgparser; };
    # linkml = python3Packages.callPackage ./linkml.nix { };
    # pyimagej = python3Packages.callPackage ./pyimagej.nix { };
    starrynight = python3Packages.callPackage ./starrynight.nix {
      inherit
        cpgdata
        pipecraft
        # linkml
        # pyimagej
        ;
      inherit (cp-pkgs) cellprofiler cellprofiler-core cellprofiler-library;
    };

    # Containers
    container_illum_calculate = pkgs.callPackage ./containers/illum-calculate.nix {
      inherit nix2container outputs;
    };
  };

in
packages
