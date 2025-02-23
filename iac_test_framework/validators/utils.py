import yaml


def load_resource_config():
    with open('config/aws_resources.yaml', 'r') as f:
        return yaml.safe_load(f)
