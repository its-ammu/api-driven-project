from prefect import flow, task
import pandas as pd
import numpy as np
from datetime import datetime
from prefect.deployments import Deployment
from prefect.infrastructure.docker import DockerContainer
import os

@task
def generate_data():
    """Generate sample data"""
    np.random.seed(42)
    data = {
        'date': pd.date_range(start='2024-01-01', periods=100),
        'value': np.random.normal(100, 15, 100)
    }
    return pd.DataFrame(data)

@task
def process_data(df):
    """Process the data by adding derived columns"""
    df['rolling_mean'] = df['value'].rolling(window=7).mean()
    df['is_above_mean'] = df['value'] > df['value'].mean()
    return df

@task
def save_data(df):
    """Save the processed data"""
    output_file = f"processed_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    df.to_csv(output_file, index=False)
    return output_file

@flow(name="Simple Data Pipeline")
def data_pipeline():
    """Main pipeline flow"""
    # Generate data
    raw_data = generate_data()
    
    # Process data
    processed_data = process_data(raw_data)
    
    # Save results
    output_file = save_data(processed_data)
    
    print(f"Pipeline completed successfully. Output saved to: {output_file}")

def create_deployment():
    """Create a deployment for the pipeline"""
    docker_container = DockerContainer(
        image="prefecthq/prefect:2-python3.10",
        image_pull_policy="ALWAYS",
        auto_remove=True,
    )
    
    deployment = Deployment.build_from_flow(
        flow=data_pipeline,
        name="data-pipeline-deployment",
        infrastructure=docker_container,
        work_queue_name="default",
    )
    deployment.apply()

if __name__ == "__main__":
    if os.getenv("PREFECT_DEPLOYMENT"):
        create_deployment()
    else:
        data_pipeline() 