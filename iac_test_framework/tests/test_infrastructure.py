import pytest
from validators.parser import parse_yaml
from validators.validator import GenericValidator


def test_stack_status(aws_client, stack_details):
    for stack_key, details in stack_details.items():
        status = aws_client.get_stack_status(details['name'])
        assert status == 'CREATE_COMPLETE', f"Stack {details['name']} is not CREATE_COMPLETE: {status}"
        events = aws_client.get_stack_events(details['name'])
        failures = [e for e in events if 'FAILED' in e['ResourceStatus']]
        assert not failures, f"Stack {details['name']} has failed events: {failures}"
        log_groups = aws_client.get_log_groups(details['name'])
        print(f"Log groups for {details['name']}: {log_groups}")


@pytest.mark.parametrize("stack_key", ['abc1', 'abc2'])
def test_resources_validation(aws_client, resource_config, stack_details, stack_key):
    details = stack_details[stack_key]
    template = parse_yaml(details['file'])
    resources = template['Resources'] if 'Resources' in template else template
    stack_resources = aws_client.get_stack_resources(details['name'])

    for logical_id, resource_def in resources.items():
        physical_id = stack_resources[logical_id]['PhysicalResourceId']
        resource_type = resource_def['Type']
        if resource_type not in resource_config:
            pytest.skip(f"No configuration for {resource_type}")
        validator = GenericValidator(resource_config[resource_type])
        actual_details = validator.get_resource_details(physical_id)
        expected_properties = resource_def.get('Properties', {})
        if 'Configuration' in resource_def:
            expected_properties.update(
                resource_def['Configuration'].get(resource_type.split('::')[-1], {}).get('Properties', {}))
        validator.validate(expected_properties, actual_details, stack_resources)
