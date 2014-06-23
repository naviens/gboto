__author__ = 'naveen'


class Ramdisk():
    """
    Represents a GCE Ramdisk.
    """

    def __init__(self, ramdisk):
        self.id = ramdisk.get('id')
        self.name = ramdisk.get('name')
        self.kind = ramdisk.get('kind')
        self.description = ramdisk.get('description')
        self.creation_timestamp = ramdisk.get('creationTimestamp')
        self.self_link = ramdisk.get('selfLink')

    def __repr__(self):
        return 'Ramdisk:%s' % self.id