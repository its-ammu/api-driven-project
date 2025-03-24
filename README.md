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
- Automatically saves outputs as GitHub Actions artifacts

## Output Artifacts

The pipeline generates three main artifacts that are saved in the `output` directory and uploaded as GitHub Actions artifacts:

1. **Interactive Visualizations**:
   - `energy_transition.html`: A scatter plot showing the relationship between fossil fuel and renewable energy consumption across countries
   - `regional_trends.html`: A line chart showing renewable energy adoption trends by region

2. **Analysis Report**:
   - `energy_report.txt`: A comprehensive report containing:
     - Total number of countries analyzed
     - Global average renewable energy share
     - Top 5 countries by renewable energy share
     - Top 5 countries by energy transition score
     - Links to generated visualizations

## Accessing the Artifacts

After the pipeline runs, you can access the artifacts in two ways:

1. **Through GitHub Actions**:
   - Go to the "Actions" tab in your repository
   - Select the latest workflow run
   - Scroll down to the "Artifacts" section
   - Click on "energy-analysis-output" to download the files
   - The artifacts are retained for 7 days

2. **Locally**:
   - The files are also saved in the `output` directory of your repository
   - You can find them at:
     - `output/energy_transition.html`
     - `output/regional_trends.html`
     - `output/energy_report.txt`

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