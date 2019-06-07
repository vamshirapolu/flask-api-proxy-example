import boto3
import os
import pprint
import argparse
import sys

client = boto3.client('lambda')

# For argument reference
parser = argparse.ArgumentParser()
parser.add_argument('--function-name', help='Lambda Function Name', required=True)
parser.add_argument('--function-handler', help='Lambda Function Handler', required=True)
parser.add_argument('--function-zip-file', help='Lambda Function Zip File Path', required=True)
parser.add_argument('--lambda-role', help='Lambda Role ARN', required=True)
parser.add_argument('--lambda_alias', help='Lambda Alias Name', required=True)
parser.add_argument('--environment', help='Environment', required=True)
parser.add_argument('--publish-lambda', help='Flag to decide on publish the lambda', required=True)
parser.add_argument('--lambda-runtime', help='Lambda runtime', required=True)
parser.add_argument('--s3-build-artifacts-bucket', help='S3 build artifacts bucket where the code archive will be copied and used to update the lambda function code', required=True)

args = parser.parse_args()

s3_build_artifacts_bucket = args.s3_build_artifacts_bucket
function_name = args.function_name
is_publish = str(args.publish_lambda).lower() == 'true'
alias_name = args.lambda_alias
environment_name = args.environment
lambda_role = args.lambda_role
lambda_handler = args.function_handler
lambda_description = 'Data ETL Stream (Build:{build}, Commit:{commit})'.format(
    build=os.environ['TRAVIS_BUILD_NUMBER'], commit=os.environ['TRAVIS_COMMIT'])
lambda_function_zip_file = args.function_zip_file
lambda_runtime = args.lambda_runtime

# retuens the lambda function zip bytes
def get_lambda_function_bytes(function_zip):
    build_dir = os.environ['TRAVIS_BUILD_DIR']
    in_file = open(build_dir + '/' + function_zip, 'rb')
    zip_bytes = in_file.read()
    in_file.close()
    return zip_bytes
    
# Uploading lambda code archive to S3
s3_client = boto3.client('s3')
s3_key = 'support_files/build_artifacts/' + lambda_function_zip_file.split('/', 1)[-1]
print('Uploading build artifact to s3://' + s3_build_artifacts_bucket + '/' + s3_key)
response = s3_client.put_object(
    Bucket=s3_build_artifacts_bucket,
    Key=s3_key,
    Metadata={
        'ingestion_version': os.environ['TRAVIS_COMMIT'],
        'build_number': os.environ['TRAVIS_BUILD_NUMBER']
    },
    ContentType='application/zip',
    Body=get_lambda_function_bytes(lambda_function_zip_file)
)
s3_version = response.get('VersionId')
print('S3 artifact version: {}'.format(s3_version))

try:
    # checks if the lambda function is already exists
    response = client.get_function(
        FunctionName=function_name,
        Qualifier='$LATEST'
    )
    print("Function {} already exists, updating.".format(function_name))
    
    # updating the function configuration
    response = client.update_function_configuration(
        FunctionName=function_name,
        Role=lambda_role,
        Handler=lambda_handler,
        Description=lambda_description,
        Runtime=lambda_runtime
    )
    print("Updated configuration of function: {function_name}.".format(function_name=response.get('FunctionName')))

    # updating the function code
    response = client.update_function_code(
        FunctionName=function_name,
        S3Bucket=s3_build_artifacts_bucket,
        S3Key=s3_key,
        S3ObjectVersion=s3_version,
        Publish=is_publish
    )
    print("Updated code of function: {function_name} [Version: {version}].".format(
        function_name=response.get('FunctionName'), version=response.get('Version')))

    if(is_publish):
        # capturing the function version if it was published 
        published_version = response.get('Version')
        try:
            # checking if the alias is already exist?
            response = client.get_alias(
                FunctionName=function_name,
                Name=alias_name
            )
            print("Alias {alias} already exists for function {function}, updating.".format(
                function=function_name, alias=alias_name))
            
            revision_id = response.get('RevisionId')
            # updating the alias
            response = client.update_alias(
                FunctionName=function_name,
                Name=alias_name,
                FunctionVersion=published_version,
                Description='Alias {alias} on version {version}'.format(
                    alias=alias_name, version=published_version),
                # passing the revision id to only update the alias if the revision ID matches the ID that's specified.
                RevisionId=revision_id
            )
        except client.exceptions.ResourceNotFoundException as exp:
            print("Alias {alias} not exists for function {function}, creating.".format(
                function=function_name, alias=alias_name))
            # creating the alias since alias was not exist
            response = client.create_alias(
                FunctionName=function_name,
                Name=alias_name,
                FunctionVersion=published_version,
                Description='Alias {alias} on version {version}'.format(
                    alias=alias_name, version=published_version)
            )
        except Exception as exp:
            print(exp)
            raise exp
except client.exceptions.ResourceNotFoundException as exp:
    print("Function {} doesn't exists, Should be created by manual or using the terraform.".format(function_name))
    sys.exit(1)
except Exception as exp:
    print(exp)
    sys.exit(1)

