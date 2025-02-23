import boto3


class AWSClient:
    def __init__(self):
        self.cfn_client = boto3.client('cloudformation')
        self.logs_client = boto3.client('logs')

    def get_stack_resources(self, stack_name):
        response = self.cfn_client.describe_stack_resources(StackName=stack_name)
        return {res['LogicalResourceId']: res for res in response['StackResources']}

    def get_stack_status(self, stack_name):
        response = self.cfn_client.describe_stacks(StackName=stack_name)
        return response['Stacks'][0]['StackStatus']

    def get_stack_events(self, stack_name):
        response = self.cfn_client.describe_stack_events(StackName=stack_name)
        return response['StackEvents']

    def get_service_client(self, service_name):
        return boto3.client(service_name)

    def get_log_groups(self, stack_name):
        response = self.logs_client.describe_log_groups(logGroupNamePrefix=f"/aws/cloudformation/{stack_name}")
        return response['logGroups']
