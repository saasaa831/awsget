import yaml
from aws_client import AWSClient


class GenericValidator:
    def __init__(self, config):
        self.config = config
        self.client = AWSClient().get_service_client(config['client'])

    def get_resource_details(self, physical_id):
        method = getattr(self.client, self.config['describe_method'])
        response = method(**{self.config['id_param']: [physical_id]})
        if self.config['client'] == 'ec2':
            return response['Reservations'][0]['Instances'][0]
        elif self.config['client'] == 'autoscaling':
            return response['AutoScalingGroups'][0]
        elif self.config['client'] == 'elbv2':
            if 'LoadBalancers' in response:
                return response['LoadBalancers'][0]
            elif 'Listeners' in response:
                return response['Listeners'][0]
        raise NotImplementedError(f"Unsupported service: {self.config['client']}")

    def resolve_value(self, value, stack_resources):
        if isinstance(value, (str, int)):
            return str(value)
        elif isinstance(value, Ref):
            return stack_resources[value.logical_id]['PhysicalResourceId']
        elif isinstance(value, GetAtt):
            ref_resource = stack_resources[value.logical_id]
            ref_physical_id = ref_resource['PhysicalResourceId']
            ref_type = ref_resource['ResourceType']
            with open('config/aws_resources.yaml', 'r') as f:
                resource_config = yaml.safe_load(f)
            ref_config = resource_config[ref_type]
            ref_details = GenericValidator(ref_config).get_resource_details(ref_physical_id)
            attr_key = self.config['attribute_mapping'].get(value.attribute)
            return ref_details[attr_key]
        raise ValueError(f"Unsupported value type: {type(value)}")

    def validate(self, expected_properties, actual_details, stack_resources):
        # Validate properties
        global prop
        for prop, value in expected_properties.items():
            expected_value = self.resolve_value(value, stack_resources)
            actual_value = actual_details.get(self.config['property_mapping'].get(prop, prop))
            if expected_value != actual_value:
                raise AssertionError(f"Mismatch for {prop}: expected {expected_value}, got {actual_value}")

        for default_prop, default_value in self.config['defaults'].items():
            if prop not in expected_properties:
                actual_value = actual_details.get(default_prop)
                if isinstance(default_value, dict):
                    if actual_value != default_value:
                        raise AssertionError(
                            f"Default mismatch for {default_prop}: expected {default_value}, got {actual_value}")
                elif actual_value not in default_value:
                    raise AssertionError(
                        f"Default mismatch for {default_prop}: expected {default_value}, got {actual_value}")

        # Validate tags (if specified)
        if 'Tags' in expected_properties:
            actual_tags = {tag['Key']: tag['Value'] for tag in actual_details.get(self.config['tag_key'], [])}
            expected_tags = {tag['Key']: tag['Value'] for tag in expected_properties['Tags']}
            for key, value in expected_tags.items():
                if actual_tags.get(key) != value:
                    raise AssertionError(f"Tag mismatch for {key}: expected {value}, got {actual_tags.get(key)}")
