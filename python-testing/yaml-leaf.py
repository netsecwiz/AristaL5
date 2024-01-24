# Mady by tristan Ziemann. I always joked about a script that makes a script. Well here we go!
# Follow my stupidity at netsecwiz.com 
import ipaddress
import yaml

def generate_yaml_config(spine1_subnets, spine2_subnets, num_leaves):
    config = {"global": {}, "spines": {}, "leaves": {}}
    
    # Generate IP addresses for spines
    spine1_p2p = (subnet for snet in spine1_subnets for subnet in ipaddress.ip_network(snet).subnets(new_prefix=31))
    spine2_p2p = (subnet for snet in spine2_subnets for subnet in ipaddress.ip_network(snet).subnets(new_prefix=31))

    for i in range(1, num_leaves + 1):
        leaf_name = f"s1-leaf{i}"
        config["leaves"][leaf_name] = {
            "interfaces": {
                "loopback0": {"ipv4": str(next(spine1_p2p).network_address), "mask": 32},
                "loopback1": {"ipv4": str(next(spine2_p2p).network_address), "mask": 32},
                "Ethernet2": {"ipv4": str(next(spine1_p2p).network_address), "mask": 31},
                "Ethernet3": {"ipv4": str(next(spine2_p2p).network_address), "mask": 31}
            },
            "BGP": {
                "ASN": 65101,  # Example ASN, modify as needed
                "spine-peers": [],  # Add spine peers
                "spine-ASN": 65100  # Example spine ASN, modify as needed
            },
            "MLAG": "Odd" if i % 2 != 0 else "Even"
        }

    return config

# Example Usage
spine1_subnets = ['172.16.80.0/24', '172.16.81.0/24']  # Two /24 subnets for spine1
spine2_subnets = ['172.17.80.0/24', '172.17.81.0/24']  # Two /24 subnets for spine2
num_leaves = 96

config = generate_yaml_config(spine1_subnets, spine2_subnets, num_leaves)

with open('network_config.yaml', 'w') as file:
    yaml.dump(config, file, default_flow_style=False)
