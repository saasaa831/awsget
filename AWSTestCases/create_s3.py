import boto3


def create_s3_bucket(bucket_name):
    try:
        AWS_REGION = "us-east-1"
        s3_client = boto3.client('s3', region_name=AWS_REGION)
        # Use the correct parameter "Bucket"
        s3_client.create_bucket(Bucket=bucket_name)
        print(f"Successfully created S3 Bucket: '{bucket_name}'!")
    except Exception as e:
        print(f"Failed to create S3 bucket: {e}")


create_s3_bucket('creating-new-bucket')
