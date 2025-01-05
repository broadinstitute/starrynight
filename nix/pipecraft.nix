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
    description = "Pipecraft library for crafting data pipelines in python";
    homepage = "https://github.com/broadinstitute/starrynight";
    license = lib.licenses.mit;
  };

}
