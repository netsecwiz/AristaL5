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

def generate_playbook(dc_name, group_name, template_file, dest_file_suffix):
    # Template for the playbook
    playbook_template = f"""---
- hosts: {group_name}_{dc_name}
  gather_facts: no
  tasks:
    - name: Register variables from underlay-{dc_name}_all.yml
      include_vars:
        file: "{{{{{lookup('env','PWD')}}}}}/vars/underlay-{dc_name}_all.yml"  
        name: underlay       
    - name: Create {group_name.capitalize()} Configuration
      template:
        src: "{{{{{lookup('env','PWD')}}}}}/templates/{template_file}.j2"
        dest: "{{{{{lookup('env','PWD')}}}}}/configs/{{{{ inventory_hostname }}}}_config_{dest_file_suffix}.conf"
    # Push Configuration to Device
    eos_config:
        src: "{{{{{lookup('env','PWD')}}}}}/configs/{{{{ inventory_hostname }}}}_config_{dest_file_suffix}.conf"
"""
    return playbook_template

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
    playbook_leafs = generate_playbook(dc_name, "leafs", "leaf", "bgp")
    playbook_spines = generate_playbook(dc_name, "spines", "spine", "")
    playbook_borderleafs = generate_playbook(dc_name, "borderleafs", "borderleaf", "bl")

    with open(f"{dc_name}_leafs_playbook.yml", "w") as file:
        file.write(playbook_leafs)
    with open(f"{dc_name}_spines_playbook.yml", "w") as file:
        file.write(playbook_spines)
    with open(f"{dc_name}_borderleafs_playbook.yml", "w") as file:
        file.write(playbook_borderleafs)
    
    print(f"Configuration files for {dc_name} generated successfully.")

if __name__ == "__main__":
    main()
