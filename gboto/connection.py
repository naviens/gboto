__author__ = 'naveen'

#!/usr/bin/env python

import logging
import httplib2
import time
from oauth2client.client import flow_from_clientsecrets
from oauth2client.file import Storage
from oauth2client.tools import run

from gboto.instance import Instance
from gboto.image import Image
from gboto.ramdisk import Ramdisk
from gboto.firewall import Firewall
from gboto.zone import Zone
from gboto.network import Network

import traceback
from apiclient.discovery import build
from apiclient.errors import HttpError
from httplib2 import HttpLib2Error
from oauth2client.client import AccessTokenRefreshError

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

    # Instance methods

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

        # Set optional fields with provided values.
        if service_email and scopes:
            instance['serviceAccounts'] = [{'email': service_email, 'scopes': scopes}]

        # Set the instance metadata if provided.
        instance['metadata'] = {}
        instance['metadata']['items'] = []
        if metadata:
            instance['metadata']['items'].extend(metadata)

        # Set the instance startup script if provided.
        if startup_script:
            startup_script_resource = {
                'key': 'startup-script', 'value': open(startup_script, 'r').read()}
            instance['metadata']['items'].append(startup_script_resource)

        # Set the instance startup script URL if provided.
        if startup_script_url:
            startup_script_url_resource = {
                'key': 'startup-script-url', 'value': startup_script_url}
            instance['metadata']['items'].append(startup_script_url_resource)

        gce_instance = self.service.instances().insert(project=self.project_id, body=instance, zone=zone).execute(
            http=self.http)

        if gce_instance and blocking:
            gce_instance = self._blocking_call(gce_instance)

        return Instance(gce_instance)

    def terminate_instance(self, name=None, zone=None):
        """
        Terminate a specific Google Compute Engine instance.

        :type name: string
        :param name: The name of the instance to terminate.

        """
        if not zone:
            zone = self.zone
        gce_instance = self.service.instances().delete(project=self.project_id, instance=name, zone=zone).execute(
            http=self.http)
        return gce_instance

    # Image methods

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

    def register_image(self):
        pass

    def deregister_image(self):
        pass

    def create_image(self):
        pass

    def reboot_instances(self):
        pass

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

        """
        gce_image = self.service.images().get(project=self.project_id, image=image_name).execute(
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

        """
        gce_zone = self.service.zones().get(project=self.project_id, zone=zone_name).execute(
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

        """
        gce_network = self.service.networks().get(project=self.project_id, network=network_name).execute(
            http=self.http)

        return Network(gce_network)

    # Address methods
    def allocate_address(self):
        pass

    def associate_address(self):
        pass

    def disassociate_address(self):
        pass

    def release_address(self):
        pass

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

        """
        gce_firewall = self.service.firewalls().get(project=self.project_id, firewall=firewall_name).execute(
            http=self.http)

        return Firewall(gce_firewall)

    def create_firewall(self, name, network_name, rules=[], source_ips=[], source_tags=[]):
        """

        :type name: string
        :param name: Name of the firewall

        :type network_name: string
        :param network_name: Name fo the network where firewall to be added

        :type rules: list
        :param rules: [('tcp','8080'),('tcp','4848')] list of tuples

        :type source_ips: list
        :param source_ips: ["0.0.0.0/0"]

        :type source_tags: list
        :param source_tags: ["apache-server","google-app"]

        :return: object
        """
        parms = dict()
        parms['name'] = name
        parms['network'] = "http://www.googleapis.com/compute/v1/project/{0}/global/networks/{1}".format(self.project_id, network_name)
        if rules:
            allowed = []
            for rule in rules:
                rul = dict()
                rul['IPProtocol'] = rule[0]
                rul['ports'] = (rule[1]).split(",")
                allowed.append(rul)

        if source_ips:
            parms["sourceRanges"] = source_ips

        if source_tags:
            parms["sourceTags"] = source_tags

        gce_firewall = self.service.firewalls().insert(project=self.project_id, body=parms).execute(
            http=self.http)
        return gce_firewall

    # Snapshot methods

    def get_all_snapshots(self):
        pass

    def create_snapshot(self):
        pass

    def delete_snapshot(self):
        pass

    def copy_snapshot(self):
        pass

    def trim_snapshots(self):
        pass

    def get_snapshot_attribute(self):
        pass

    def modify_snapshot_attribute(self):
        pass


    def _blocking_call(self, response):
        """Blocks until the operation status is done for the given operation.

        Args:
          response: The response from the API call.

        Returns:
          Dictionary response representing the operation.
        """

        status = response['status']

        while status != 'DONE' and response:
            operation_id = response['name']
            if 'zone' in response:
                zone = response['zone'].rsplit('/', 1)[-1]
                request = self.service.zoneOperations().get(
                    project=self.project_id, zone=zone, operation=operation_id)
            else:
                request = self.service.globalOperations().get(
                    project=self.project_id, operation=operation_id)
            response = self._execute_request(request)
            if response:
                status = response['status']
                logging.info(
                    'Waiting until operation is DONE. Current status: %s', status)
                if status != 'DONE':
                    time.sleep(3)

        return response

    def _execute_request(self, request):

        """Helper method to execute API requests.

        Args:
          request: The API request to execute.

        Returns:
          Dictionary response representing the operation if successful.

        Raises:
          ApiError: Error occurred during API call.
        """

        try:
            response = request.execute()
        except AccessTokenRefreshError, e:
            logging.error('Access token is invalid.')
            raise ApiError(e)
        except HttpError, e:
            logging.error('Http response was not 2xx.')
            raise ApiError(e)
        except HttpLib2Error, e:
            logging.error('Transport error.')
            raise ApiError(e)
        except Exception, e:
            logging.error('Unexpected error occured.')
            traceback.print_stack()
            raise ApiError(e)

        return response


class Error(Exception):
    """Base class for exceptions in this module."""
    pass


class ApiError(Error):
    """Error occurred during API call."""
    pass


class ApiOperationError(Error):
    """Raised when an API operation contains an error."""

    def __init__(self, error_list):
        """Initialize the Error.

        Args:
          error_list: the list of errors from the operation.
        """

        super(ApiOperationError, self).__init__()
        self.error_list = error_list

    def __str__(self):
        """String representation of the error."""

        return repr(self.error_list)


class DiskDoesNotExistError(Error):
    """Disk to be used for instance boot does not exist."""
    pass
