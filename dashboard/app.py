from flask import Flask, render_template, jsonify
import requests
import json
from datetime import datetime
from collections import Counter

app = Flask(__name__)

def get_pipelines():
    response = requests.get('https://es3ozkq7i8.execute-api.us-east-1.amazonaws.com/dev/data/pipeline')
    return response.json()

def get_pipeline_details(pipeline_id):
    response = requests.get(f'https://es3ozkq7i8.execute-api.us-east-1.amazonaws.com/dev/data/pipeline/status?id={pipeline_id}')
    return response.json()

def get_ml_pipelines():
    response = requests.get('https://es3ozkq7i8.execute-api.us-east-1.amazonaws.com/dev/ml/pipeline')
    print("ML Pipelines:", response.json())
    return response.json()

def get_ml_pipeline_details(pipeline_id):
    response = requests.get(f'https://es3ozkq7i8.execute-api.us-east-1.amazonaws.com/dev/ml/pipeline/status?pipeline_id={pipeline_id}')
    return response.json()

def analyze_pipeline_runs(runs):
    # Convert string timestamps to datetime objects
    for run in runs:
        run['created'] = datetime.fromisoformat(run['created'].replace('Z', '+00:00'))
        run['updated'] = datetime.fromisoformat(run['updated'].replace('Z', '+00:00'))
        if run['start_time']:
            run['start_time'] = datetime.fromisoformat(run['start_time'].replace('Z', '+00:00'))
        if run['end_time']:
            run['end_time'] = datetime.fromisoformat(run['end_time'].replace('Z', '+00:00'))

    # Calculate statistics
    total_runs = len(runs)
    status_counts = Counter(run['state_type'] for run in runs)
    avg_run_time = sum(run['total_run_time'] for run in runs) / total_runs if total_runs > 0 else 0
    success_rate = (status_counts['COMPLETED'] / total_runs * 100) if total_runs > 0 else 0
    
    # Get latest run
    latest_run = max(runs, key=lambda x: x['created']) if runs else None
    
    # Get error types
    error_types = Counter(run['state']['message'] for run in runs if run['state_type'] in ['FAILED', 'CRASHED'])
    
    return {
        'total_runs': total_runs,
        'status_counts': dict(status_counts),
        'avg_run_time': round(avg_run_time, 2),
        'success_rate': round(success_rate, 2),
        'latest_run': latest_run,
        'error_types': dict(error_types),
        'runs': sorted(runs, key=lambda x: x['created'], reverse=True)
    }

def analyze_ml_pipeline_runs(executions):
    if not executions or 'PipelineExecutionSummaries' not in executions:
        return {
            'total_runs': 0,
            'status_counts': {},
            'avg_run_time': 0,
            'success_rate': 0,
            'latest_run': None,
            'error_types': {},
            'runs': []
        }
    
    runs = executions['PipelineExecutionSummaries']
    
    # Calculate statistics
    total_runs = len(runs)
    status_counts = Counter(run['PipelineExecutionStatus'] for run in runs)
    success_rate = (status_counts['Succeeded'] / total_runs * 100) if total_runs > 0 else 0
    
    # Get latest run
    latest_run = max(runs, key=lambda x: x['StartTime']) if runs else None
    
    # Get error types
    error_types = Counter(run['PipelineExecutionStatus'] for run in runs if run['PipelineExecutionStatus'] not in ['Succeeded'])
    
    return {
        'total_runs': total_runs,
        'status_counts': dict(status_counts),
        'success_rate': round(success_rate, 2),
        'latest_run': latest_run,
        'error_types': dict(error_types),
        'runs': sorted(runs, key=lambda x: x['StartTime'], reverse=True)
    }

@app.route('/')
def home():
    data_pipelines = get_pipelines()
    ml_pipelines = get_ml_pipelines()
    return render_template('index.html', 
                         data_pipelines=data_pipelines,
                         ml_pipelines=ml_pipelines)

@app.route('/pipeline/<pipeline_id>')
def pipeline_details(pipeline_id):
    runs = get_pipeline_details(pipeline_id)
    if not runs:
        return "Pipeline not found", 404
    
    # Get pipeline info from the first run
    pipeline_info = {
        'id': runs[0]['flow_id'],
        'name': runs[0]['flow_name'],
        'version': runs[0]['flow_version']
    }
    
    # Analyze the runs
    analysis = analyze_pipeline_runs(runs)
    
    return render_template('pipeline_details.html', 
                         pipeline=pipeline_info,
                         analysis=analysis)

@app.route('/ml/pipeline/<pipeline_id>')
def ml_pipeline_details(pipeline_id):
    executions = get_ml_pipeline_details(pipeline_id)
    if not executions or 'PipelineExecutionSummaries' not in executions:
        return "Pipeline not found", 404
    
    # Get pipeline info from the first execution
    pipeline_info = {
        'id': executions['PipelineExecutionSummaries'][0]['PipelineExecutionDetails']['PipelineArn'].split('/')[-1],
        'name': executions['PipelineExecutionSummaries'][0]['PipelineExecutionDetails']['PipelineArn'].split('/')[-1],
        'display_name': executions['PipelineExecutionSummaries'][0]['PipelineExecutionDisplayName']
    }
    
    # Analyze the executions
    analysis = analyze_ml_pipeline_runs(executions)
    
    return render_template('ml_pipeline_details.html', 
                         pipeline=pipeline_info,
                         analysis=analysis)

if __name__ == '__main__':
    app.run(debug=True)
