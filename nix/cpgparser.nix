{
  lib,
  buildPythonPackage,
  fetchPypi,
  rustPlatform,
}:
buildPythonPackage rec {
  pname = "cpgparser";
  version = "0.2.0";
  pyproject = true;

  src = fetchPypi {
    inherit pname version;
    sha256 = "sha256-5k3u873kKKFyP2qps1Buq+SmIuU0BPUfa23+FaAoomE=";

  };

  nativeBuildInputs = with rustPlatform; [
    maturinBuildHook
    cargoSetupHook
  ];

  cargoDeps = rustPlatform.fetchCargoTarball {
    inherit pname version src;
    hash = "sha256-uz/q3cnWNf9k8bNeUIh1gzJGCWWOnPSwSoAgvlwAdlo=";
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
