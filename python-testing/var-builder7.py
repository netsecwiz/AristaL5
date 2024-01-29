import ipaddress
import yaml

def generate_yaml_config(num_leaves, loopback_subnet):
    p2p_subnet = ipaddress.ip_network(loopback_subnet).supernet(new_prefix=24)

    config = {
        "global": {
            "spine_ASN": 65000,
            "lo0": f"{loopback_subnet}",
            "MTU": 9214
        }
    }

    # Spine Configuration
    for i in range(1, 3):  # Hardcoded for 2 spines
        spine_name = f"spine{i}"
        spine_ip = str(ipaddress.ip_network(loopback_subnet)[0]) if i == 1 else str(ipaddress.ip_network(loopback_subnet)[-1])
        config[spine_name] = {
            "interfaces": {
                "loopback0": {"ipv4": spine_ip, "mask": 32}
            },
            "BGP": {"ASN": 65000}
        }
        # Assigning interfaces to leafs and borderleafs
        for j in range(1, num_leaves + 3):  # Including borderleafs
            leaf_ip = str(p2p_subnet[j * 2 - 1]) if i == 1 else str(p2p_subnet[j * 2])
            config[spine_name]["interfaces"][f"Ethernet{j}"] = {"ipv4": leaf_ip, "mask": 31}

    # Leaf Configuration
    leaf_ASN = 65002
    for i in range(1, num_leaves + 3):  # Including borderleafs
        leaf_name = f"leaf{i}" if i <= num_leaves else f"borderleaf{i - num_leaves}"
        leaf_ip = str(ipaddress.ip_network(loopback_subnet)[252 + i - num_leaves]) if i > num_leaves else None
        config[leaf_name] = {
            "interfaces": {
                "loopback0": {"ipv4": leaf_ip, "mask": 32} if leaf_ip else {},
                "Ethernet1": {"ipv4": str(p2p_subnet[i * 2 - 1]), "mask": 31},
                "Ethernet2": {"ipv4": str(p2p_subnet[i * 2]), "mask": 31}
            },
            "BGP": {"ASN": leaf_ASN if i <= num_leaves else 65001},
            "MLAG": "Odd" if i % 2 != 0 else "Even"
        }
        if i <= num_leaves: leaf_ASN += 1

    return config

def main():
    num_leaves = int(input("Enter the number of leaves: "))
    loopback_subnet = input("Enter the loopback subnet (e.g., '10.255.255.0/24'): ")

    config = generate_yaml_config(num_leaves, loopback_subnet)
    filename = 'network_config.yaml'
    with open(filename, 'w') as file:
        yaml.dump(config, file, default_flow_style=False, sort_keys=False)

    print("Network configuration generated successfully.")

if __name__ == "__main__":
    main()
    