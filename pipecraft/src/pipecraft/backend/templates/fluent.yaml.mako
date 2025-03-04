service:
  flush: 1
  log_level: info

parsers:
  - name: stringify
    format: regex
    regex: '^(?<message>.*)'

pipeline:
  inputs:
    # - name: random
    #   tag: test_random
    - name: stdin
      tag: stdin
      parser: stringify

  outputs:
    - name: stdout
      match: '*'
    - name: file
      file: nohup.out
      match: '*'
    - name: opentelemetry
      match: "*"
      host: localhost
      port: 4318
      add_label: 'app random-app'
      processors:
        logs:
        - name: opentelemetry_envelope
        - name: content_modifier
          context: otel_resource_attributes
          action: insert
          key: service.name
          value: test_app
        - name: content_modifier
          context: otel_resource_attributes
          action: insert
          key: service.label
          value: test_app_label
