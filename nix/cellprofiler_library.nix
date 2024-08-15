{ pkgs, centrosome }:
pkgs.python3Packages.buildPythonPackage rec {
  pname = "cellprofiler_library_nightly";
  version = "5.0.0.dev69";

  src = pkgs.fetchPypi {
    inherit pname version;
    sha256 = "sha256-U8qrzJ38uZWAf7uHp8olO0tzLdgK/POikkWSi1D6LoA="; # TODO
  };

  pyproject = true;
  patches = [ ./cellprofiler_library_version.patch];

  postPatch = ''
    substituteInPlace pyproject.toml \
      --replace "centrosome~=1.2.2" "centrosome~=1.2.3" \
  '';

  buidInputs  = with pkgs.python3Packages; [
    pytest
  ];

  propagatedBuildInputs = with pkgs.python3Packages; [
    numpy
    scikit-image
    scipy
    mahotas
    centrosome
    matplotlib
    packaging
  ];
  pythonImportsCheck = [];

  meta = with pkgs.lib; {
    description = "Cellprofiler library";
    homepage = "https://cellprofiler.org";
    # license = license.mit;
  };

}
