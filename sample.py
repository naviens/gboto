__author__ = 'naveen'

import sys
from gboto.connection import GCEConnection


client_secrets = 'client_secrets.json'
project_id = 'myproject'
zone = 'us-central1-a'


#Create a connection object for gce
conn = GCEConnection(client_secrets, project_id, zone)

#list all instance associated with this account
print conn.get_all_instances()

# create a instance with root disk will be deleted on termination of instance
print conn.run_instance('myfirstinstance1', 'debian-cloud', 'debian-7-wheezy-v20140606',auto_delete=True)

#terminate instance using name
print conn.terminate_instance('myfirstinstance1')

#List all images
print conn.get_all_images()

#List all images
print conn.get_all_zones()

