# Getting Started with the StarryNight Web UI

The StarryNight Web UI (Canvas) provides a user-friendly interface for creating projects, configuring and running jobs, and analyzing results. This guide will help you get started with the web interface.

## System Components

The web interface consists of two main components:

1. **Conductor**: The backend API server that manages projects, jobs, and runs
2. **Canvas**: The frontend UI built with Next.js

## Prerequisites

- StarryNight packages installed
- Access to image data storage

## Starting the Services

### 1. Start the Conductor API Server

From the StarryNight repository root:

```bash
# In a Nix shell
conductor
```

This starts the API server on http://localhost:8000 by default.

### 2. Start the Canvas UI

From the StarryNight repository root:

```bash
# In a separate terminal
cd canvas
npm run dev
```

This starts the web UI on http://localhost:3000.

## Using the Web Interface

### Creating a New Project

1. Navigate to the Projects page
2. Click "Create New Project"
3. Follow the step-by-step wizard:
   - Enter project name and description
   - Specify dataset paths
   - Select project type
   - Choose parsing method
   - Review and create the project

### Project Dashboard

Once a project is created, you'll be taken to the project dashboard with tabs for:

- **Overview**: Project details and status
- **Jobs**: Configure and run processing modules
- **Runs**: View execution history and results

### Configuring a Job

1. In the project dashboard, go to the Jobs tab
2. Select the module you want to run (e.g., Illumination Correction)
3. Configure module-specific parameters
4. Save the configuration

### Running a Job

1. From the Jobs tab, find your configured job
2. Click "Run" to start execution
3. Monitor progress in real-time

### Viewing Results

1. Once a job completes, go to the Runs tab
2. Select the run you're interested in
3. View logs, metrics, and output files
4. Compare multiple runs using the comparison view

## Workflow Example

A typical workflow in the web UI:

1. Create a new project with your dataset location
2. Wait for inventory and index generation to complete
3. Configure an illumination correction job
4. Run the job and monitor progress
5. View the generated illumination files
6. Configure subsequent processing steps
7. Export or download results as needed

## Troubleshooting

If you encounter issues:

- Check the logs in the Run details page
- Verify your data paths are correct
- Ensure Conductor API is running
- Check browser console for frontend errors

## Next Steps

- Learn about [project management](project-management.md)
- Understand how to [configure jobs](job-configuration.md)
- Explore [result analysis](result-analysis.md)

For CLI alternatives to the web UI, see the [CLI workflow guides](../cli-workflows/illumination-correction.md).
