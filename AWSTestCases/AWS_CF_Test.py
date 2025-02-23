# Standard library modules


# Third-party modules
import boto3
import json
from botocore.exceptions import ClientError

AWS_REGION = "us-west-1"

SG_STACK_NAME = "simple-sg-stack"
SG_TEMPLATE = r"""AWSTemplateFormatVersion: '2010-09-09'
Description: 'AWS CloudFormation Template to create an EC2 instance with SSH access'

Parameters:
  KeyName:
    Description: Name of an existing EC2 KeyPair to enable SSH access
    Type: AWS::EC2::KeyPair::KeyName
    ConstraintDescription: Must be the name of an existing EC2 KeyPair
  InstanceType:
    Description: EC2 instance type
    Type: String
    Default: t2.micro
    AllowedValues:
      - t2.micro
      - t2.small
      - t2.medium
    ConstraintDescription: Must be a valid EC2 instance type
  SSHLocation:
    Description: IP address range that can SSH into the instance (e.g., your IP)
    Type: String
    MinLength: '9'
    MaxLength: '18'
    Default: '0.0.0.0/0'
    AllowedPattern: '(\d{1,3})\.(\d{1,3})\.(\d{1,3})\.(\d{1,3})/(\d{1,2})'
    ConstraintDescription: Must be a valid IP CIDR range (e.g., x.x.x.x/x)
  LatestAmiId:
    Description: Latest Amazon Linux 2 AMI from SSM Parameter Store
    Type: 'AWS::SSM::Parameter::Value<AWS::EC2::Image::Id>'
    Default: '/aws/service/ami-amazon-linux-latest/amzn2-ami-hvm-x86_64-gp2'

Resources:
  EC2Instance:
    Type: AWS::EC2::Instance
    Properties:
      InstanceType: !Ref InstanceType
      KeyName: !Ref KeyName
      ImageId: !Ref LatestAmiId
      SecurityGroups:
        - !Ref InstanceSecurityGroup
      Tags:
        - Key: Name
          Value: MyEC2Instance

  InstanceSecurityGroup:
    Type: AWS::EC2::SecurityGroup
    Properties:
      GroupDescription: Enable SSH access via port 22
      SecurityGroupIngress:
        - IpProtocol: tcp
          FromPort: 22
          ToPort: 22
          CidrIp: !Ref SSHLocation

Outputs:
  InstanceId:
    Description: Instance ID of the newly created EC2 instance
    Value: !Ref EC2Instance
  PublicIP:
    Description: Public IP address of the EC2 instance
    Value: !GetAtt EC2Instance.PublicIp
  PublicDNS:
    Description: Public DNS name of the EC2 instance
    Value: !GetAtt EC2Instance.PublicDnsName"""


class CFClient:
    def __init__(self, AWS_REGION):
        self.AWS_REGION = AWS_REGION
        self.client = boto3.client('cloudformation', region_name=self.AWS_REGION)
        self.s3Client = boto3.client('s3', region_name=self.AWS_REGION)
        self.ec2Client = boto3.client('ec2', region_name=self.AWS_REGION)
        self.resource = boto3.resource('cloudformation', region_name=self.AWS_REGION)

    def create_simple_instance(self):
        """Test that we can create a simple CloudFormation stack that imports values from an existing CloudFormation stack"""

        self.client.create_stack(StackName=SG_STACK_NAME, TemplateBody=SG_TEMPLATE, Parameters=[
            {
                "ParameterKey": "KeyName",
                "ParameterValue": "KeyEC2"
            },
            {
                "ParameterKey": "InstanceType",
                "ParameterValue": "t2.micro"
            },
            {
                "ParameterKey": "SSHLocation",
                "ParameterValue": "0.0.0.0/0"
            }
        ])
        response = self.client.describe_stacks()
        print("Stacks", response)
        stack_info = response["Stacks"]
        print(1, len(stack_info))
        print("StackName", stack_info[0])

    def make_chained_depends_on_template(self):
        depends_on_template_linked_dependencies = {
            "AWSTemplateFormatVersion": "2010-09-09",
            "Resources": {
                "Bucket0": {  # Define the first bucket (Bucket0)
                    "Type": "AWS::S3::Bucket",
                    "Properties": {"BucketName": "test-bucket-0-us-east-1"},
                }
            },
        }

        '''for i in range(1, 10):  # Ensure all buckets are defined properly
            depends_on_template_linked_dependencies["Resources"]["Bucket" + str(i)] = {
                "Type": "AWS::S3::Bucket",
                "Properties": {"BucketName": "test-bucket-" + str(i) + "-us-east-1"},
                "DependsOn": ["Bucket" + str(i - 1)],  # Ensure proper chaining
            }'''

        return json.dumps(depends_on_template_linked_dependencies)

    def create_chained_depends_on_stack(self):
        gTemplatex = self.make_chained_depends_on_template()
        print(gTemplatex)

        self.client.create_stack(
            StackName="linked-depends-on-test",
            TemplateBody=gTemplatex
        )

        response = self.client.describe_stacks()
        print("Stacks", response)

        bucket_response = self.s3Client.list_buckets()["Buckets"]
        print(bucket_response)

        gbucket = sorted([bucket["Name"] for bucket in bucket_response]) == [
            "test-bucket-" + str(i) + "-us-east-1" for i in range(10)
        ]
        print(gbucket)

    def getAclperm(self):
        result = self.s3Client.list_table_buckets(Bucket="test-bucket-0-us-east-1")
        print(result)

    def describe_instance(self):
        response = self.ec2Client.describe_instances()
        print(response['Reservations'][0]['Instances'][0]["SecurityGroups"][0]["GroupId"])
        '''securityG = response['Reservations'][0]['Instances'][0]["SecurityGroups"][0]["GroupId"]
        sgx = self.client.describe_security_groups()
        print(sgx['SecurityGroups'][0]['SecurityGroupArn'])'''
        return response['Reservations'][0]['Instances']


getec2 = CFClient("us-east-1")
getec2.describe_instance()
