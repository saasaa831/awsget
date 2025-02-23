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
        Capabilities=['CAPABILITY_IAM', 'CAPABILITY_NAMED_IAM']
    )


def wait_for_stack(cf_client, stack_name, status, timeout=600):
    """Waits for the stack to reach a specified status."""
    start_time = time.time()
    while time.time() - start_time < timeout:
        try:
            stack = cf_client.describe_stacks(StackName=stack_name)['Stacks'][0]
            if stack['StackStatus'] == status:
                return stack
            elif stack['StackStatus'] in ['CREATE_FAILED', 'ROLLBACK_COMPLETE']:
                raise Exception(f"Stack {stack_name} failed with status {stack['StackStatus']}")
            time.sleep(10)
        except ClientError as e:
            if 'does not exist' in str(e) and status == 'DELETE_COMPLETE':
                return
            raise
    raise TimeoutError(f"Stack {stack_name} did not reach {status} within {timeout} seconds")


def get_stack_outputs(stack):
    """Extracts outputs from the stack."""
    return {output['OutputKey']: output['OutputValue'] for output in stack.get('Outputs', [])}


def start_step_function_execution(state_machine_arn):
    """Starts a Step Functions execution."""
    sfn_client = boto3.client('stepfunctions')
    response = sfn_client.start_execution(
        stateMachineArn=state_machine_arn,
        input=json.dumps({"example": "input"})
    )
    return response['executionArn']


def wait_for_step_function_execution(execution_arn, timeout=300):
    """Waits for the Step Functions execution to succeed."""
    sfn_client = boto3.client('stepfunctions')
    start_time = time.time()
    while time.time() - start_time < timeout:
        response = sfn_client.describe_execution(executionArn=execution_arn)
        status = response['status']
        if status == 'SUCCEEDED':
            return response
        elif status in ['FAILED', 'TIMED_OUT', 'ABORTED']:
            raise Exception(f"Execution {execution_arn} failed with status {status}")
        time.sleep(5)
    raise TimeoutError(f"Execution {execution_arn} did not succeed within {timeout} seconds")


def validate_ec2_instance(instance_id, expected_instance_type, expected_key_name):
    """Validates minimal EC2 instance properties."""
    ec2_client = boto3.client('ec2')
    instance = ec2_client.describe_instances(InstanceIds=[instance_id])['Reservations'][0]['Instances'][0]
    assert instance['State']['Name'] == 'running', "Instance is not running"
    assert instance['InstanceType'] == expected_instance_type, f"Expected {expected_instance_type}"
    assert instance['KeyName'] == expected_key_name, f"Expected key {expected_key_name}"


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


# Test Class
class TestStepFunctionDeployment:
    @pytest.mark.parametrize('deployed_stack', [{
        'template_path': 'stepfunction_template.yaml',
        'parameters': [{'ParameterKey': 'KeyName', 'ParameterValue': 'my-key-pair'}]
    }], indirect=True)
    def test_stack_status(self, deployed_stack):
        """Validates stack creation status."""
        assert deployed_stack['StackStatus'] == 'CREATE_COMPLETE', "Stack not in CREATE_COMPLETE status"

    @pytest.mark.parametrize('deployed_stack', [{
        'template_path': 'stepfunction_template.yaml',
        'parameters': [{'ParameterKey': 'KeyName', 'ParameterValue': 'my-key-pair'}]
    }], indirect=True)
    def test_step_function_execution(self, deployed_stack):
        """Validates Step Functions execution succeeds."""
        outputs = get_stack_outputs(deployed_stack)
        state_machine_arn = outputs['StateMachineArn']
        execution_arn = start_step_function_execution(state_machine_arn)
        execution = wait_for_step_function_execution(execution_arn)
        assert execution['status'] == 'SUCCEEDED', "Step Function execution did not succeed"
        assert execution['output'] == '"Hello, Step Functions!"', "Unexpected output"

    @pytest.mark.parametrize('deployed_stack', [{
        'template_path': 'stepfunction_template.yaml',
        'parameters': [{'ParameterKey': 'KeyName', 'ParameterValue': 'my-key-pair'}]
    }], indirect=True)
    def test_ec2_instance(self, deployed_stack):
        """Validates EC2 instance properties."""
        outputs = get_stack_outputs(deployed_stack)
        validate_ec2_instance(outputs['InstanceId'], 't2.micro', 'my-key-pair')

    @pytest.mark.parametrize('deployed_stack', [{
        'template_path': 'stepfunction_template.yaml',
        'parameters': [{'ParameterKey': 'KeyName', 'ParameterValue': 'my-key-pair'}]
    }], indirect=True)
    def test_stack_outputs(self, deployed_stack):
        """Validates stack outputs."""
        outputs = get_stack_outputs(deployed_stack)
        assert 'InstanceId' in outputs, "Missing InstanceId"
        assert 'PublicIP' in outputs, "Missing PublicIP"
        assert 'StateMachineArn' in outputs, "Missing StateMachineArn"

    @pytest.mark.parametrize('deployed_stack', [{
        'template_path': 'stepfunction_template.yaml',
        'parameters': [{'ParameterKey': 'KeyName', 'ParameterValue': 'my-key-pair'}]
    }], indirect=True)
    def test_stack_resources(self, deployed_stack):
        """Validates stack resources."""
        cf_client = boto3.client('cloudformation')
        resources = cf_client.describe_stack_resources(StackName=deployed_stack['StackName'])['StackResources']
        resource_types = {res['ResourceType'] for res in resources}
        expected_types = {
            'AWS::EC2::Instance',
            'AWS::EC2::SecurityGroup',
            'AWS::IAM::Role',
            'AWS::StepFunctions::StateMachine'
        }
        assert resource_types == expected_types, f"Expected resources {expected_types}, got {resource_types}"


# To validate an existing stack independently
def validate_existing_stack(stack_name):
    cf_client = boto3.client('cloudformation')
    sfn_client = boto3.client('stepfunctions')

    # Check stack status
    stack = cf_client.describe_stacks(StackName=stack_name)['Stacks'][0]
    assert stack['StackStatus'] == 'CREATE_COMPLETE', f"Stack status is {stack['StackStatus']}"

    # Get outputs and validate Step Functions
    outputs = get_stack_outputs(stack)
    execution_arn = start_step_function_execution(outputs['StateMachineArn'])
    execution = wait_for_step_function_execution(execution_arn)
    assert execution['status'] == 'SUCCEEDED', "Step Function execution failed"

    # Validate EC2
    validate_ec2_instance(outputs['InstanceId'], 't2.micro', 'my-key-pair')

    # Check stack resources
    resources = cf_client.describe_stack_resources(StackName=stack_name)['StackResources']
    resource_types = {res['ResourceType'] for res in resources}
    expected_types = {
        'AWS::EC2::Instance', 'AWS::EC2::SecurityGroup',
        'AWS::IAM::Role', 'AWS::StepFunctions::StateMachine'
    }
    assert resource_types == expected_types, "Resource mismatch"


if __name__ == "__main__":
    # Example: Validate an existing stack
    validate_existing_stack('my-existing-stack')