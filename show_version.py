#!/usr/bin/env python3

from jsonrpclib import Server
import ssl
import json
import pprint
from urllib.request import urlopen
with urlopen('https://pypi.org/pypi/sampleproject/json') as resp:
    project_info = json.load(resp)['info']

ssl._create_default_https_context = ssl._create_unverified_context

switch = Server("https://arista:aristaxb8c@192.168.0.12/command-api")

response = switch.runCmds( 1, ["show version"] )

pp = pprint.PrettyPrinter(width=41, compact=True)
pp.pprint(response)

