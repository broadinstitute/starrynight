# Canvas UI Guide

This guide explains how to use the Canvas web interface for managing StarryNight projects and jobs.

## Overview

Canvas is the web interface for the Conductor service, providing a graphical way to:

- Create and manage projects
- Configure and run jobs
- Monitor execution
- View and download results

## Starting Canvas

1. **Start the Conductor service**:
   ```bash
   conductor start
   ```

2. **Start the Canvas UI** (in a separate terminal):
   ```bash
   cd canvas
   npm run dev
   ```

3. **Access the interface** by opening your browser to:
   ```
   http://localhost:3000
   ```

## Projects

### Creating a Project

1. From the dashboard, click **Create New Project**
2. Enter a project name and description
3. Configure project settings:
   - Storage location (local or S3)
   - Default parameters
4. Click **Create Project**

### Project Dashboard

The project dashboard shows:
- Project overview and description
- Recent job runs
- Quick access to common actions

## Jobs

### Creating a Job

1. Navigate to your project
2. Click **Create Job**
3. Select a job type:
   - Illumination Correction
   - Alignment
   - Preprocessing
   - Other available modules
4. Configure job parameters:
   - Input data location
   - Processing options
   - Output location
5. Click **Save Job**

### Running a Job

1. From the job page, click **Run Job**
2. Confirm the execution parameters
3. Click **Start**

### Job Configuration

Jobs are configured through a form interface with:
- Required parameters (highlighted)
- Optional parameters
- Advanced options (expandable sections)
- Validation to ensure proper configuration

## Monitoring

### Run Status

The run status page shows:
- Overall progress
- Current step
- Time elapsed
- Resource usage

### Logs

To view logs for a run:
1. Go to the run details page
2. Click **View Logs**
3. Filter logs by level (INFO, WARNING, ERROR)
4. Search for specific text

## Results

### Viewing Results

1. Navigate to a completed run
2. Click **View Results**
3. Browse the output files
4. Use built-in viewers for:
   - Images
   - CSV files
   - Parquet files
   - Text files

### Downloading Results

1. From the results page, select files to download
2. Click **Download Selected**
3. Or use the **Download All** button to get everything

## Advanced Features

### Project Templates

Save job configurations as templates:
1. Configure a job
2. Click **Save as Template**
3. Enter a template name
4. Use the template for future jobs

### AWS Integration

Configure AWS for cloud storage and processing:
1. Go to Project Settings
2. Click **Configure AWS**
3. Enter AWS credentials or configure IAM role
4. Select S3 bucket for storage

### Batch Processing

Process multiple datasets:
1. Create a job
2. Click **Add Batch**
3. Configure batch settings
4. Run as normal - all batches will be processed

## Troubleshooting

### Common UI Issues

- **Login problems**: Ensure Conductor service is running
- **Slow loading**: Check network connection and server logs
- **Failed jobs**: View logs for detailed error messages

### Server Issues

If the Canvas UI cannot connect to the Conductor service:
1. Check that Conductor is running (`conductor status`)
2. Verify network connectivity
3. Check Conductor logs for errors

## Next Steps

- Learn about [CLI Reference](cli-reference.md) for automation
- Explore [Processing Modules](modules.md) for available functionality
- Set up a [Developer Environment](developer-guide.md) to contribute
