import pytest
import boto3
import uuid
from botocore.exceptions import ClientError
from AWSTestCases.AWS_S3_Test import aws_s3_check_if_buckets_exist

# Create S3 client
s3 = boto3.client('s3')


def test_aws_s3_check_if_buckets_exist():
    assert aws_s3_check_if_buckets_exist(s3) == True


# tests/test_s3.py


def test_create_and_delete_s3_bucket():
    # Get the S3 client from our AWSClient fixture.
    # Generate a unique bucket name.
    bucket_name = f"test-bucket-{uuid.uuid4()}"
    AWS_REGION = "us-east-1"
    # Create the bucket. (For regions other than us-east-1, specify CreateBucketConfiguration)
    s3.create_bucket(Bucket=bucket_name)

    # Verify bucket creation by listing buckets.
    buckets = s3.list_buckets()['Buckets']
    print(buckets)
    assert any(bucket['Name'] == bucket_name for bucket in buckets), "Bucket creation failed"

    # Clean up: delete the bucket.
    s3.delete_bucket(Bucket='creating-new-bucket')
