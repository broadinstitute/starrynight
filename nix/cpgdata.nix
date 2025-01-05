{
  lib,
  buildPythonPackage,
  fetchPypi,
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
buildPythonPackage {
  pname = "cpgdata";
  version = "0.4.0";
  src = fetchPypi {
    inherit pname version;
    sha256 = "";

  };
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
