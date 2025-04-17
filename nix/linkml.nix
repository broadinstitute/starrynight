{
  lib,
  buildPythonPackage,
  fetchPypi,
  rustPlatform,
}:
buildPythonPackage rec {
  pname = "linkml";
  version = "1.8.7";
  pyproject = true;

  src = fetchPypi {
    inherit pname version;
    sha256 = "";

  };

  dependencies = [
  ];
  pythonImportsCheck = [ "cpgparser" ];

  meta = {
    description = "CPG parser python library";
    homepage = "https://github.com/broadinstitute/cpg";
    license = lib.licenses.mit;
  };

}
