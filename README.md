gboto
=====

Python goto library for Google Compute Engine

###Usage

Python Interface for managing GCE

Here's an example:

```python
client_secrets = 'client_secrets.json'
project_id = 'myproject'
zone = 'us-central1-a'

#Create a connection object for gce
conn = GCEConnection(client_secrets, project_id, zone)

#list all instance associated with this account
print conn.get_all_instances()

```

### Google Compute Engine Setup

Download client_secrets.json for the google engine project and put in the place where your code resides 

Refer sample.py for more info


