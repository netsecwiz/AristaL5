#!/usr/bin/env python3

import pyeapi

# Connect to the node
node = pyeapi.connect(host='192.168.0.12', username='arista', password='aristaxb8c', return_node=True)

# Create and configure a VLAN
vlan = node.api('vlans')
vlan_id = 100  # Replace with your desired VLAN ID
vlan.create(vlan_id)
vlan.set_name(vlan_id, 'VLAN100')  # Optional: Set a name for the VLAN

# Configure Ethernet1 as a switchport and assign it to the VLAN
interface_name = 'Ethernet1'
commands = [
    'interface {}'.format(interface_name),
    'description Configured for VLAN100',  # Optional: Set a description
    'switchport mode access',
    'switchport access vlan {}'.format(vlan_id)
]

# Send the configuration commands
node.config(commands)

# Save the configuration
node.config(['write memory'])
