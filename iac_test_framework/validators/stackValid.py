import pytest
import boto3
from botocore.exceptions import ClientError
import time
import json


# Utility Functions
def deploy_stack(template_path, parameters, stack_name):
    """Deploys a CloudFormation stack from a YAML template."""
    with open(template_path, 'r') as f:
        template_body = f.read()
    cf_client = boto3.client('cloudformation')
    cf_client.create_stack(
        StackName=stack_name,
        TemplateBody=template_body,
        Parameters=parameters,
        Capabilities=['CAPABILITY_IAM']
    )


def wait_for_stack(cf_client, stack_name, status, timeout=600):
    """Waits for the stack to reach a specified status."""
    start_time = time.time()
    while time.time() - start_time < timeout:
        try:
            stack = cf_client.describe_stacks(StackName=stack_name)['Stacks'][0]
            current_status = stack['StackStatus']
            if current_status == status:
                return stack
            elif current_status in ['CREATE_FAILED', 'ROLLBACK_COMPLETE', 'DELETE_FAILED']:
                raise Exception(f"Stack {stack_name} failed with status {current_status}")
            time.sleep(10)
        except ClientError as e:
            if 'does not exist' in str(e) and status == 'DELETE_COMPLETE':
                return
            raise
    raise TimeoutError(f"Stack {stack_name} did not reach {status} within {timeout} seconds")


def get_stack_outputs(stack):
    """Extracts outputs from the stack."""
    return {output['OutputKey']: output['OutputValue'] for output in stack.get('Outputs', [])}


def validate_ec2_instance(instance_id, expected_instance_type, expected_key_name, expected_sg_rules, expected_tags):
    """Validates EC2 instance properties."""
    ec2_client = boto3.client('ec2')
    instance = ec2_client.describe_instances(InstanceIds=[instance_id])['Reservations'][0]['Instances'][0]
    assert instance['State']['Name'] == 'running', "Instance is not running"
    assert instance['InstanceType'] == expected_instance_type, f"Expected instance type {expected_instance_type}"
    assert instance['KeyName'] == expected_key_name, f"Expected key name {expected_key_name}"
    assert instance['Tags'] == expected_tags, f"Expected tags {expected_tags}"
    sg_id = instance['SecurityGroups'][0]['GroupId']
    sg = ec2_client.describe_security_groups(GroupIds=[sg_id])['SecurityGroups'][0]
    assert sg['IpPermissions'] == expected_sg_rules, f"Expected security group rules {expected_sg_rules}"


# Pytest Fixture
@pytest.fixture
def deployed_stack(request):
    """Deploys and cleans up a CloudFormation stack."""
    template_path = request.param['template_path']
    parameters = request.param.get('parameters', [])
    stack_name = f"test-stack-{int(time.time())}"

    deploy_stack(template_path, parameters, stack_name)
    cf_client = boto3.client('cloudformation')
    stack = wait_for_stack(cf_client, stack_name, 'CREATE_COMPLETE')

    yield stack

    cf_client.delete_stack(StackName=stack_name)
    wait_for_stack(cf_client, stack_name, 'DELETE_COMPLETE')


# Test Class for EC2 Template
class TestEC2Deployment:
    @pytest.mark.parametrize('deployed_stack', [{
        'template_path': 'ec2_template.yaml',
        'parameters': [{'ParameterKey': 'KeyName', 'ParameterValue': 'my-key-pair'}]
    }], indirect=True)
    def test_stack_status(self, deployed_stack):
        """Validates stack creation status."""
        assert deployed_stack['StackStatus'] == 'CREATE_COMPLETE'

    @pytest.mark.parametrize('deployed_stack', [{
        'template_path': 'ec2_template.yaml',
        'parameters': [{'ParameterKey': 'KeyName', 'ParameterValue': 'my-key-pair'}]
    }], indirect=True)
    def test_outputs(self, deployed_stack):
        """Validates stack outputs."""
        outputs = get_stack_outputs(deployed_stack)
        assert 'InstanceId' in outputs
        assert 'PublicIP' in outputs
        assert 'PublicDNS' in outputs

    @pytest.mark.parametrize('deployed_stack', [{
        'template_path': 'ec2_template.yaml',
        'parameters': [{'ParameterKey': 'KeyName', 'ParameterValue': 'my-key-pair'}]
    }], indirect=True)
    def test_ec2_instance(self, deployed_stack):
        """Validates EC2 instance properties with defaults."""
        outputs = get_stack_outputs(deployed_stack)
        expected_sg_rules = [{
            'FromPort': 22,
            'ToPort': 22,
            'IpProtocol': 'tcp',
            'IpRanges': [{'CidrIp': '0.0.0.0/0'}]
        }]
        expected_tags = [{'Key': 'Name', 'Value': 'MyEC2Instance'}]
        validate_ec2_instance(
            outputs['InstanceId'],
            't2.micro',
            'my-key-pair',
            expected_sg_rules,
            expected_tags
        )