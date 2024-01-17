#!/usr/bin/env python3

import pyeapi

node = pyeapi.connect(host='192.168.0.12',username='arista',password='aristaxb8c',return_node=True)

users = node.api('users')

users.create('testuser',secret='foo')
users.set_privilege('testuser',value='15')
users.set_role('testuser',value='network-admin')