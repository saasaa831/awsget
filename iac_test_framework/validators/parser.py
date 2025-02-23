import yaml


class Ref:
    def __init__(self, logical_id):
        self.logical_id = logical_id


class GetAtt:
    def __init__(self, logical_id, attribute):
        self.logical_id = logical_id
        self.attribute = attribute


def ref_constructor(loader, node):
    return Ref(loader.construct_scalar(node))


def getatt_constructor(loader, node):
    values = loader.construct_sequence(node)
    return GetAtt(values[0], values[1])


yaml.add_constructor('!Ref', ref_constructor)
yaml.add_constructor('!GetAtt', getatt_constructor)


def parse_yaml(file_path):
    with open(file_path, 'r') as file:
        return yaml.load(file, Loader=yaml.Loader)
