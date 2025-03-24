from prefect import flow, task
import pandas as pd
import numpy as np
from datetime import datetime
import requests
import plotly.express as px
import plotly.graph_objects as go
from dash import Dash, html, dcc
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

@task
def fetch_energy_data():
    """Fetch energy consumption and renewable energy data from World Bank API"""
    # World Bank API endpoints for energy indicators
    indicators = {
        'EG.USE.PCAP.KG.OE': 'Energy use per capita (kg of oil equivalent)',
        'EG.FEC.RNEW.ZS': 'Renewable energy consumption (% of total final energy consumption)',
        'EG.USE.COMM.FO.ZS': 'Fossil fuel energy consumption (% of total)',
        'EG.USE.ELEC.KH.PC': 'Electric power consumption (kWh per capita)'
    }
    
    try:
        # Fetch data for each indicator
        dfs = []
        for indicator in indicators.keys():
            url = f"https://api.worldbank.org/v2/country/all/indicator/{indicator}?format=json&per_page=1000"
            response = requests.get(url)
            response.raise_for_status()
            
            # Extract data from response
            data = response.json()[1]
            
            # Convert to DataFrame
            df = pd.DataFrame(data)
            
            # Extract relevant columns
            df = df[['country', 'date', 'value', 'indicator']]
            
            # Map indicator code to description
            df['indicator'] = df['indicator'].map(indicators)
            
            # Convert date and value to appropriate types
            df['date'] = pd.to_datetime(df['date'])
            df['value'] = pd.to_numeric(df['value'], errors='coerce')
            
            dfs.append(df)
        
        # Combine all indicators
        combined_df = pd.concat(dfs, ignore_index=True)
        
        # Pivot the data to have indicators as columns
        df_pivot = combined_df.pivot(
            index=['country', 'date'],
            columns='indicator',
            values='value'
        ).reset_index()
        
        return df_pivot
    except Exception as e:
        print(f"Error fetching data: {e}")
        raise

@task
def process_data(df):
    """Process and clean the energy data"""
    # Calculate year-over-year changes
    df['Renewable Growth'] = df.groupby('country')['Renewable energy consumption (% of total final energy consumption)'].pct_change()
    
    # Calculate energy transition score (higher renewable %, lower fossil fuel %)
    df['Energy Transition Score'] = (
        df['Renewable energy consumption (% of total final energy consumption)'] -
        df['Fossil fuel energy consumption (% of total)']
    )
    
    # Get latest data for each country
    latest_data = df.groupby('country').last().reset_index()
    
    # Calculate regional averages
    df['Region'] = df['country'].map(lambda x: get_region(x))
    regional_avg = df.groupby(['Region', 'date']).mean().reset_index()
    
    return df, latest_data, regional_avg

def get_region(country):
    """Map countries to regions"""
    # This is a simplified mapping - you can expand this
    regions = {
        'United States': 'North America',
        'Canada': 'North America',
        'China': 'Asia',
        'India': 'Asia',
        'Germany': 'Europe',
        'France': 'Europe',
        'Brazil': 'South America',
        'South Africa': 'Africa',
        'Australia': 'Oceania'
    }
    return regions.get(country, 'Other')

@task
def create_visualizations(df, latest_data, regional_avg):
    """Create interactive visualizations"""
    # Create output directory if it doesn't exist
    os.makedirs('output', exist_ok=True)
    
    # 1. Energy Transition Progress
    fig_transition = px.scatter(
        latest_data,
        x='Fossil fuel energy consumption (% of total)',
        y='Renewable energy consumption (% of total final energy consumption)',
        size='Energy use per capita (kg of oil equivalent)',
        color='Region',
        hover_data=['country'],
        title='Energy Transition Progress by Country',
        labels={
            'Fossil fuel energy consumption (% of total)': 'Fossil Fuel Consumption (%)',
            'Renewable energy consumption (% of total final energy consumption)': 'Renewable Energy (%)'
        }
    )
    fig_transition.write_html('output/energy_transition.html')
    
    # 2. Regional Renewable Energy Trends
    fig_regional = px.line(
        regional_avg,
        x='date',
        y='Renewable energy consumption (% of total final energy consumption)',
        color='Region',
        title='Regional Renewable Energy Adoption Trends',
        labels={
            'Renewable energy consumption (% of total final energy consumption)': 'Renewable Energy (%)',
            'date': 'Year'
        }
    )
    fig_regional.write_html('output/regional_trends.html')
    
    # 3. Create a dashboard
    app = Dash(__name__)
    
    app.layout = html.Div([
        html.H1('Global Energy Transition Dashboard'),
        html.Div([
            dcc.Graph(figure=fig_transition),
            dcc.Graph(figure=fig_regional)
        ])
    ])
    
    app.run_server(debug=False, port=8050)
    
    return 'output/energy_transition.html', 'output/regional_trends.html'

@task
def generate_report(latest_data, transition_file, regional_file):
    """Generate a summary report"""
    report = f"""
    Global Energy Transition Analysis Report
    Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
    
    Key Statistics:
    --------------
    Total Countries Analyzed: {len(latest_data)}
    Global Average Renewable Energy Share: {latest_data['Renewable energy consumption (% of total final energy consumption)'].mean():.2f}%
    
    Top 5 Countries by Renewable Energy Share:
    ----------------------------------------
    {latest_data.nlargest(5, 'Renewable energy consumption (% of total final energy consumption)')[['country', 'Renewable energy consumption (% of total final energy consumption)']].to_string()}
    
    Top 5 Countries by Energy Transition Score:
    ----------------------------------------
    {latest_data.nlargest(5, 'Energy Transition Score')[['country', 'Energy Transition Score']].to_string()}
    
    Visualizations:
    --------------
    - Energy Transition Progress: {transition_file}
    - Regional Renewable Trends: {regional_file}
    """
    
    with open('output/energy_report.txt', 'w') as f:
        f.write(report)
    
    return 'output/energy_report.txt'

@flow(name="Global Energy Transition Analysis Pipeline")
def energy_pipeline():
    """Main pipeline flow"""
    # Fetch data
    raw_data = fetch_energy_data()
    
    # Process data
    processed_data, latest_data, regional_avg = process_data(raw_data)
    
    # Create visualizations
    transition_file, regional_file = create_visualizations(processed_data, latest_data, regional_avg)
    
    # Generate report
    report_file = generate_report(latest_data, transition_file, regional_file)
    
    print(f"Pipeline completed successfully. Report saved to: {report_file}")
    print(f"Visualizations saved in the 'output' directory")
    print("Dashboard available at http://localhost:8050")

def create_deployment():
    """Create a deployment for the pipeline"""
    energy_pipeline.serve(
        name="energy-analysis-deployment",
        work_queue_name="default",
    )

if __name__ == "__main__":
    if os.getenv("PREFECT_DEPLOYMENT"):
        create_deployment()
    else:
        energy_pipeline() 