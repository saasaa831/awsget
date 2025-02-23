import pytest
from validators.aws_client import AWSClient
from validators.parser import parse_yaml
from validators.utils import load_resource_config


@pytest.fixture(scope="session")
def aws_client():
    return AWSClient()


@pytest.fixture(scope="session")
def resource_config():
    return load_resource_config()


@pytest.fixture
def stack_details():
    return {
        'abc1': {'name': 'stack-abc1', 'file': 'templates/abc1.yaml'},
        'abc2': {'name': 'stack-abc2', 'file': 'templates/abc2.yaml'}
    }
