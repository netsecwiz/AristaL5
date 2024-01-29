import ipaddress
import yaml

def generate_yaml_config(num_leaves, num_spines, num_borderleafs, dc_config):
    # Global configuration
    config = {
        "global": {
            dc_config['dc_name']: {
                "spine_ASN": dc_config['spine_ASN'],
                "p2p": dc_config['p2p'],
                "lo0": dc_config['lo0'],
                "spine_peers": dc_config['spine_peers'],
                "MTU": 9214
            }
        }
    }

    # Spine Configuration
    spines_loopback = dc_config['spines_loopback']
    spine1_p2p_subnets = list(ipaddress.ip_network(dc_config['spine1_p2p']).subnets(new_prefix=31))
    spine2_p2p_subnets = list(ipaddress.ip_network(dc_config['spine2_p2p']).subnets(new_prefix=31))
    
    for i in range(1, num_spines + 1):
        spine_name = f"{dc_config['dc_name']}-spine{i}"
        config[spine_name] = {
            "interfaces": {
                "loopback0": {"ipv4": spines_loopback[i-1], "mask": 32},
            },
            "BGP": {
                "ASN": dc_config['spine_ASN']
            }
        }
        for j in range(num_leaves + num_borderleafs):
            config[spine_name]["interfaces"][f"Ethernet{j+1}"] = {
                "ipv4": str(spine1_p2p_subnets[j].network_address if i == 1 else spine2_p2p_subnets[j].network_address),
                "mask": 31
            }

    # Leaf and Borderleaf Configuration
    spine_peers = dc_config['spine_peers']
    leaf_ASN_start = dc_config['leaf_ASN_start']
    for i in range(1, num_leaves + num_borderleafs + 1):
        leaf_name = f"{dc_config['dc_name']}-leaf{i}" if i <= num_leaves else f"{dc_config['dc_name']}-Brdr{i - num_leaves}"
        config[leaf_name] = {
            "interfaces": {
                "loopback0": {"ipv4": f"10.255.255.{i}", "mask": 32},
                "loopback1": {"ipv4": f"10.255.254.{(i+1)//2}", "mask": 32},
                "Ethernet2": {"ipv4": str(spine1_p2p_subnets[i-1].network_address), "mask": 31},
                "Ethernet3": {"ipv4": str(spine2_p2p_subnets[i-1].network_address), "mask": 31}
            },
            "BGP": {
                "ASN": leaf_ASN_start + (i - 1) // 2,
                "spine-peers": spine_peers.copy(),
                "spine-ASN": dc_config['spine_ASN']
            },
            "MLAG": "Odd" if i % 2 != 0 else "Even"
        }

    return config

# Main script execution
def main():
    dc_config = {
            'dc_name': input("Enter the data center name: "),
            'spine_ASN': int(input("Enter the spine ASN: ")),
            'p2p': input("Enter the point-to-point network for spine1 (e.g., '172.16.80.0/23'): "),
            'spine1_p2p': input("Enter the point-to-point network for spine1 (e.g., '172.16.80.0/23'): "),
            'spine2_p2p': input("Enter the point-to-point network for spine2 (e.g., '172.17.80.0/23'): "),  # corrected key here
            'lo0': input("Enter the loopback network (e.g., '10.255.255.0/24'): "),
            'spine_peers': input("Enter the spine peer IPs separated by space (e.g., '10.255.255.0 10.255.255.255'): ").split(),
            'spines_loopback': input("Enter the spine loopback IPs separated by space (e.g., '10.255.255.0 10.255.255.255'): ").split(),
            'leaf_ASN_start': int(input("Enter the starting ASN for leaves: "))
    }

    num_spines = int(input("Enter the number of spines: "))
    num_leaves = int(input("Enter the number of leaves: "))
    num_borderleafs = int(input("Enter the number of borderleafs: "))

    config = generate_yaml_config(num_leaves, num_spines, num_borderleafs, dc_config)
    filename = f'{dc_config["dc_name"]}_network_config.yaml'
    with open(filename, 'w') as file:
        yaml.dump(config, file, default_flow_style=False, sort_keys=False)

    print(f"All configurations for {dc_config['dc_name']} generated successfully.")

if __name__ == "__main__":
    main()
