import boto3
import requests
import json

def get_secret(secret_name):
    client = boto3.client('secretsmanager')
    response = client.get_secret_value(SecretId=secret_name)
    return json.loads(response['SecretString'])['token']

def get_flowruns(id):
    api_key = get_secret('prefect/api-key')
    account_id = "c1b7590b-f2c7-4385-ab75-f61175b1a0aa"
    workspace_id = "ad1def85-680c-408b-8a1b-aa89cc07692f"
    url = f"https://api.prefect.cloud/api/accounts/{account_id}/workspaces/{workspace_id}/flow_runs/filter"
    body = {
    "flows": {
        "id": {
            "any_" : [
                id
            ]
        } 
    }
}
    headers = {
        'Authorization': f'Bearer {api_key}'
    }
    response = requests.post(url, headers=headers, json=body)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error: {response.status_code}")
        return None

def lambda_handler(event, context):
    id = event.get('queryStringParameters').get('id')
    if not id:
        return {
            'statusCode': 400,
            'body': json.dumps('Missing id parameter in query string')
        }
    pipelines = get_flowruns(id)
    return {
        'statusCode': 200,
        'body': json.dumps(pipelines)
    }
