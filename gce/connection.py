__author__ = 'naveen'

#!/usr/bin/env python

import logging
import httplib2
from oauth2client.client import flow_from_clientsecrets
from oauth2client.file import Storage
from oauth2client.tools import run
from apiclient.discovery import build

from gce.instance import Instance


OAUTH2_STORAGE = 'oauth2.dat'
GCE_SCOPE = 'https://www.googleapis.com/auth/compute'
API_VERSION = 'v1'
DEFAULT_ZONE = 'us-central1-a'


class GCEConnection(object):

    def __init__(self, client_secrets, project_id, zone=None):
        logging.basicConfig(level=logging.INFO)

        self.project_id = project_id
        self.storage = Storage('oauth2.dat')
        self.credentials = self.storage.get()
        self.default_network = "https://www.googleapis.com/compute/{0}/projects/google/networks/default".format(API_VERSION)
        self.gce_url = 'https://www.googleapis.com/compute/{0}/projects'.format(API_VERSION)
        if zone is None:
            self.zone = DEFAULT_ZONE
        else:
            self.zone = zone

        # Perform OAuth 2.0 authorization.
        flow = flow_from_clientsecrets(client_secrets, scope=GCE_SCOPE)

        if self.credentials is None or self.credentials.invalid:
            self.credentials = run(flow, self.storage)

        self.http = self.credentials.authorize(httplib2.Http())
        self.service = build("compute", API_VERSION, http=self.http)

    # Instance Operations

    def get_all_instances(self, list_filter=None):
        """
        Retrieve all the Google Compute Engine instances available to specific
        project.
        """
        list_gce_instances = self.service.instances().list(
            project=self.project_id, filter=list_filter, zone=self.zone).execute(http=self.http)

        print list_gce_instances

        list_instances = []
        if 'items' in list_gce_instances:
            for instance in list_gce_instances['items']:
                list_instances.append(Instance(instance))

        return list_instances

    def run_instance(self, name=None, image_name=None, machine_type=None,
                     zone_name=None):
        """
        Insert a Google Compute Engine instance into your cluster.

        :type name: string
        :param name: The name of the instance to insert.

        :rtype: :class:`boto.gce.operation.Operation`
        :return: A Google Compute Engine operation.
        """
        body = {
            'name': name,
            'image': image_name,
            'zone': zone_name,
            'machineType': machine_type,
            'networkInterfaces': [{
                'network': self.default_network
             }]
        }

        gce_instance = self.service.instances().insert(project=self.project_id,
                                                       body=body, zone=zone_name).execute(
                                                           http=self.http)
        return Instance(gce_instance)


    def terminate_instance(self, name=None):
        """
        Terminate a specific Google Compute Engine instance.

        :type name: string
        :param name: The name of the instance to terminate.

        :rtype: :class:`boto.gce.operation.Operation`
        :return: A Google Compute Engine operation.
        """
        gce_instance = self.service.instances().delete(project=self.project_id,
                                                       instance=name, zone=self.zone).execute(
                                                           http=self.http)
        return gce_instance

    def reboot_instance(self):
        pass


