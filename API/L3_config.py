import pyeapi
from pyeapi.client import Node, Config

# Specify the path to your .eapi.conf file
config_file_path = '/home/coder/.eapi.conf'

# Load the configuration file
pyeapi.client.load_config(config_file_path)

# Print out the available connection profiles
print("Available connection profiles:", pyeapi.client.config.connections)

# Open a session with s1-leaf1
try:
    connect = pyeapi.connect_to("s1-leaf1")
except AttributeError as e:
    print(f"Error: {e}")
    print("Exiting script.")
    exit(1)

# Rest of your script...

# "Create" sets the port as a Layer 3 port (no switchport)
connect.api("ipinterfaces").create('Ethernet4')
# Set Ethernet4 for the IP address of 4.4.4.4 and put the result into the variable (boolean) result
result = connect.api("ipinterfaces").set_address('Ethernet4','4.4.4.4/24')
# This is just very basic error handling here, it gives a yes or no answer depending on whether a "200 OK" response was given, or another error was occurred.
if result == True:
    print("Completed!")
if result == False:
    print("Error!")
