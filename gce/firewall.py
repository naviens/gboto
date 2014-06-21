__author__ = 'naveen'

class Firewall():
    """
    Represents a GCE Firewall.
    """
    def __init__(self, firewall):
        self.id = firewall.get('id')
        self.kind = firewall.get('kind')
        self.description = firewall.get('description')
        self.source_ranges = firewall.get('sourceRanges')
        self.network = firewall.get('network')
        self.allowed = firewall.get('allowed')
        self.creation_timestamp = firewall.get('creationTimestamp')
        self.self_link = firewall.get('selfLink')
        self.name = firewall.get('name')

    def __repr__(self):
        return 'Firewall:%s' % self.id
