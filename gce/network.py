__author__ = 'naveen'

class Network():
    """
    Represents a GCE Network.
    """
    def __init__(self, network):
        self.id = network.get('id')
        self.kind = network.get('kind')
        self.description = network.get('description')
        self.ip_range = network.get('IPv4Range')
        self.self_link = network.get('selfLink')
        self.name = network.get('name')
        self.creation_timestamp = network.get('creationTimestamp')
        self.gateway_ip = network.get('gatewayIPv4')

    def __repr__(self):
        return 'Network:%s' % self.id