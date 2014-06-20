__author__ = 'naveen'

class Instance():
    """
    Represents a GCE Instance.
    """
    def __init__(self, instance):
        self.id = instance['id']
        self.status = instance['status']
        self.kind = instance['kind']
        self.name = instance['name']
        self.self_link = instance['selfLink']
        # self.image = instance['image']
        self.machine_type = instance['machineType']
        self.zone = instance['zone']

    def __repr__(self):
        return 'Instance:%s' % self.id
