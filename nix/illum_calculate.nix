{pkgs}:
{
  illum_calculate = pkgs.dockerTools.buildLayeredImage {
    name = "starrynight-pcp-illum-calculate";
    tag = "latest";
    contents = [ app ];
    config = {
      Cmd = [];
      ExposedPorts = {};
    };
  };
}
