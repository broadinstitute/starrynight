{ pytest, jgo, jpype1, buildPythonPackage, fetchPypi }:
buildPythonPackage rec {
  pname = "scyjava";
  version = "1.10.0";

  src = fetchPypi {
    inherit pname version;
    sha256 = "sha256-f4boY36Oed5W1kPZeOgyU/84l0pD12V583ktXgdtVoE=";
  };

  pyproject = true;

  # Relax deps constraints
  # postPatch = ''
  #   substituteInPlace setup.py \
  #     --replace "scipy>=1.4.1,<1.11" "scipy>=1.4.1" \
  #     --replace "matplotlib>=3.1.3,<3.8" "matplotlib>=3.1.3"
  # '';

  buidInputs  = [
    pytest
  ];

  propagatedBuildInputs = [
    jpype1
    jgo
  ];

  pythonImportsCheck = [];

  meta = {
    description = "ScyJava";
    homepage = "https://github.com/scijava/scyjava";
    # license = license.mit;
  };

}
