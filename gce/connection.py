__author__ = 'naveen'

#!/usr/bin/env python

import logging
import httplib2
from oauth2client.client import flow_from_clientsecrets
from oauth2client.file import Storage
from oauth2client.tools import run
from apiclient.discovery import build

from gce.instance import Instance
from gce.image import Image
from gce.ramdisk import Ramdisk
from gce.firewall import Firewall
from gce.zone import Zone
from gce.network import Network


OAUTH2_STORAGE = 'oauth2.dat'
GCE_SCOPE = 'https://www.googleapis.com/auth/compute'
API_VERSION = 'v1'
DEFAULT_ZONE = 'us-central1-a'
DISK_TYPE = 'PERSISTENT'
DEFAULT_MACHINE_TYPE = 'n1-standard-1'
DEFAULT_NETWORK = 'default'


class GCEConnection(object):
    def __init__(self, client_secrets, project_id, zone=None):
        logging.basicConfig(level=logging.INFO)

        self.project_id = project_id
        self.storage = Storage('oauth2.dat')
        self.credentials = self.storage.get()
        self.default_network = "https://www.googleapis.com/compute/{0}/projects/google/networks/default".format(
            API_VERSION)
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
                     image_cloud,
                     image_name,
                     machine_type=DEFAULT_MACHINE_TYPE,
                     zone=DEFAULT_ZONE,
                     network=DEFAULT_NETWORK,
                     auto_delete=False,
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

        :type image_cloud: string
        :param image_cloud: ['centos-cloud','rhel-cloud','suse-cloud','debian-cloud']

        :type image_cloud: string
        :param image_cloud: ['centos-cloud','rhel-cloud','suse-cloud','debian-cloud']

        :type machine_type: string
        :param machine_type: ['f1-micro',
                 'g1-small',
                 'n1-highcpu-16',
                 'n1-highcpu-2',
                 'n1-highcpu-2-d',
                 'n1-highcpu-4',
                 'n1-highcpu-4-d',
                 'n1-highcpu-8',
                 'n1-highcpu-8-d',
                 'n1-highmem-16',
                 'n1-highmem-2',
                 'n1-highmem-2-d',
                 'n1-highmem-4',
                 'n1-highmem-4-d',
                 'n1-highmem-8',
                 'n1-highmem-8-d',
                 'n1-standard-1',
                 'n1-standard-1-d',
                 'n1-standard-16',
                 'n1-standard-2',
                 'n1-standard-2-d',
                 'n1-standard-4',
                 'n1-standard-4-d',
                 'n1-standard-8',
                 'n1-standard-8-d']

        :type zone: string
        :param zone: ['asia-east1-a','asia-east1-b','europe-west1-a','europe-west1-b','us-central1-1','us-central1-b']

        :type network: string
        :param network: 'default' for default network

        :type auto_delete: bool
        :param auto_delete: Delete the root disk when deleting the instance

        :rtype: :class:`boto.gce.operation.Operation`
        :return: A Google Compute Engine operation.
        """
        # Body dictionary is sent in the body of the API request.
        instance = dict()

        instance['name'] = name
        instance['image'] = image_name
        instance['zone'] = zone
        instance['machineType'] = '%s/zones/%s/machineTypes/%s' % (self.project_url, zone, machine_type)
        instance['networkInterfaces'] = [{'accessConfigs': [{'type': 'ONE_TO_ONE_NAT', 'name': 'External NAT'}],
                                          'network': '%s/global/networks/%s' % (self.project_url, network)}]
        image_url = '%s/%s/global/images/%s' % (self.gce_url, image_cloud, image_name)

        instance['disks'] = [{
                                 'autoDelete': auto_delete,
                                 'boot': True,
                                 'type': DISK_TYPE,
                                 'initializeParams': {
                                     'sourceImage': image_url
                                 }
                             }]

        gce_instance = self.service.instances().insert(project=self.project_id,
                                                       body=instance, zone=zone).execute(
            http=self.http)
        return Instance(gce_instance)

    def terminate_instance(self, name=None, zone=None):
        """
        Terminate a specific Google Compute Engine instance.

        :type name: string
        :param name: The name of the instance to terminate.

        :rtype: :class:`boto.gce.operation.Operation`
        :return: A Google Compute Engine operation.
        """
        if not zone:
            zone = self.zone
        gce_instance = self.service.instances().delete(project=self.project_id,
                                                       instance=name, zone=zone).execute(
            http=self.http)
        return gce_instance

    # Image Operation


    def get_all_images(self):
        """
        Retrieve all the Google Compute Engine images available to your
        project.
        """
        list_gce_images = self.service.images().list(
            project=self.project_id).execute(http=self.http)

        list_images = []
        if 'items' in list_gce_images:
            for image in list_gce_images['items']:
                list_images.append(Image(image))

        return list_images

    def get_all_ramdisks(self, zone=None):
        """
        Retrieve all the Google Compute Engine disks available to your project.
        """
        if not zone:
            zone = self.zone

        list_gce_ramdisks = self.service.disks().list(
            project=self.project_id, zone=zone).execute(http=self.http)

        list_ramdisks = []
        for ramdisk in list_gce_ramdisks['items']:
            list_ramdisks.append(Ramdisk(ramdisk))

    def get_image(self, image_name):
        """
        Shortcut method to retrieve a specific image.

        :type image_name: string
        :param image_name: The name of the Image to retrieve.

        :rtype: :class:`boto.gce.image.Image`
        :return: The Google Compute Engine Image specified, or None if the image
        is not found
        """
        gce_image = self.service.images().get(project=self.project_id,
                                              image=image_name).execute(
            http=self.http)
        return Image(gce_image)

    # Zone methods

    def get_all_zones(self):
        """
        Retrieve all the Google Compute Engine zones available to your project.
        """
        list_gce_zones = self.service.zones().list(
            project=self.project_id).execute(http=self.http)

        list_zones = []
        for zone in list_gce_zones['items']:
            list_zones.append(Zone(zone))

        return list_zones

    def get_zone(self, zone_name):
        """
        Shortcut method to retrieve a specific zone.

        :type zone_name: string
        :param zone_name: The name of the Zone to retrieve.

        :rtype: :class:`boto.gce.zone.Zone`
        :return: The Google Compute Engine Zone specified, or None if the zone
        is not found
        """
        gce_zone = self.service.zones().get(project=self.project_id,
                                            zone=zone_name).execute(
            http=self.http)

        return Zone(gce_zone)

    # Network methods

    def get_all_networks(self):
        """
        Retrieve all the Google Compute Engine networks available to your
        project.
        """
        list_gce_networks = self.service.networks().list(
            project=self.project_id).execute(http=self.http)

        list_networks = []
        for network in list_gce_networks['items']:
            # print dir(network)
            list_networks.append(Network(network))

        return list_networks

    def get_network(self, network_name):
        """
        Shortcut method to retrieve a specific network.

        :type network_name: string
        :param network_name: The name of the Network to retrieve.

        :rtype: :class:`boto.gce.network.Network`
        :return: The Google Compute Engine Network specified, or None if the
        network is not found
        """
        gce_network = self.service.networks().get(project=self.project_id,
                                                  network=network_name).execute(
            http=self.http)

        return Network(gce_network)

    # Firewall methods

    def get_all_firewalls(self):
        """
        Retrieve all the Google Compute Engine firewalls available to your
        project.
        """
        list_gce_firewalls = self.service.firewalls().list(
            project=self.project_id).execute(http=self.http)

        list_firewalls = []
        for firewall in list_gce_firewalls['items']:
            list_firewalls.append(Firewall(firewall))

        return list_firewalls

    def get_firewall(self, firewall_name):
        """
        Shortcut method to retrieve a specific firewall.

        :type firewall_name: string
        :param firewall_name: The name of the Firewall to retrieve.

        :rtype: :class:`boto.gce.firewall.Firewall`
        :return: The Google Compute Engine Firewall specified, or None if the
        firewall is not found
        """
        gce_firewall = self.service.firewalls().get(
            project=self.project_id, firewall=firewall_name).execute(
            http=self.http)

        return Firewall(gce_firewall)



