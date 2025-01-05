{
  lib,
  buildPythonPackage,
  fetchPypi,
  poetry-core,
  pytest,
  cython,
  setuptools,
  setuptools-scm,
  click,
  pydantic,
  polars,
  pyarrow,
  joblib,
  cpgparser,
  tqdm,
  lark,
}:
buildPythonPackage rec {
  pname = "cpgdata";
  version = "0.4.0";
  src = fetchPypi {
    inherit pname version;
    sha256 = "sha256-nCDzjnEXD0Hs4lfS9NP9DbG0ly84Y8NDICbvpuMD1cU=";

  };
  pyproject = true;

  # Relax deps constraints
  postPatch = ''
    substituteInPlace pyproject.toml \
      --replace-warn 'polars = "^0.19"' 'polars = ">=0.19"' \
      --replace-warn 'pyarrow = "^13.0"' 'pyarrow = ">=13.0"'
  '';

  buildInputs = [
    pytest
    cython
    setuptools
    setuptools-scm
    poetry-core
  ];

  propagatedBuildInputs = [
    click
    pydantic
    polars
    pyarrow
    joblib
    cpgparser
    tqdm
    lark
  ];
  pythonImportsCheck = [ "cpgdata" ];

  meta = {
    description = "CPG data python library";
    homepage = "https://github.com/broadinstitute/cpg";
    license = lib.licenses.mit;
  };

}
