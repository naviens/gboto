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
DISK_TYPE = 'PERSISTENT'
DEFAULT_MACHINE_TYPE = 'n1-standard-1'
DEFAULT_NETWORK = 'default'
DEFAULT_IMAGES = {
    'debian': 'debian-7-wheezy-v20140606',
    'centos': 'centos-6-v20131120'
}


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
        self.project_url = '%s/%s' % (self.gce_url, self.project_id)

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

    def run_instance(self,
                     name,
                     image,
                     machine_type=DEFAULT_MACHINE_TYPE,
                     zone=DEFAULT_ZONE,
                     disk_name=None,
                     network=DEFAULT_NETWORK,
                     service_email=None,
                     scopes=None,
                     metadata=None,
                     startup_script=None,
                     startup_script_url=None,
                     blocking=True):
        """
        Insert a Google Compute Engine instance into your cluster.

        :type name: string
        :param name: The name of the instance to insert.

        :rtype: :class:`boto.gce.operation.Operation`
        :return: A Google Compute Engine operation.
        """
        # Body dictionary is sent in the body of the API request.
        instance = {}

        instance['name'] = name
        instance['image'] = image
        instance['zone'] = zone
        instance['machineType'] = '%s/zones/%s/machineTypes/%s' % (self.project_url, zone, machine_type)
        instance['networkInterfaces'] = [{'accessConfigs': [{'type': 'ONE_TO_ONE_NAT', 'name': 'External NAT'}],'network': '%s/global/networks/%s' % (self.project_url, network)}]
        image_url = '%s/%s/global/images/%s' % (self.gce_url, 'debian-cloud', DEFAULT_IMAGES[image])

        if not disk_name:
            disk_name = name

        instance['disks'] = [{
            'boot': True,
            'type': DISK_TYPE,
            'initializeParams': {
                'diskName': disk_name,
                'sourceImage': image_url
            }
          }]

        gce_instance = self.service.instances().insert(project=self.project_id,
                                                       body=instance, zone=zone).execute(
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


    # Image Operation


    def get_all_images(self):
        """
        Retrieve all the Google Compute Engine images available to your
        project.
        """
        list_gce_images = self.service.images().list(
            project=self.google_project).execute(http=self.http)

        list_images = []
        for image in list_gce_images['items']:
            list_images.append(Image(image))

        return list_images


