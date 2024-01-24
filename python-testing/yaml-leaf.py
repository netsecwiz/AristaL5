# Author: Tristan Ziemann, info@netsecwiz.com 
import ipaddress
import yaml

# Function to generate YAML configuration for network devices
def generate_yaml_config(num_leaves, dc_name):
    # Initialize configuration dictionary
    config = {"spines": {}, "leaves": {}}

    # Spine Configuration
    # Define loopback addresses for the two spines
    spines_loopback = ["10.255.255.0", "10.255.255.255"]
    
    # Generate /31 subnets for spine-to-leaf connections
    spine1_p2p = ipaddress.ip_network('172.16.80.0/24').subnets(new_prefix=31)
    spine2_p2p = ipaddress.ip_network('172.17.80.0/24').subnets(new_prefix=31)

    # Configure each spine switch
    for i in range(1, 3):
        spine_name = f"s1-spine{i}"
        config["spines"][spine_name] = {
            "interfaces": {
                "loopback0": {"ipv4": spines_loopback[i-1], "mask": 32},
            },
            "BGP": {
                "ASN": 65100
            }
        }
        # Add Ethernet interfaces for each spine
        for j in range(1, num_leaves + 1):
            config["spines"][spine_name]["interfaces"][f"Ethernet{j}"] = {
                "ipv4": str(next(spine1_p2p if i == 1 else spine2_p2p).network_address),
                "mask": 31
            }

    # Leaf Configuration
    # Define spine peer IP addresses (loopbacks of spines)
    spine_peers = ["10.255.255.0", "10.255.255.255"]
    
    # Configure each leaf switch
    for i in range(1, num_leaves + 1):
        leaf_name = f"s1-leaf{i}"
        config["leaves"][leaf_name] = {
            "interfaces": {
                # Assign loopback0 addresses incrementally for each leaf
                "loopback0": {"ipv4": f"10.255.255.{i}", "mask": 32},
                # Assign loopback1 addresses, shared between every pair of leaves
                "loopback1": {"ipv4": f"10.255.254.{(i+1)//2}", "mask": 32},
                # Assign IPv4 addresses for Ethernet interfaces to connect to spines
                "Ethernet2": {"ipv4": str(ipaddress.IPv4Address('172.16.80.0') + 2 * (i - 1)), "mask": 31},
                "Ethernet3": {"ipv4": str(ipaddress.IPv4Address('172.17.80.0') + 2 * (i - 1)), "mask": 31}
            },
            "BGP": {
                # Assign BGP ASNs, incrementing every pair
                "ASN": 65101 + (i - 1) // 2,
                "spine-peers": spine_peers.copy(),  # Copy the list to avoid YAML references
                "spine-ASN": 65100
            },
            # Set MLAG configuration for each leaf
            "MLAG": "Odd" if i % 2 != 0 else "Even"
        }

    return config

# Main script execution
# Set the data center name and the number of leaves
dc_name = "DC1"  # Replace with desired DC name
num_leaves = 96

# Generate the configuration
config = generate_yaml_config(num_leaves, dc_name)

# Define the filename including the data center name
filename = f'{dc_name}_network_config.yaml'

# Write the configuration to a YAML file
with open(filename, 'w') as file:
    yaml.dump(config, file, default_flow_style=False, sort_keys=False)
