'''import yaml
from jinja2 import Environment, FileSystemLoader

# Load vars.yaml
with open("vars.yaml", "r") as vars_file:
    vars_data = yaml.safe_load(vars_file) or {}

# Extract values from _defaults if necessary
if "_defaults" in vars_data:
    vars_data["InstanceType"] = vars_data["_defaults"]["InstanceType"]

# Debug print to check loaded data
print("DEBUG: Loaded Variables from vars.yaml ->", vars_data)

# Ensure vars.InstanceType exists
if "InstanceType" not in vars_data:
    print("ERROR: InstanceType not found in vars.yaml!")
    exit(1)

# Configure Jinja2
env = Environment(loader=FileSystemLoader("."), trim_blocks=True, lstrip_blocks=True)
template = env.get_template("component.yaml")

# Render template with vars.yaml data
rendered_yaml = template.render(vars=vars_data)

# Debug print to check rendered YAML
print("DEBUG: Rendered YAML Content ->\n", rendered_yaml)

# Save the output
with open("output.yaml", "w") as output_file:
    output_file.write(rendered_yaml)

print("Rendered YAML saved to output.yaml")'''

import yaml
from jinja2 import Environment, FileSystemLoader

# Load vars.yaml
with open("vars.yaml", "r") as vars_file:
    vars_data = yaml.safe_load(vars_file) or {}

# Extract all values from _defaults if it exists
if "_defaults" in vars_data:
    for key, value in vars_data["_defaults"].items():
        vars_data[key] = value  # Move key-value pairs to the main level

# Debug print to check loaded data
print("DEBUG: Loaded Variables from vars.yaml ->", vars_data)

# Ensure required variables exist
#required_keys = ["InstanceType", "Namex"]
#missing_keys = [key for key in required_keys if key not in vars_data]
#if missing_keys:
#    print(f"ERROR: Missing keys in vars.yaml: {missing_keys}")
 #   exit(1)

# Configure Jinja2
env = Environment(loader=FileSystemLoader("."), trim_blocks=True, lstrip_blocks=True)
template = env.get_template("component.yaml")

# Render template with vars.yaml data
rendered_yaml = template.render(vars=vars_data)

# Debug print to check rendered YAML
print("DEBUG: Rendered YAML Content ->\n", rendered_yaml)

# Save the output
with open("output.yaml", "w") as output_file:
    output_file.write(rendered_yaml)

print("Rendered YAML saved to output.yaml")
