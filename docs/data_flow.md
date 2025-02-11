# Data flow

## Scientific users
- Create project
    - Add details (dataset related paths)
    - Select project type
    - Select project parser
    - Add project related details
    - Create project

- Configure experiment
    - Generate inventory
    - Generate Index
    - Configure Experiment from Index
    - Create pipeline from experiment and data params

- Execute Pipeline
    - Execute entire pipeline
    - Execute parts of the pipeline
    - Inpect and change inputs of pipeline modules
    - Inspect outputs of multiple runs
    - Maybe add additional jobs to the pipeline

## Module Authors

- Write scientific algorithm
- Wrap the algorithm using a `Node` object
- Write spec for the algorithm
- Write script to configure module using experiment and data params together with the spec
- Optionally describe parallel execution strategy

## Infrastructure maintainer

- Write the pipecraft backend
- Think about the security model
- Figure out a deployment strategy
    - CI/CD of Starrynight components
    - Scaling of compute workers
    - Data storage and movement
