{
  lib,
  buildPythonPackage,
  pytest,
  cython,
  setuptools,
  setuptools-scm,
  pipecraft,
  cpgdata,
  lark,
  numpy,
  contourpy,
  cloudpathlib,
  cellprofiler,
  cellprofiler-core,
  cellprofiler-library,
  joblib,
  pyimagej,
  linkml,
  marimo,
}:
buildPythonPackage {
  pname = "starrynight";
  version = "0.1.0";
  pyproject = true;

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
    cpgdata
    lark
    numpy
    contourpy
    cloudpathlib
    cellprofiler
    cellprofiler-core
    cellprofiler-library
    joblib
    pyimagej
    linkml
    marimo
  ];
  pythonImportsCheck = [ "starrynight" ];

  meta = {
    description = "Starrynight";
    homepage = "https://github.com/broadinstitute/bin/starrynight";
    license = lib.licenses.mit;
  };

}
