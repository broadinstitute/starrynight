{
  lib,
  buildPythonPackage,
  pytest,
  cython,
  setuptools,
  setuptools-scm,
  pipecraft,
  lark,
  numpy,
  contourpy,
  cloudpathlib,
  cellprofiler,
  cellprofiler-core,
  cellprofiler-library,
  joblib,
}:
buildPythonPackage {
  pname = "starrynight";
  version = "0.1.0";

  src = ./../starrynight;

  # Relax deps constraints
  # postPatch = ''
  #   substituteInPlace setup.py \
  #     --replace "scipy>=1.4.1,<1.11" "scipy>=1.4.1" \
  #     --replace "matplotlib>=3.1.3,<3.8" "matplotlib>=3.1.3"
  # '';

  buildInputs = [
    pytest
    cython
    setuptools
    setuptools-scm
  ];

  propagatedBuildInputs = [
    pipecraft
    lark
    numpy
    contourpy
    cloudpathlib
    cellprofiler
    cellprofiler-core
    cellprofiler-library
    joblib
  ];
  pythonImportsCheck = [ "starrynight" ];

  meta = {
    description = "Centrosome";
    homepage = "https://cellprofiler.org";
    license = lib.licenses.mit;
  };

}
