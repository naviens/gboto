__author__ = 'naveen'


class Address():
    """
    Represents a GCE Address.
    """

    def __init__(self, address):
        self.id = address.get('id')
        self.kind = address.get('kind')
        self.name = address.get('name')
        self.description = address.get('description')
        self.address = address.get('address')
        self.region = address.get('region')
        self.status = address.get('status')
        self.creation_timestamp = address.get('creationTimestamp')
        self.self_link = address.get('selfLink')
        self.users = address.get('users')

    def __repr__(self):
        return 'Address:%s' % self.id
