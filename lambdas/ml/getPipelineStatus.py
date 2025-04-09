import boto3
import json

def get_sagemaker_pipeline_executions(pipeline_id):
    sagemaker_client = boto3.client('sagemaker')
    response = sagemaker_client.list_pipeline_executions(PipelineName=pipeline_id)
    print(response)
    return response

def get_execution_details(execution_arn):
    sagemaker_client = boto3.client('sagemaker')
    response = sagemaker_client.describe_pipeline_execution(PipelineExecutionArn=execution_arn)
    return response


def lambda_handler(event, context):
    try:
        if "pipeline_id" not in event['queryStringParameters']:
            return {
                'statusCode': 400,
                'body': "pipeline_id is required"
            }
        pipeline_id = event['queryStringParameters']['pipeline_id']
        pipeline_details = get_sagemaker_pipeline_executions(pipeline_id)
        for execution in pipeline_details['PipelineExecutionSummaries']:
            if "StartTime" in execution:
                execution['StartTime'] = execution['StartTime'].isoformat() if execution['StartTime'] else None
            print(f"Parsing Execution : {execution['PipelineExecutionArn']}")
            execution_details = get_execution_details(execution['PipelineExecutionArn'])
            execution['PipelineExecutionDetails'] = execution_details
            execution['PipelineExecutionDetails']['CreationTime'] = execution['PipelineExecutionDetails']['CreationTime'].isoformat() if execution['PipelineExecutionDetails']['CreationTime'] else None
            execution['PipelineExecutionDetails']['LastModifiedTime'] = execution['PipelineExecutionDetails']['LastModifiedTime'].isoformat() if execution['PipelineExecutionDetails']['LastModifiedTime'] else None

        return {
            'statusCode': 200,
            'body': json.dumps(pipeline_details)
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'body': str(e)
        }
