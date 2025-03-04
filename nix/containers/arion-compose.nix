{
  project.name = "starrynight-observability";
  # enableDefaultNetwork = true;
  # networks.pythonml.driver = "host";
  services = {
    otel-lgtm = {
      service = {
        image = "grafana/otel-lgtm";
        ports = [
          "3100:3100"
          "4000:3000"
          "4317:4317"
          "4318:4318"
        ];

      };
    };
  };
}
