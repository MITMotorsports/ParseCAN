from .. import spec, helper

class BoardType:
    def __init__(self, name, arch=None, location=None, publish=None, subscribe=None):
        self.name = name
        self.arch = arch
        self.location = location
        self.publish = publish if publish else {}
        self.subscribe = subscribe if subscribe else {}
