__author__ = 'naveen'

class Zone():
    """
    Represents a GCE Zone.
    """
    def __init__(self, zone):
        self.status = zone.get('status')
        self.kind = zone.get('kind')
        self.creation_timestamp = zone.get('creationTimestamp')
        self.id = zone.get('id')
        self.self_link = zone.get('selfLink')
        self.name = zone.get('name')

    def __repr__(self):
        return 'Zone:%s' % self.id