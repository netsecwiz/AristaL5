import os

def generate_hosts_file(dc_name, num_spines, num_leafs, num_borderleafs):
    # Template for the hosts file
    hosts_template = f"""[all:vars]
ansible_connection = network_cli
ansible_network_os = eos
ansible_become = yes
ansible_become_method = enable
ansible_python_interpreter = /usr/bin/python3
ansible_user = arista

[{dc_name}:children]
spines_{dc_name}
leafs_{dc_name}

[spines_{dc_name}]
{dc_name}spine[1:{num_spines}]

[leafs_{dc_name}]
{dc_name}leaf[1:{num_leafs}]
{dc_name}Brdr[1:{num_borderleafs}]

[borderleafs_{dc_name}]
{dc_name}Brdr[1:{num_borderleafs}]
"""

    return hosts_template

def main():
    # User inputs
    dc_name = input("Enter the data center name: ")
    num_spines = int(input("Enter the number of spines: "))
    num_leafs = int(input("Enter the number of leafs: "))
    num_borderleafs = int(input("Enter the number of borderleafs: "))

    # Generate hosts file
    hosts_content = generate_hosts_file(dc_name, num_spines, num_leafs, num_borderleafs)

    # Write to a file
    with open(f"{dc_name}_hosts.ini", "w") as file:
        file.write(hosts_content)
    
    print(f"Hosts file for {dc_name} generated successfully.")

if __name__ == "__main__":
    main()
