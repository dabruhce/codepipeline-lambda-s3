from __future__ import print_function
from boto3.session import Session
import boto3
import traceback

print('Loading codepipeline-lambda-s3 function.')


def get_codepipeline_client():
    return boto3.client('codepipeline')


def get_input_artifact(artifacts):
    """Returns the input artifact from the 'artifacts' list.

    Args:
        artifacts: The list of artifacts available to the function
    Returns:
        The bucket and key of the artifact in a dict.
    Raises:
        Exception: If no artifact is found or there are too many artifacts.
    """
    if not len(artifacts) == 1:
        raise ValueError(
            'Expected one and only one input artifact, got ' + str(artifacts))

    artifact = artifacts[0]
    location = artifact['location']
    if not location['type'] == 'S3':
        raise ValueError(
            'Artifact must be in S3, got ' + str(location['type']))
    bucket = location['s3Location']['bucketName']
    key = location['s3Location']['objectKey']
    return {'Bucket': bucket, 'Key': key}


def put_job_success(job, message):
    """Notify CodePipeline of a successful job

    Args:
        job: The CodePipeline job ID
        message: A message to be logged relating to the job status
    Raises:
        Exception: Any exception thrown by .put_job_success_result()
    """
    print('Putting job success')
    print(message)
    get_codepipeline_client.put_job_success_result(jobId=job)


def put_job_failure(job, message):
    """Notify CodePipeline of a failed job

    Args:
        job: The CodePipeline job ID
        message: A message to be logged relating to the job status
    Raises:
        Exception: Any exception thrown by .put_job_failure_result()
    """
    print('Putting job failure')
    print(message)
    get_codepipeline_client.put_job_failure_result(
        jobId=job, failureDetails={'message': message, 'type': 'JobFailed'})


def parse_job_data(job_data):
    """Decodes the JSON user parameters and validates the required properties.

    Args:
        job_data: Structure containing parameters for this invocation.
    Returns:
        The JSON parameters decoded as a dictionary.
    Raises:
        Exception: The JSON can't be decoded or a property is missing.
    """
    credentials = job_data['artifactCredentials']
    configuration = job_data['actionConfiguration']['configuration']
    inputs = job_data['inputArtifacts']
    # The user parameters should be a string which is the name of the
    # function to update.
    if 'UserParameters' in configuration:
        function = configuration['UserParameters']
        if len(function) < 1:
            msg = 'Lambda function name is blank.'
            print(msg)
            raise ValueError(msg)
    else:
        msg = 'Must be given a Lambda function name in user parameters.'
        print(msg)
        raise ValueError(msg)
    print("Got function name: " + function)
    return credentials, inputs, function


def setup_session_client(credentials, service):
    """Creates a boto client client

    Uses the credentials passed in the event by CodePipeline. These
    credentials can be used to access the artifact bucket.
    Args:
        job_data: The job data structure
    Returns:
        An S3 client with the appropriate credentials
    """
    key_id = credentials['accessKeyId']
    key_secret = credentials['secretAccessKey']
    session_token = credentials['sessionToken']

    session = Session(
            aws_access_key_id=key_id,
            aws_secret_access_key=key_secret,
            aws_session_token=session_token)
    return session.client(
        service, config=botocore.client.Config(signature_version='s3v4'))


def lambda_handler(event, context):
    """The Lambda function handler

    Args:
        event: The event passed by Lambda
        context: The context passed by Lambda
    """
    try:
        # Extract the Job ID
        job_id = event['CodePipeline.job']['id']
        print('CodePipeline Job ID: ' + str(job_id))

        # Extract the Job Data
        job_data = event['CodePipeline.job']['data']

        # Extract the params
        credentials, inputs, function = parse_job_data(job_data)

        artifact = get_input_artifact(inputs)
        message = 'Lambda function %s with artifact %s/%s: ' % (
                function, artifact['Bucket'], artifact['Key'])
        print('About to update ' + message)
        lambda_client = boto3.client('lambda')
        response = lambda_client.update_function_code(
                    FunctionName=function,
                    S3Key=artifact['Key'], S3Bucket=artifact['Bucket'])
        put_job_success(job_id, message)

    except Exception as e:
        # If any other exceptions which we didn't expect are raised
        # then fail the job and log the exception message.
        print('Function failed due to exception.')
        print(e)
        traceback.print_exc()
        put_job_failure(job_id, 'Function exception: ' + str(e))

    print('Function complete.')
    return "Complete."
