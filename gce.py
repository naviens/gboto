__author__ = 'naveen'

import sys
from gce.connection import GCEConnection


client_secrets = 'client_secrets.json'
project_id = 'industrial-glow-533'
zone = 'us-central1-b'

conn = GCEConnection(client_secrets, project_id,zone)
# ins = conn.get_all_instances()
# print conn.terminate_instance('test-inst')

cre = conn.run_instance('test123','debian')
print cre