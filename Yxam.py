'''import yaml


def validate_yaml(file_path):
    """
    Validates the YAML file syntax.
    :param file_path: Path to the YAML file.
    :return: Parsed YAML content if valid; None if invalid.
    """
    try:
        with open(file_path, 'r') as file:
            content = yaml.safe_load(file)
        print(f"'{file_path}' is valid.")
        return content
    except yaml.YAMLError as e:
        print(f"Error in '{file_path}': {e}")
        return None


def compare_yaml_content(content1, content2):
    """
    Compares two YAML contents for differences.
    :param content1: Parsed content of the first YAML file.
    :param content2: Parsed content of the second YAML file.
    :return: None; Prints differences if any.
    """
    if content1 == content2:
        print("The two YAML files are identical.")
    else:
        print("Differences found:")
        for key in set(content1).union(content2):
            if content1.get(key) != content2.get(key):
                print(f" - Key '{key}':")
                print(f"   File 1: {content1.get(key)}")
                print(f"   File 2: {content2.get(key)}")


# File paths
file1 = 'samplex.yaml'
file2 = 'samplex_abc.yaml'

# Validate files
content1 = validate_yaml(file1)
content2 = validate_yaml(file2)

if content1 and content2:
    # Compare contents if both files are valid
    compare_yaml_content(content1, content2)

import yaml


def validate_yaml(file_path):
    """
    Validates the YAML file syntax.
    :param file_path: Path to the YAML file.
    :return: Parsed YAML content if valid; None if invalid.
    """
    try:
        with open(file_path, 'r') as file:
            content = yaml.safe_load(file)
        print(f"'{file_path}' is valid.")
        return content
    except yaml.YAMLError as e:
        print(f"Error in '{file_path}': {e}")
        return None


def compare_dictionaries(dict1, dict2, parent_key=''):
    """
    Recursively compares two dictionaries and identifies differences.
    :param dict1: First dictionary to compare.
    :param dict2: Second dictionary to compare.
    :param parent_key: The key path leading to the current comparison level.
    :return: A list of differences.
    """
    differences = []
    keys = set(dict1.keys()).union(dict2.keys())
    for key in keys:
        full_key = f"{parent_key}.{key}" if parent_key else key
        if key not in dict1:
            differences.append((full_key, None, dict2[key]))
        elif key not in dict2:
            differences.append((full_key, dict1[key], None))
        elif isinstance(dict1[key], dict) and isinstance(dict2[key], dict):
            differences.extend(compare_dictionaries(dict1[key], dict2[key], full_key))
        elif dict1[key] != dict2[key]:
            differences.append((full_key, dict1[key], dict2[key]))
    return differences


def print_differences(differences):
    """
    Prints the differences in the desired format.
    :param differences: List of differences as tuples (key, value1, value2).
    """
    if differences:
        print("Differences found:")
        for key, value1, value2 in differences:
            print(f" - Key '{key}':")
            print(f"   File 1: {value1}")
            print(f"   File 2: {value2}")
    else:
        print("The two YAML files are identical.")


# File paths
file1 = 'samplex.yaml'
file2 = 'samplex_abc.yaml'

# Validate files
content1 = validate_yaml(file1)
content2 = validate_yaml(file2)

if content1 and content2:
    # Compare contents if both files are valid
    differences = compare_dictionaries(content1, content2)
    print_differences(differences)

import yaml
from deepdiff import DeepDiff


def cloudformation_tag_constructor(loader, tag_suffix, node):
    """
    Handle CloudFormation-like tags dynamically (e.g., !Select, !GetAZs).
    """
    if isinstance(node, yaml.SequenceNode):
        return {tag_suffix: loader.construct_sequence(node)}
    elif isinstance(node, yaml.ScalarNode):
        return {tag_suffix: loader.construct_scalar(node)}
    elif isinstance(node, yaml.MappingNode):
        return {tag_suffix: loader.construct_mapping(node)}
    else:
        raise ValueError(f"Unhandled node type: {type(node)}")


def register_dynamic_tag_handler():
    """
    Registers a catch-all constructor for handling arbitrary YAML tags.
    """
    yaml.SafeLoader.add_multi_constructor('!', cloudformation_tag_constructor)


def validate_yaml(file_path):
    """
    Validates the syntax of a YAML file and returns the parsed content.
    """
    try:
        with open(file_path, 'r') as file:
            content = yaml.load(file, Loader=yaml.SafeLoader)
        print(f"'{file_path}' is valid.")
        return content
    except yaml.YAMLError as e:
        print(f"Error in '{file_path}': {e}")
        return None


def compare_yaml(content1, content2):
    """
    Compares two YAML contents and reports differences.
    """
    diff = DeepDiff(content1, content2, ignore_order=True, verbose_level=2)
    if diff:
        print("Differences found:")
        print(diff)
    else:
        print("No differences found between the YAML files.")


if __name__ == "__main__":
    # Register dynamic YAML tag handler
    register_dynamic_tag_handler()

    # File paths to the YAML files
    file1 = "samplex.yaml"
    file2 = "samplex_abc.yaml"

    # Validate and parse YAML files
    content1 = validate_yaml(file1)
    content2 = validate_yaml(file2)

    if content1 and content2:
        # Compare the YAML files
        compare_yaml(content1, content2)

import yaml


# Define a custom loader that can handle the !Ref tag
class CustomLoader(yaml.SafeLoader):
    pass


def ref_constructor(loader, node):
    # This returns the scalar value associated with the !Ref tag
    return node.value


# Add the constructor for the !Ref tag to the custom loader
CustomLoader.add_constructor('!Ref', ref_constructor)
CustomLoader.add_constructor('!GetAtt', ref_constructor)
CustomLoader.add_constructor('!Select', ref_constructor)
CustomLoader.add_constructor('!Join', ref_constructor)


# Define a recursive function to search for keys in nested YAML data
def find_values(key, data):
    results = []
    if isinstance(data, dict):
        for k, v in data.items():
            if k == key:
                results.append(v)
            if isinstance(v, (dict, list)):
                results.extend(find_values(key, v))
    elif isinstance(data, list):
        for item in data:
            results.extend(find_values(key, item))
    return results


file1 = 'component.yaml'
# Load the YAML file
with open(file1, 'r') as file:
    yaml_data = yaml.load(file, Loader=CustomLoader)

# Example usage:
types = find_values('Type', yaml_data)
group_desc = find_values('GroupDescription', yaml_data)

print("Values for key 'Type':", types)
print("Values for key 'GroupDescription':", group_desc)

import yaml


# Custom Loader to handle the !Ref tag by simply returning its scalar value.
class CustomLoader(yaml.SafeLoader):
    pass


def ref_constructor(loader, node):
    return node.value


CustomLoader.add_constructor('!Ref', ref_constructor)
CustomLoader.add_constructor('!GetAtt', ref_constructor)
CustomLoader.add_constructor('!Select', ref_constructor)
CustomLoader.add_constructor('!Join', ref_constructor)


def find_values_with_paths(target_key, data, path=None):
    """
    Recursively search for all occurrences of `target_key` in a nested data structure,
    and return a list of tuples, each containing:
      - The full key path as a string (with keys separated by '>').
      - The corresponding value.
    """
    if path is None:
        path = []
    matches = []
    if isinstance(data, dict):
        for key, value in data.items():
            # Append the current key to the path
            new_path = path + [key]
            if key == target_key:
                # When a match is found, join the key path and save with the value.
                matches.append((">".join(new_path), value))
            # Recursively search if the value is a dict or list.
            if isinstance(value, (dict, list)):
                matches.extend(find_values_with_paths(target_key, value, new_path))
    elif isinstance(data, list):
        # For lists, you might include an index in the path for clarity.
        for index, item in enumerate(data):
            new_path = path + [f"[{index}]"]
            matches.extend(find_values_with_paths(target_key, item, new_path))
    return matches


file1 = 'Samplex.yaml'

# Load the YAML file using the custom loader
with open(file1, 'r') as file:
    yaml_data = yaml.load(file, Loader=CustomLoader)

# Example 1: Find all values for key "Type"
type_matches = find_values_with_paths("Type", yaml_data)
print("Matches for key 'Type':")
for key_tree, value in type_matches:
    print("Path:", key_tree, "-> Value:", value)

# Example 2 & 3: Find all values for key "GroupDescription" along with their key tree
group_desc_matches = find_values_with_paths("GroupDescription", yaml_data)
print("\nMatches for key 'GroupDescription':")
for key_tree, value in group_desc_matches:
    print("Path:", key_tree, "-> Value:", value)'''

import yaml
import re


# --- Custom Loader to handle the !Ref tag ---
class CustomLoader(yaml.SafeLoader):
    pass


def ref_constructor(loader, node):
    # For the purpose of this example, simply return the scalar value.
    return node.value


CustomLoader.add_constructor('!Ref', ref_constructor)
CustomLoader.add_constructor('!GetAtt', ref_constructor)
CustomLoader.add_constructor('!Select', ref_constructor)
CustomLoader.add_constructor('!Join', ref_constructor)


# --- Helper Function 1: Find all values for a given key ---
def find_values(target_key, data):
    """
    Recursively search the nested data for all values of target_key.
    Returns a flat list of values.
    """
    results = []
    if isinstance(data, dict):
        for key, value in data.items():
            if key == target_key:
                results.append(value)
            if isinstance(value, (dict, list)):
                results.extend(find_values(target_key, value))
    elif isinstance(data, list):
        for item in data:
            results.extend(find_values(target_key, item))
    return results


# --- Helper Function 2: Find all paths (as lists of keys) for a given key ---
def find_key_paths(data, target_key, current_path=None):
    """
    Recursively find all paths (each as a list of keys) to occurrences of target_key.
    Returns a list of tuples (path_list, value).
    """
    if current_path is None:
        current_path = []
    matches = []
    if isinstance(data, dict):
        for key, value in data.items():
            new_path = current_path + [key]
            if key == target_key:
                matches.append((new_path, value))
            if isinstance(value, (dict, list)):
                matches.extend(find_key_paths(value, target_key, new_path))
    elif isinstance(data, list):
        for index, item in enumerate(data):
            new_path = current_path + [f"[{index}]"]
            matches.extend(find_key_paths(item, target_key, new_path))
    return matches


# --- Helper Function 3: Reconstruct the minimal branch along a given path ---
def build_minimal_branch(data, path_list):
    """
    Given the original data and a path (list of keys) that leads to the target,
    build a minimal dictionary branch that includes:
      - All scalar keys at the current level (to keep context),
      - And for the key in the path, only the branch leading to the target.
    """
    print('************************************************************1')
    print(data, path_list)
    if not path_list:
        return data
    key = path_list[0]
    if isinstance(data, dict) and key in data:
        branch = {}
        # Include all scalar keys (non-dict, non-list) at this level as context.
        for k, v in data.items():
            if not isinstance(v, (dict, list)):
                branch[k] = v
        # Recurse only for the key that is on the branch.
        branch[key] = build_minimal_branch(data[key], path_list[1:])
        print('**********************************************************2:', branch)
        return branch

    else:
        return None


def find_values_with_paths(target_key, data, path=None):
    """
    Recursively search for all occurrences of `target_key` in a nested data structure,
    and return a list of tuples, each containing:
      - The full key path as a string (with keys separated by '>').
      - The corresponding value.
    """
    if path is None:
        path = []
    matches = []
    if isinstance(data, dict):
        for key, value in data.items():
            # Append the current key to the path
            new_path = path + [key]
            if key == target_key or (isinstance(target_key, str) and isinstance(key, str) and target_key in key):
                # When a match is found, join the key path and save with the value.
                matches.append((">".join(new_path), value))
            # Recursively search if the value is a dict or list.
            if isinstance(value, (dict, list)):
                matches.extend(find_values_with_paths(target_key, value, new_path))
    elif isinstance(data, list):
        # For lists, you might include an index in the path for clarity.
        for index, item in enumerate(data):
            new_path = path + [f"[{index}]"]
            matches.extend(find_values_with_paths(target_key, item, new_path))
    return matches


def getconvertion(abc):
    # Step 1: Split by '>' while keeping indexes intact
    parts = re.split(r'>(?=\[|\w)', abc)

    # Step 2: Format each part correctly
    formatted_parts = []
    for part in parts:
        if re.match(r'^\[\d+\]$', part):  # If it's an index like [0]
            formatted_parts.append(part)
        else:  # It's a key, so wrap it in quotes
            formatted_parts.append(f"['{part}']")

    # Step 3: Join formatted parts into a single expression
    bac = ''.join(formatted_parts)
    return bac


# --- Main Execution ---
file1 = 'ec2xx.yaml'
# Load the YAML file using the custom loader.
with open(file1, 'r') as file:
    yaml_data = yaml.load(file, Loader=CustomLoader)

# Requirement 1: Get all values for key "Type"
type_values = find_values('ImageId', yaml_data)
print("Values for key 'Type':", type_values)
# Expected output: ['AWS::EC2::Instance', 'AWS::EC2::SecurityGroup']

# Requirement 2: Get all values for key "GroupDescription"
group_desc_values = find_values('ImageId', yaml_data)
print("Values for key 'Network':", group_desc_values)
# Expected output: ['Enable SSH access via port 22 via anywhere']
'''
# Requirement 3: For key "GroupDescription", get the minimal branch (key tree).
# The YAML structure is: Resources -> ResourceName -> Properties -> GroupDescription.
# For demonstration, we remove the top-level "Resources" key to focus on the resource.
paths = find_key_paths(yaml_data, 'ImageId')
print(paths)
minimal_branches = []
for path, value in paths:
    # Check that the path starts with "Resources". If so, remove it.
    if path and path[0] == "Resources":
        # The next element is the resource name (e.g., "InstanceSecurityGroup").
        # We then want the branch inside that resource.
        resource_name = path[1]
        if "Resources" in yaml_data and resource_name in yaml_data["Resources"]:
            resource_dict = yaml_data["Resources"][resource_name]
            # Build the minimal branch from the resource dictionary
            # using the remaining path (e.g. ["Properties", "GroupDescription"]).
            print(resource_dict, path, path[2:])
            branch = build_minimal_branch(resource_dict, path[2:])
            minimal_branches.append(branch)
    else:
        # If "Resources" is not part of the path, use the full branch.
        branch = build_minimal_branch(yaml_data, path)
        minimal_branches.append(branch)

print("Minimal branches for key 'SubnetId':")
for branch in minimal_branches:
    print(branch)
'''

# Example 2 & 3: Find all values for key "GroupDescription" along with their key tree
group_desc_matches = find_values_with_paths("Name", yaml_data)
print("\nMatches for key 'GroupDescription':")
for key_tree, value in group_desc_matches:
    # print("Path:", key_tree, "-> Value:", value)
    getcnt = getconvertion(abc='Reservations>'+key_tree)
    print(getcnt, "-> Value:", value)

# For your sample YAML, the expected minimal branch for "GroupDescription" is:
# {
#    "Type": "AWS::EC2::SecurityGroup",
#    "Properties": {
#         "GroupDescription": "Enable SSH access via port 22 via anywhere"
#    }
# }
#abc = "Reservations>[0]>Instances>[0]>NetworkInterfaces>[0]>Groups>[0]>GroupId"
#getcnt = getconvertion(abc=abc)
#print(getcnt)