__author__ = 'naveen'

import sys
from goto.connection import GCEConnection


client_secrets = 'client_secrets.json'
project_id = 'industrial-glow-533'
zone = 'us-central1-a'


#Create a connection object for gce
conn = GCEConnection(client_secrets, project_id, zone)

# #list all instance associated with this account
# print conn.get_all_instances()
#
# # create a instance with root disk will be deleted on termination of instance
# print conn.run_instance('myfirstinstance1', 'debian-cloud', 'debian-7-wheezy-v20140606',auto_delete=True)
#
# #terminate instance using name
# # print conn.terminate_instance('myfirstinstance1')
#
# #List all images
# print conn.get_all_images()
#
# #List all images
# print conn.get_all_zones()

# fil = conn.get_all_firewalls()
# for fire in fil:
#     # print fire.id
#     print fire.name

# fwall = conn.create_firewall(name="testwall",network_name="mynetwork",rules=[('tcp','8080'),('tcp','4848')],source_ips=["0.0.0.0/0"],)
# print fwall