{
  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-24.05";
    nixpkgs_master.url = "github:NixOS/nixpkgs/master";
    systems.url = "github:nix-systems/default";
    devenv.url = "github:cachix/devenv";
  };
  outputs = { self, nixpkgs, flake-utils, systems, ... } @ inputs:
      flake-utils.lib.eachDefaultSystem (system:
        let
            pkgs = import nixpkgs {
              system = system;
              config.allowUnfree = true;
            };

            # mpkgs = import inputs.nixpkgs_master {
            #   system = system;
            #   config.allowUnfree = true;
            # };
          in
          with pkgs;
        {
          devShells = {
              default = let 
                python_with_pkgs = (pkgs.python311.withPackages(pp: [
                  pp.packaging
                  pp.snakemake
                ]));
              in mkShell {
                    NIX_LD = runCommand "ld.so" {} ''
                        ln -s "$(cat '${pkgs.stdenv.cc}/nix-support/dynamic-linker')" $out
                      '';
                    NIX_LD_LIBRARY_PATH = lib.makeLibraryPath [
                      # Add needed packages here
                      stdenv.cc.cc
                      libGL
                     
                    ];
                    packages = [
                      python_with_pkgs
                      python3Packages.venvShellHook
                      uv
                      duckdb
                      # Required by snakemake apptainer/singularity backend
                      gocryptfs
                      nextflow
                    ];
                    venvDir = "./.venv";
                    postVenvCreation = ''
                        unset SOURCE_DATE_EPOCH
                      '';
                    postShellHook = ''
                        unset SOURCE_DATE_EPOCH
                      '';
                    shellHook = ''
                        export LD_LIBRARY_PATH=$NIX_LD_LIBRARY_PATH
                        export PYTHON_KEYRING_BACKEND=keyring.backends.fail.Keyring
                        runHook venvShellHook
                        export PYTHONPATH=${python_with_pkgs}/${python_with_pkgs.sitePackages}:$PYTHONPATH
                    '';
                  };
              };
        }
      );
}
