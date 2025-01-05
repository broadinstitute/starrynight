{
  lib,
  buildPythonPackage,
  pytest,
  cython,
  setuptools,
  setuptools-scm,
  pydantic,
  matplotlib,
  mako,
  cloudpathlib,
  networkx,
}:
buildPythonPackage {
  pname = "pipecraft";
  version = "0.1.0";

  src = ./../pipecraft;
  pyproject = true;

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
    pydantic
    networkx
    cloudpathlib
    matplotlib
    mako
  ];
  pythonImportsCheck = [ "pipecraft" ];

  meta = {
    description = "Centrosome";
    homepage = "https://cellprofiler.org";
    license = lib.licenses.mit;
  };

}
