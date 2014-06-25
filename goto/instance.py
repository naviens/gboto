__author__ = 'naveen'


class Instance():
    """
    Represents a GCE Instance.
    """

    def __init__(self, instance):
        self.id = instance.get('id')
        self.status = instance.get('status')
        self.kind = instance.get('kind')
        self.name = instance.get('name')
        self.self_link = instance.get('selfLink')
        self.image = instance.get('image')
        self.machine_type = instance.get('machineType')
        self.zone = instance.get('zone')

    def __repr__(self):
        return 'Instance:%s' % self.id
