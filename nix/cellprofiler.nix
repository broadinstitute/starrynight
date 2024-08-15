{ pkgs, centrosome, cellprofiler-library-nightly, cellprofiler-core-nightly, scyjava,  }:

pkgs.python3Packages.buildPythonPackage rec {
  pname = "cellprofiler_nightly";
  version = "5.0.0.dev69";

  src = pkgs.fetchPypi {
    inherit pname version;
    sha256 = "sha256-tT2VLnK8MCoUEA0m1WWI6Q+eJBkVVLH65SK8kzJHsoo=";
  };
  
  pyproject = true;
  patches = [ ./cellprofiler_version.patch];
  

  postPatch = ''
    substituteInPlace pyproject.toml \
      --replace "docutils==0.15.2" "docutils>=0.15.2" \
      --replace "scipy>=1.4.1,<1.11" "scipy>=1.4.1" \
      --replace "wxPython==4.2.0" "wxPython~=4.2" \
  '';

  buidInputs  = with pkgs.python3Packages; [
    pytest
  ];

  propagatedBuildInputs = with pkgs.python3Packages; [
    cellprofiler-library-nightly
    cellprofiler-core-nightly
    centrosome
    boto3
    docutils
    imageio
    inflect
    jinja2
    joblib
    mahotas
    mysqlclient
    pillow
    sentry-sdk
    requests
    future
    fsspec
    h5py
    lxml
    matplotlib
    numpy
    psutil
    pyzmq
    scikit-image
    scikit-learn
    scipy
    scyjava
    six
    tifffile
    wxPython_4_2
    # (wxPython_4_2.overrideAttrs {
    #   src = pkgs.fetchurl {
    #     url = "https://extras.wxpython.org/wxPython4/extras/linux/gtk3/ubuntu-22.04/";
    #     hash = "";
    #   };
    # })
    rapidfuzz
    packaging
  ];

  pythonImportsCheck = [];

  meta = with pkgs.lib; {
    description = "Cellprofiler core";
    homepage = "https://cellprofiler.org";
    # license = license.mit;
  };
}
