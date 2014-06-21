__author__ = 'naveen'
class Image():
    """
    Represents a GCE Image.
    """
    def __init__(self, image):
        self.id = image.get('id')
        self.name = image.get('name')
        self.kind = image.get('kind')
        self.self_link = image.get('selfLink')
        self.creation_timestamp = image.get('creationTimestamp')
        self.description = image.get('description')
        self.raw_disk = image.get('rawDisk')
        self.preferred_kernel = image.get('preferredKernel')
        self.source_type = image.get('sourceType')

    def __repr__(self):
        return 'Image:%s' % self.id
