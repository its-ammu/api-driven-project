# Simple Data Pipeline with Prefect

This project demonstrates a simple data pipeline using Prefect. The pipeline generates sample data, processes it by adding derived columns, and saves the results to a CSV file.

## Setup

1. Create a virtual environment (recommended):
```bash
python -m venv venv
source venv/bin/activate  # On Windows, use: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Local Usage

Run the pipeline locally:
```bash
python pipeline.py
```

The pipeline will:
1. Generate sample time series data
2. Process the data by adding:
   - 7-day rolling mean
   - Boolean flag indicating if value is above mean
3. Save the processed data to a CSV file with timestamp

## Cloud Deployment

### Prefect Cloud Setup

1. Sign up for a Prefect Cloud account at https://app.prefect.cloud
2. Create a new workspace
3. Get your API key from the Prefect Cloud UI
4. Set up the API key in GitHub Secrets:
   - Go to your GitHub repository settings
   - Navigate to Secrets and Variables > Actions
   - Add a new secret named `PREFECT_API_KEY` with your Prefect Cloud API key

### GitHub Actions

The pipeline is configured to run automatically:
- On push to the main branch
- On pull requests to the main branch
- Manually via workflow_dispatch

To run the pipeline manually:
1. Go to the Actions tab in your GitHub repository
2. Select "Run Prefect Pipeline"
3. Click "Run workflow"

## Project Structure

- `pipeline.py`: Main pipeline script containing the Prefect flow and tasks
- `requirements.txt`: Project dependencies
- `.github/workflows/pipeline.yml`: GitHub Actions workflow configuration
- `README.md`: This file

## Features

- Uses Prefect's `@flow` and `@task` decorators for workflow management
- Demonstrates basic data processing with pandas
- Includes automatic file naming with timestamps
- Provides clear logging of pipeline execution
- Runs in Docker containers via Prefect Cloud
- Automated execution through GitHub Actions