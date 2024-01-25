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
# Other functions...

def generate_template(template_name, content):
    with open(os.path.join("templates", template_name), "w") as file:
        file.write(content)

def main():
    # User inputs
    dc_name = input("Enter the data center name: ")
    num_spines = int(input("Enter the number of spines: "))
    num_leafs = int(input("Enter the number of leafs: "))
    num_borderleafs = int(input("Enter the number of borderleafs: "))

    # Generate hosts file
    hosts_content = generate_hosts_file(dc_name, num_spines, num_leafs, num_borderleafs)
    with open(f"{dc_name}_hosts.ini", "w") as file:
        file.write(hosts_content)

    # Generate playbooks
    # ...

    # Ensure the templates directory exists
    os.makedirs("templates", exist_ok=True)

    # Generate Jinja templates
    borderleaf_template = "router bgp {{ underlay[inventory_hostname]['BGP']['ASN'] }}\n\n   neighbor DCI peer group\n   ... " # Add full content
    leaf_template = "service routing protocols model multi-agent\n\n{% for item in underlay[inventory_hostname]['interfaces'] %}\n... " # Add full content
    spine_template = "service routing protocols model multi-agent\n\n{% for item in underlay[inventory_hostname]['interfaces'] %}\n... " # Add full content

    generate_template("borderleaf.j2", borderleaf_template)
    generate_template("leaf.j2", leaf_template)
    generate_template("spine.j2", spine_template)
    
    print(f"Configuration files and templates for {dc_name} generated successfully.")

if __name__ == "__main__":
    main()
