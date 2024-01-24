import ipaddress
import yaml

def generate_yaml_config(num_leaves, dc_name):
    # Global configuration
    config = {
        "global": {
            "DC1": {
                "spine_ASN": 65100,
                "p2p": "172.16.80.0/23",
                "lo0": "10.255.255.0/24",
                "spine_peers": [
                    "10.255.255.0",
                    "10.255.255.255"
                ],
                "MTU": 9214
            }
        }
    }

    # Spine Configuration
    spines_loopback = ["10.255.255.0", "10.255.255.255"]
    spine1_p2p_subnets = list(ipaddress.ip_network('172.16.80.0/23').subnets(new_prefix=31))
    spine2_p2p_subnets = list(ipaddress.ip_network('172.17.80.0/23').subnets(new_prefix=31))
    
    for i in range(1, 3):
        spine_name = f"s1-spine{i}"
        config[spine_name] = {
            "interfaces": {
                "loopback0": {"ipv4": spines_loopback[i-1], "mask": 32},
            },
            "BGP": {
                "ASN": 65100
            }
        }
        for j in range(num_leaves):
            config[spine_name]["interfaces"][f"Ethernet{j+1}"] = {
                "ipv4": str(spine1_p2p_subnets[j].network_address if i == 1 else spine2_p2p_subnets[j].network_address),
                "mask": 31
            }

    # Leaf Configuration
    spine_peers = ["10.255.255.0", "10.255.255.255"]
    for i in range(1, num_leaves + 1):
        leaf_name = f"s1-leaf{i}"
        config[leaf_name] = {
            "interfaces": {
                "loopback0": {"ipv4": f"10.255.255.{i}", "mask": 32},
                "loopback1": {"ipv4": f"10.255.254.{(i+1)//2}", "mask": 32},
                "Ethernet2": {"ipv4": str(spine1_p2p_subnets[i-1].network_address), "mask": 31},
                "Ethernet3": {"ipv4": str(spine2_p2p_subnets[i-1].network_address), "mask": 31}
            },
            "BGP": {
                "ASN": 65101 + (i - 1) // 2,
                "spine-peers": spine_peers.copy(),
                "spine-ASN": 65100
            },
            "MLAG": "Odd" if i % 2 != 0 else "Even"
        }

    return config

# Main script execution

dc_name = "DC1"  # Replace with desired DC name
num_leaves = 96
config = generate_yaml_config(num_leaves, dc_name)

filename = f'{dc_name}_network_config.yaml'
with open(filename, 'w') as file:
    yaml.dump(config, file, default_flow_style=False, sort_keys=False)
