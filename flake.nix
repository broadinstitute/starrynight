{
  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-23.11";
    nixpkgs_master.url = "github:NixOS/nixpkgs/master";
    systems.url = "github:nix-systems/default";
    flake-utils.url = "github:numtide/flake-utils";
    flake-utils.inputs.systems.follows = "systems";
  };

  outputs = { self, nixpkgs, flake-utils, systems, ... } @ inputs:
      flake-utils.lib.eachDefaultSystem (system:
        let
            pkgs = import nixpkgs {
              system = system;
              config.allowUnfree = true;
            };

            mpkgs = import inputs.nixpkgs_master {
              system = system;
              config.allowUnfree = true;
            };
            python_with_pkgs = (pkgs.python310.withPackages(pp: [
              pp.wxPython_4_2
              pp.pygobject3
            ]));
          in
          with pkgs;
        {
          devShells = {
              default = mkShell {
                    NIX_LD = runCommand "ld.so" {} ''
                        ln -s "$(cat '${pkgs.stdenv.cc}/nix-support/dynamic-linker')" $out
                      '';
                    NIX_LD_LIBRARY_PATH = lib.makeLibraryPath [
                      # Add needed packages here
                      stdenv.cc.cc
                      libGL
                      zlib
                      libmysqlclient
                      mariadb
                      glib
                    ];
                    packages = [
                      python_with_pkgs
                      python310Packages.venvShellHook
                      git
                      gtk3
                      glib
                      pkg-config
                      poetry
                      # (mpkgs.awscli2.overrideAttrs (old: {
                      #   makeWrapperArgs = (old.makeWrapperArgs or []) ++ ["--unset" "PYTHONPATH"];
                      # }))
                      # mpkgs.pulumi-bin
                      jdk
                      maven
                      libmysqlclient
                      mariadb
                      duckdb
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
                        runHook venvShellHook
                        export PYTHONPATH=${python_with_pkgs}/${python_with_pkgs.sitePackages}:$PYTHONPATH
                        poetry install -C starrynight
                        python -m ipykernel install --user --name starry
                    '';
                  };
              };
        }
      );
}
