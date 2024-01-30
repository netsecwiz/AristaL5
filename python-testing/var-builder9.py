import ipaddress
import yaml

def generate_yaml_config(num_leaves, dc_name, spine1_p2p_subnet, spine2_p2p_subnet, loopback0_subnet, spine_asn, borderleaf_asn, leaf_asn_start):
    spine1_p2p_subnets = list(ipaddress.ip_network(spine1_p2p_subnet).subnets(new_prefix=31))
    spine2_p2p_subnets = list(ipaddress.ip_network(spine2_p2p_subnet).subnets(new_prefix=31))
    loopback0_ips = list(ipaddress.ip_network(loopback0_subnet).hosts())

    config = {
        "global": {
            "spine_ASN": spine_asn,
            "lo0": str(loopback0_subnet),
            "MTU": 9214
        }
    }

    # Spine Configuration
    for i in range(1, 3):  # Hardcoded for 2 spines
        spine_name = f"{dc_name}-spine{i}"
        spine_ip = str(ipaddress.ip_network(loopback0_subnet)[0]) if i == 1 else str(ipaddress.ip_network(loopback0_subnet)[-1])
        config[spine_name] = {
            "interfaces": {
                "loopback0": {"ipv4": spine_ip, "mask": 32}
            },
            "BGP": {"ASN": spine_asn}
        }

        # Setup P2P connections
        p2p_subnets = spine1_p2p_subnets if i == 1 else spine2_p2p_subnets
        for j in range(num_leaves):  # For leaves
            leaf_ip = str(p2p_subnets[j].network_address)
            config[spine_name]["interfaces"][f"Ethernet{j+1}"] = {"ipv4": leaf_ip, "mask": 31}
        
        # Hardcode borderleaf connections
        config[spine_name]["interfaces"]["Ethernet61"] = {"ipv4": str(p2p_subnets[-2].network_address), "mask": 31}  # For Borderleaf1
        config[spine_name]["interfaces"]["Ethernet62"] = {"ipv4": str(p2p_subnets[-1].network_address), "mask": 31}  # For Borderleaf2

    # Leaf and Borderleaf Configuration
    leaf_ASN = leaf_asn_start
    for i in range(1, num_leaves + 3):  # Including borderleafs
        leaf_name = f"{dc_name}-leaf{i}" if i <= num_leaves else f"{dc_name}-borderleaf{i - num_leaves}"
        leaf_loopback0 = str(loopback0_ips[i - 1])
        leaf_loopback1 = str(loopback0_ips[((i - 1) // 2) * 2])  # Same Loopback1 for each pair
        config[leaf_name] = {
            "interfaces": {
                "loopback0": {"ipv4": leaf_loopback0, "mask": 32},
                "loopback1": {"ipv4": leaf_loopback1, "mask": 32},
                "Ethernet1": {"ipv4": str(spine1_p2p_subnets[i-1].network_address), "mask": 31},
                "Ethernet2": {"ipv4": str(spine2_p2p_subnets[i-1].network_address), "mask": 31}
            },
            "BGP": {"ASN": leaf_ASN if i <= num_leaves else borderleaf_asn},
            "MLAG": "Odd" if i % 2 != 0 else "Even"
        }
        if i <= num_leaves and i % 2 == 0: leaf_ASN += 1

    return config

def main():
    dc_name = input("Enter the data center name: ")
    num_leaves = int(input("Enter the number of leaves: "))
    spine1_p2p_subnet = input("Enter the point-to-point subnet for spine1 (e.g., '172.16.80.0/24'): ")
    spine2_p2p_subnet = input("Enter the point-to-point subnet for spine2 (e.g., '172.16.81.0/24'): ")
    loopback0_subnet = input("Enter the loopback0 subnet (e.g., '10.255.255.0/24'): ")
    spine_asn = int(input("Enter the spine ASN: "))
    borderleaf_asn = int(input("Enter the borderleaf ASN: "))
    leaf_asn_start = int(input("Enter the starting ASN for leaves: "))

    config = generate_yaml_config(num_leaves, dc_name, spine1_p2p_subnet, spine2_p2p_subnet, loopback0_subnet, spine_asn, borderleaf_asn, leaf_asn_start)
    filename = f'{dc_name}_network_config.yaml'
    with open(filename, 'w') as file:
        yaml.dump(config, file, default_flow_style=False, sort_keys=False)

    print(f"Network configuration for {dc_name} generated successfully.")

if __name__ == "__main__":
    main()
