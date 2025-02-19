import boto3

AWS_REGION = "us-east-1"
# Initialize a Boto3 CloudFormation client
cf_client = boto3.client('cloudformation', region_name=AWS_REGION)

# Load your CloudFormation template
with open('eccreate.yaml', 'r') as template_file:
    template_body = template_file.read()

# Define stack parameters
stack_parameters = [
    {
        'ParameterKey': 'KeyName',
        'ParameterValue': 'your-key-pair-name'
    },
    {
        'ParameterKey': 'InstanceType',
        'ParameterValue': 't3.micro'
    },
    {
        'ParameterKey': 'VpcId',
        'ParameterValue': 'your-vpc-id'
    },
    {
        'ParameterKey': 'SubnetId',
        'ParameterValue': 'your-subnet-id'
    }
]

# Create the CloudFormation stack
try:
    response = cf_client.create_stack(
        StackName='EC_Creation_test',
        TemplateBody=template_body,
        Parameters=stack_parameters,
        Capabilities=['CAPABILITY_NAMED_IAM'],  # Include if your template involves IAM roles/policies
        OnFailure='ROLLBACK'  # Action to take if stack creation fails
    )
    print(f"Stack creation initiated: {response['StackId']}")
except Exception as e:
    print(f"Failed to create stack: {e}")
