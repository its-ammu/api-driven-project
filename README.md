# Global Energy Transition Analysis Pipeline with Prefect

This project implements a data pipeline that analyzes global energy consumption and renewable energy adoption data from the World Bank. The pipeline tracks energy transition progress across countries and regions, providing insights into the shift towards sustainable energy sources.

## Features

- Real-time data fetching from World Bank API
- Multi-indicator energy analysis
- Regional trend analysis
- Interactive visualizations using Plotly
- Web dashboard using Dash
- Automated report generation
- Prefect workflow management

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
1. Fetch the latest energy consumption data from World Bank
2. Process and analyze energy transition metrics
3. Generate interactive visualizations
4. Create a web dashboard
5. Generate a summary report

Outputs:
- Interactive visualizations in the `output` directory
- Summary report in `output/energy_report.txt`
- Web dashboard available at http://localhost:8050

## Cloud Deployment

### Prefect Cloud Setup

1. Sign up for a Prefect Cloud account at https://app.prefect.cloud
2. Create a new workspace
3. Get your API key from the Prefect Cloud UI
4. Set up the API key in GitHub Secrets:
   - Go to your GitHub repository settings
   - Navigate to Secrets and Variables > Actions
   - Add a new secret named `PREFECT_API_KEY` with your Prefect Cloud API key
   - Add a new secret named `PREFECT_WORKSPACE` with your workspace name

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
- `output/`: Directory containing generated visualizations and reports
- `README.md`: This file

## Data Analysis Features

1. Energy Consumption Analysis:
   - Per capita energy use
   - Electric power consumption
   - Fossil fuel dependency
   - Renewable energy adoption

2. Transition Metrics:
   - Energy transition score
   - Year-over-year renewable growth
   - Regional energy patterns
   - Country-level comparisons

3. Visualizations:
   - Interactive scatter plots for energy transition progress
   - Regional trend line charts
   - Web dashboard with multiple views

4. Reporting:
   - Key energy statistics
   - Top performing countries
   - Regional comparisons
   - Links to interactive visualizations