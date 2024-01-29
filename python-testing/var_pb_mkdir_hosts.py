import os
import ipaddress
import yaml

# Function definitions: generate_hosts_file, create_directories, generate_playbook, generate_yaml_config
# ...

# Function to create directories
def create_directories(dir_list):
    for dir_name in dir_list:
        os.makedirs(dir_name, exist_ok=True)

# Function to generate hosts file
def generate_hosts_file(dc_name, num_spines, num_leafs, num_borderleafs):
    # Template for the hosts file
    # ... function implementation ...

# Function to generate playbooks
def generate_playbook(dc_name, group_name, template_file, dest_file_suffix):
    # Template for the playbook
    # ... function implementation ...

# Function to generate YAML configuration
def generate_yaml_config(num_leaves, dc_name):
    # ... function implementation ...

def main():
    # User inputs for DC configuration
    dc_name = input("Enter the data center name: ")
    num_spines = int(input("Enter the number of spines: "))
    num_leafs = int(input("Enter the number of leafs: "))
    num_borderleafs = int(input("Enter the number of borderleafs: "))

    # Create necessary directories
    directories = ["configs", "playbooks", "reports", "templates", "vars"]
    create_directories(directories)

    # Generate and write hosts file
    hosts_content = generate_hosts_file(dc_name, num_spines, num_leafs, num_borderleafs)
    with open(f"{dc_name}_hosts.ini", "w") as file:
        file.write(hosts_content)

    # Generate and write playbooks
    playbook_dir = "playbooks"
    playbook_leafs = generate_playbook(dc_name, "leafs", "leaf", "bgp")
    playbook_spines = generate_playbook(dc_name, "spines", "spine", "")
    playbook_borderleafs = generate_playbook(dc_name, "borderleafs", "borderleaf", "bl")

    with open(os.path.join(playbook_dir, f"{dc_name}_leafs_playbook.yml"), "w") as file:
        file.write(playbook_leafs)
    with open(os.path.join(playbook_dir, f"{dc_name}_spines_playbook.yml"), "w") as file:
        file.write(playbook_spines)
    with open(os.path.join(playbook_dir, f"{dc_name}_borderleafs_playbook.yml"), "w") as file:
        file.write(playbook_borderleafs)

    # Generate and write YAML configuration
    config = generate_yaml_config(num_leafs, dc_name)
    filename = f'{dc_name}_network_config.yaml'
    with open(filename, 'w') as file:
        yaml.dump(config, file, default_flow_style=False, sort_keys=False)

    print(f"All configurations for {dc_name} generated successfully.")

# This should be outside of the main function
if __name__ == "__main__":
    main()
