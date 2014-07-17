__author__ = 'naveen'


class Snapshot():
    """
    Represents a GCE Snapshot.
    """

    def __init__(self, snapshot):
        self.id = snapshot.get('id')
        self.kind = snapshot.get('kind')
        self.name = snapshot.get('name')
        self.description = snapshot.get('description')
        self.source_disk_id = snapshot.get('sourceDiskId')
        self.disk_size_gb = snapshot.get('diskSizeGb')
        self.status = snapshot.get('status')
        self.creation_timestamp = snapshot.get('creationTimestamp')
        self.self_link = snapshot.get('selfLink')

    def __repr__(self):
        return 'Snapshots:%s' % self.id
