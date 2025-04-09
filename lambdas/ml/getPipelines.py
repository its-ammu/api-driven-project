import boto3
import json

def get_sagemaker_pipelines():
    sagemaker_client = boto3.client('sagemaker')
    response = sagemaker_client.list_pipelines()
    pipelines = response['PipelineSummaries']
    while 'NextToken' in response:
        response = sagemaker_client.list_pipelines(NextToken=response['NextToken'])
        pipelines.extend(response['PipelineSummaries'])
    
    print(pipelines)
    return pipelines


def lambda_handler(event, context):
    try:
        pipelines = get_sagemaker_pipelines()
        # error : Object of type datetime is not JSON serializable. Modify datetime to string
        for pipeline in pipelines:
            pipeline['CreationTime'] = pipeline['CreationTime'].isoformat()
            pipeline['LastModifiedTime'] = pipeline['LastModifiedTime'].isoformat()
            if "LastExecutionTime" in pipeline:
                pipeline['LastExecutionTime'] = pipeline['LastExecutionTime'].isoformat()

        return {
            'statusCode': 200,
            'body': json.dumps(pipelines)
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'body': str(e)
        }
