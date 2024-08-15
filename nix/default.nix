{ pkgs, ... }:
rec {

  # Cellprofiler
  centrosome = import ./centrosome.nix { inherit pkgs; };
  cellprofiler-library-nightly = import ./cellprofiler_library.nix { inherit pkgs centrosome; };
  jgo = import ./jgo.nix { inherit pkgs; };
  scyjava = import ./scyjava.nix { inherit pkgs jgo; };
  cellprofiler-core-nightly = import ./cellprofiler_core.nix { inherit pkgs centrosome cellprofiler-library-nightly scyjava; };
  cellprofiler-nightly = import ./cellprofiler.nix { inherit pkgs cellprofiler-library-nightly centrosome cellprofiler-core-nightly scyjava; };

  # Starrynight
  # illum-calculate = import ./illum_calculate { inherit pkgs;};
  # docker-illum-calculate = import ./docker_image { inherit pkgs illum-calculate;};
  # canvas = dream2nix.lib.evalModules{
  #   packageSets.nixpkgs = pkgs;
  #   modules = [
  #     ./canvas.nix
  #     {
  #       paths.projectRoot = ../.;
  #       paths.projectRootFile = "flake.nix";
  #       paths.package = ../.;
  #     }
  #   ];
  # };
  #
  # conductor = dream2nix.lib.evalModules{
  #   packageSets.nixpkgs = pkgs;
  #   modules = [
  #     ./conductor.nix
  #     {
  #       paths.projectRoot = ../.;
  #       paths.projectRootFile = "flake.nix";
  #       paths.package = ../.;
  #     }
  #   ];
  # };
}
