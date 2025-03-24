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
def fetch_world_bank_data():
    """Fetch energy consumption data from World Bank API"""
    base_url = "http://api.worldbank.org/v2/country/all/indicator"
    indicators = {
        'EG.USE.PCAP.KG.OE': 'Energy use per capita',
        'EG.FEC.RNEW.ZS': 'Renewable energy consumption',
        'EG.USE.COMM.FO.ZS': 'Fossil fuel energy consumption'
    }
    
    all_data = []
    
    for indicator_id, indicator_name in indicators.items():
        url = f"{base_url}/{indicator_id}?format=json&per_page=1000"
        response = requests.get(url)
        
        if response.status_code == 200:
            data = response.json()
            if isinstance(data, list) and len(data) > 1:
                for item in data[1]:  # Skip the metadata in data[0]
                    if item.get('value') is not None:  # Only include non-null values
                        all_data.append({
                            'country': item['country']['value'],
                            'country_code': item['countryiso3code'],
                            'date': item['date'],
                            indicator_name: item['value']
                        })
        else:
            print(f"Error fetching {indicator_name}: {response.status_code}")
    
    # Convert to DataFrame
    df = pd.DataFrame(all_data)
    
    # Pivot the data to get all indicators in columns
    df_pivot = df.pivot_table(
        index=['country', 'country_code', 'date'],
        values=list(indicators.values()),
        aggfunc='first'
    ).reset_index()
    
    return df_pivot

@task
def process_data(df):
    """Process and clean the energy data"""
    # Calculate year-over-year changes
    df['Renewable Growth'] = df.groupby('country')['Renewable energy consumption'].pct_change()
    
    # Calculate energy transition score (higher renewable %, lower fossil fuel %)
    df['Energy Transition Score'] = (
        df['Renewable energy consumption'] -
        df['Fossil fuel energy consumption']
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
        x='Fossil fuel energy consumption',
        y='Renewable energy consumption',
        size='Energy use per capita',
        color='Region',
        hover_data=['country'],
        title='Energy Transition Progress by Country',
        labels={
            'Fossil fuel energy consumption': 'Fossil Fuel Consumption (%)',
            'Renewable energy consumption': 'Renewable Energy (%)',
            'Energy use per capita': 'Energy Use per Capita (kg of oil equivalent)'
        }
    )
    fig_transition.write_html('output/energy_transition.html')
    
    # 2. Regional Renewable Energy Trends
    fig_regional = px.line(
        regional_avg,
        x='date',
        y='Renewable energy consumption',
        color='Region',
        title='Regional Renewable Energy Adoption Trends',
        labels={
            'Renewable energy consumption': 'Renewable Energy (%)',
            'date': 'Year'
        }
    )
    fig_regional.write_html('output/regional_trends.html')
    
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
    Global Average Renewable Energy Share: {latest_data['Renewable energy consumption'].mean():.2f}%
    
    Top 5 Countries by Renewable Energy Share:
    ----------------------------------------
    {latest_data.nlargest(5, 'Renewable energy consumption')[['country', 'Renewable energy consumption']].to_string()}
    
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
    raw_data = fetch_world_bank_data()
    
    # Process data
    processed_data, latest_data, regional_avg = process_data(raw_data)
    
    # Create visualizations
    transition_file, regional_file = create_visualizations(processed_data, latest_data, regional_avg)
    
    # Generate report
    report_file = generate_report(latest_data, transition_file, regional_file)
    
    print(f"Pipeline completed successfully. Report saved to: {report_file}")
    print(f"Visualizations saved in the 'output' directory")

if __name__ == "__main__":
    energy_pipeline() 