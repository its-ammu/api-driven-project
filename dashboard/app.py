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

# pipelines : [{\"id\": \"4265d3d9-26cc-42ac-8fb7-b8e786796584\", \"created\": \"2025-03-24T14:47:28.193399Z\", \"updated\": \"2025-03-24T14:47:28.193419Z\", \"name\": \"Global Energy Transition Analysis Pipeline\", \"tags\": [], \"labels\": {}}, {\"id\": \"32e6109b-56eb-4f79-ae9c-a5513e800495\", \"created\": \"2025-03-24T12:55:48.498668Z\", \"updated\": \"2025-03-24T12:55:48.498685Z\", \"name\": \"Simple Data Pipeline\", \"tags\": [], \"labels\": {}}]

@app.route('/')
def home():
    pipelines = get_pipelines()
    return render_template('index.html', pipelines=pipelines)

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

if __name__ == '__main__':
    app.run(debug=True)
