{
  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-24.11";
    nixpkgs_master.url = "github:NixOS/nixpkgs/master";
    systems.url = "github:nix-systems/default";
    flake-utils.url = "github:numtide/flake-utils";
    flake-utils.inputs.systems.follows = "systems";
    cp-flake.url = "github:CellProfiler/CellProfiler";
    cp-flake.inputs.nixpkgs.follows = "nixpkgs";
  };

  outputs =
    {
      self,
      nixpkgs,
      flake-utils,
      systems,
      ...
    }@inputs:
    flake-utils.lib.eachDefaultSystem (
      system:
      let
        inherit (self) outputs;
        pkgs = import nixpkgs {
          inherit system;
          config.allowUnfree = true;
        };
        mpkgs = import inputs.nixpkgs_master {
          inherit system;
          config.allowUnfree = true;
        };
      in
      with pkgs;
      {
        packages = pkgs.callPackage ./nix {
          inherit inputs outputs;
          python3Packages = pkgs.python311Packages;
        };
        devShells = {
          default =
            let
              python_with_pkgs = (
                pkgs.python311.withPackages (pp: [
                  (inputs.cp-flake.packages.${system}.override {
                    python3Packages = pkgs.python311Packages;
                  }).cellprofiler
                  pp.mysqlclient
                  pp.packaging
                  pp.snakemake
                  pp.snakemake-storage-plugin-s3
                ])
              );
            in
            mkShell {
              NIX_LD = runCommand "ld.so" { } ''
                ln -s "$(cat '${pkgs.stdenv.cc}/nix-support/dynamic-linker')" $out
              '';
              NIX_LD_LIBRARY_PATH = lib.makeLibraryPath [
                # Add needed packages here
                stdenv.cc.cc
                libGL

                libxcrypt-legacy
                libmysqlclient
                mariadb
                glib
                hdf5
              ];
              packages = [
                python_with_pkgs
                python311Packages.venvShellHook
                git
                gtk3
                glib
                pkg-config
                uv
                jdk
                maven
                libmysqlclient
                mariadb
                duckdb
                hdf5
                # nodejs deps
                nodejs_22
                gocryptfs
                goofys
                nextflow
                arion
                mpkgs.fluent-bit
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
