import ipaddress
import yaml

def validate_no_overlap(networks):
    subnets = [ipaddress.ip_network(net) for net in networks]
    for i in range(len(subnets)):
        for j in range(i + 1, len(subnets)):
            if subnets[i].overlaps(subnets[j]):
                return False
    return True

def generate_yaml_config(num_leaves, num_spines, num_borderleafs, dc_config):
    # Global configuration
    config = {
        "global": {
            dc_config['dc_name']: {
                "spine_ASN": dc_config['spine_ASN'],
                "lo0": dc_config['lo0'],
                "spine_peers": dc_config['spine_peers'],
                "MTU": 9214
            }
        }
    }

    # Spine Configuration
    for i in range(1, num_spines + 1):
        spine_name = f"{dc_config['dc_name']}-spine{i}"
        config[spine_name] = {
            "interfaces": {
                "loopback0": {"ipv4": dc_config['spines_loopback'][i-1], "mask": 32},
                "BGP": {"ASN": dc_config['spine_ASN']}
            }
        }
        spine_p2p_subnets = list(ipaddress.ip_network(dc_config['spine_p2ps'][i-1]).subnets(new_prefix=31))
        for j in range(60):  # Using 60 ports for leaves
            port = f"Ethernet{j+1}"
            config[spine_name]["interfaces"][port] = {
                "ipv4": str(spine_p2p_subnets[j].network_address), "mask": 31
            }

    # Borderleaf Configuration
    for i in range(1, num_borderleafs + 1):
        borderleaf_name = f"{dc_config['dc_name']}-Brdr{i}"
        config[borderleaf_name] = {
            "interfaces": {
                "loopback0": {"ipv4": dc_config['borderleaf_loopbacks'][i-1], "mask": 32},
                "BGP": {"ASN": dc_config['borderleaf_ASNs'][i-1]}
            }
            # ... Add further borderleaf configurations ...
        }

    # Leaf Configuration
    leaf_ASN_start = dc_config['leaf_ASN_start']
    for i in range(1, num_leaves + 1):
        leaf_name = f"{dc_config['dc_name']}-leaf{i}"
        config[leaf_name] = {
            # ... Leaf configuration ...
        }

    return config

def main():
    num_spines = int(input("Enter the number of spines: "))
    num_borderleafs = int(input("Enter the number of borderleafs: "))
    num_leaves = int(input("Enter the number of leaves: "))

    dc_config = {
        'dc_name': input("Enter the data center name: "),
        'spine_ASN': int(input("Enter the spine ASN: ")),
        'lo0': input("Enter the loopback network (e.g., '10.255.255.0/24'): "),
        'leaf_ASN_start': int(input("Enter the starting ASN for leaves: "))
    }

    # Spine configuration
    dc_config['spine_p2ps'] = []
    for i in range(1, num_spines + 1):
        dc_config['spine_p2ps'].append(input(f"Enter the point-to-point network for spine{i} (e.g., '172.16.80.0/24'): "))

    if not validate_no_overlap(dc_config['spine_p2ps']):
        print("Error: Overlapping point-to-point networks detected.")
        return

    dc_config['spines_loopback'] = input("Enter the spine loopback IPs separated by space: ").split()

    # Calculate spine peers based on spine p2p networks
    dc_config['spine_peers'] = []
    for p2p in dc_config['spine_p2ps']:
        first_ip = ipaddress.ip_network(p2p).network_address + 1
        dc_config['spine_peers'].append(str(first_ip))

    # Borderleaf configuration
    borderleaf_loops = input("Enter the loopback IPs for borderleafs separated by space (e.g., '10.255.254.1 10.255.254.2'): ").split()
    dc_config['borderleaf_loopbacks'] = borderleaf_loops[:num_borderleafs]
    borderleaf_ASN = int(input("Enter the ASN for borderleafs: "))
    dc_config['borderleaf_ASNs'] = [borderleaf_ASN] * num_borderleafs

    # Generate and write YAML configuration
    config = generate_yaml_config(num_leaves, num_spines, num_borderleafs, dc_config)
    filename = f'{dc_config["dc_name"]}_network_config.yaml'
    with open(filename, 'w') as file:
        yaml.dump(config, file, default_flow_style=False, sort_keys=False)

    print(f"All configurations for {dc_config['dc_name']} generated successfully.")

if __name__ == "__main__":
    main()