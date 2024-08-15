{ pkgs, centrosome, cellprofiler-library-nightly, scyjava }:

pkgs.python3Packages.buildPythonPackage rec {
  pname = "cellprofiler_core_nightly";
  version = "5.0.0.dev69";

  src = pkgs.fetchPypi {
    inherit pname version;
    sha256 = "sha256-ROmgES6GY1RGOQdPiz8LqhsCVwUd7Vzq8Pe/KyASWuI=";
  };
  
  pyproject = true;
  patches = [ ./cellprofiler_core_version.patch];
  

  postPatch = ''
    substituteInPlace pyproject.toml \
      --replace "docutils==0.15.2" "docutils>=0.15.2" \
      --replace "scipy>=1.4.1,<1.11" "scipy>=1.4.1"
  '';

  buidInputs  = with pkgs.python3Packages; [
    pytest
  ];

  propagatedBuildInputs = with pkgs.python3Packages; [
    cellprofiler-library-nightly
    centrosome
    boto3
    docutils
    future
    fsspec
    h5py
    lxml
    matplotlib
    numpy
    psutil
    pyzmq
    scikit-image
    scipy
    scyjava
    zarr
    google-cloud-storage
    packaging
  ];

  pythonImportsCheck = [];

  meta = with pkgs.lib; {
    description = "Cellprofiler core";
    homepage = "https://cellprofiler.org";
    # license = license.mit;
  };
}
