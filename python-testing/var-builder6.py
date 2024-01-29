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
    config = {"global": {dc_config['dc_name']: dc_config['global_config']}}

    # Spine Configuration
    for i in range(1, num_spines + 1):
        spine_name = f"{dc_config['dc_name']}-spine{i}"
        config[spine_name] = {
            "interfaces": {
                "loopback0": {"ipv4": dc_config['spines_loopback'][i-1], "mask": 32}
            },
            "BGP": {"ASN": dc_config['spine_ASN']}
        }
        spine_p2p_subnets = list(ipaddress.ip_network(dc_config['spine_p2ps'][i-1]).subnets(new_prefix=31))
        for j in range(1, num_leaves + 1):
            config[spine_name]["interfaces"][f"Ethernet{j}"] = {"ipv4": str(spine_p2p_subnets[j-1].network_address), "mask": 31}
        
        # Assigning specific interfaces for borderleafs
        if num_borderleafs >= 1:
            config[spine_name]["interfaces"]["Ethernet61"] = {"ipv4": "Link to Borderleaf1", "mask": None}
        if num_borderleafs >= 2:
            config[spine_name]["interfaces"]["Ethernet62"] = {"ipv4": "Link to Borderleaf2", "mask": None}


    # Leaf Configuration
    leaf_ASN = dc_config['leaf_ASN_start']
    for i in range(1, num_leaves + 1):
        leaf_name = f"{dc_config['dc_name']}-leaf{i}"
        config[leaf_name] = {"interfaces": {"loopback0": {"ipv4": f"10.255.255.{i}", "mask": 32}, "loopback1": {"ipv4": f"10.255.254.{(i+1)//2}", "mask": 32}}, "BGP": {"ASN": leaf_ASN, "spine-peers": dc_config['spine_peers'], "spine-ASN": dc_config['spine_ASN']}, "MLAG": "Odd" if i % 2 != 0 else "Even"}
        leaf_ASN += 1  # Increment ASN for next leaf

    return config

def main():
    num_spines = int(input("Enter the number of spines: "))
    num_borderleafs = int(input("Enter the number of borderleafs: "))
    num_leaves = int(input("Enter the number of leaves: "))

    # Initialize dc_config dictionary
    dc_config = {
        'dc_name': input("Enter the data center name: "),
        'spine_ASN': int(input("Enter the spine ASN: ")),
        'lo0': input("Enter the loopback network (e.g., '10.255.255.0/24'): "),
        'leaf_ASN_start': int(input("Enter the starting ASN for leaves: "))
    }

    # Spine configuration
    dc_config['spine_p2ps'] = [input(f"Enter the point-to-point network for spine{i} (e.g., '172.16.80.0/24'): ") for i in range(1, num_spines + 1)]
    if not validate_no_overlap(dc_config['spine_p2ps']):
        print("Error: Overlapping point-to-point networks detected.")
        return

    dc_config['spines_loopback'] = input("Enter the spine loopback IPs separated by space: ").split()
    dc_config['spine_peers'] = [str(ipaddress.ip_network(net).network_address + 1) for net in dc_config['spine_p2ps']]

    # Borderleaf configuration
    dc_config['borderleaf_loopbacks'] = [input(f"Enter the loopback IP for borderleaf{i} (e.g., '10.255.254.1'): ") for i in range(1, num_borderleafs + 1)]
    borderleaf_ASN = int(input("Enter the ASN for borderleafs: "))
    dc_config['borderleaf_ASNs'] = [borderleaf_ASN] * num_borderleafs

    # Setting up global_config within dc_config
    dc_config['global_config'] = {
        "spine_ASN": dc_config['spine_ASN'],
        "lo0": dc_config['lo0'],
        "spine_peers": dc_config['spine_peers'],
        "MTU": 9214
    }

    # Generate and write YAML configuration
    config = generate_yaml_config(num_leaves, num_spines, num_borderleafs, dc_config)
    filename = f'{dc_config["dc_name"]}_network_config.yaml'
    with open(filename, 'w') as file:
        yaml.dump(config, file, default_flow_style=False, sort_keys=False)

    print(f"All configurations for {dc_config['dc_name']} generated successfully.")

if __name__ == "__main__":
    main()