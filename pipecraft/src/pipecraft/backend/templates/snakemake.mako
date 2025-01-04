rule all:
  input:
    % for container in containers:
      % for k, v in container.output_paths.items():
    ${k}_${container.name.replace(" ", "_").lower()}=[
            % for path in v:
            "${path}",
            % endfor
          ],
      % endfor
    % endfor
  shell:
    "echo 'done' > completed.txt"

% for container in containers:
rule ${container.name.replace(" ", "_").lower()}:
  input:
    % for k, v in container.input_paths.items():
      ${k}=[
              % for path in v:
              "${path}",
              % endfor
            ],
    % endfor
  output:
    % for k, v in container.output_paths.items():
      ${k}=[
              % for path in v:
              "${path}",
              % endfor
            ],
    % endfor
  container: "docker://${container.config.image}"
  % if len(container.config.cmd) != 0:
  shell:
    "${' '.join(container.config.cmd)}"
  % elif "cellprofiler" in container.config.image:
  shell:
    "cellprofiler -c -r -p {input.cppipe} --data-file {input.load_data}"
  % elif "fiji" in container.config.image:
  shell:
    "python exec_fiji.py {input.load_data}"
  % endif
% endfor

% for pyfunction in pyfunctions:
rule ${function.name}:
  inputs:
  outputs:
  shell:
% endfor


% for invoke_shell in invoke_shells:
rule ${invoke_shell.name}:
  inputs:
  outputs:
  shell:
% endfor
