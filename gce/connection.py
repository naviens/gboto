__author__ = 'naveen'

#!/usr/bin/env python

import logging
import httplib2
from oauth2client.client import flow_from_clientsecrets
from oauth2client.file import Storage
from oauth2client.tools import run
from apiclient.discovery import build

from boto.gce.instance import Instance


OAUTH2_STORAGE = 'oauth2.dat'
GCE_SCOPE = 'https://www.googleapis.com/auth/compute'
API_VERSION = 'v1'


class GCEConnection(object):

    def __init__(self, client_secrets, project_id):
        logging.basicConfig(level=logging.INFO)

        self.project_id = project_id
        self.storage = Storage('oauth2.dat')
        self.credentials = self.storage.get()
        self.default_network = "https://www.googleapis.com/compute/{0}/projects/google/networks/default".format(API_VERSION)
        self.gce_url = 'https://www.googleapis.com/compute/{0}/projects'.format(API_VERSION)

        # Perform OAuth 2.0 authorization.
        flow = flow_from_clientsecrets(client_secrets, scope=GCE_SCOPE)

        if self.credentials is None or self.credentials.invalid:
            self.credentials = run(flow, self.storage)

        self.http = self.credentials.authorize(httplib2.Http())
        self.service = build("compute", API_VERSION, http=self.http)

    # Instance Operations

    def get_all_instances(self, default_zone, list_filter=None):
        """
        Retrieve all the Google Compute Engine instances available to specific
        project.
        """
        list_gce_instances = self.service.instances().list(
            project=self.project_id, filter=list_filter, zone=default_zone).execute(http=self.http)

        list_instances = []
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

        gce_instance = self.service.instances().insert(project=self.gce_project,
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
        gce_instance = self.service.instances().delete(project=self.gce_project,
                                                       instance=name).execute(
                                                           http=self.http)