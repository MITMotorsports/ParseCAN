from .. import spec, plural


class Board:
    def __init__(self, name, arch=None, location=None, publish=None, subscribe=None):
        self.name = name
        self.arch = arch
        self.location = location
        self.publish = publish
        self.subscribe = subscribe

    @property
    def publish(self):
        return self._publish

    @publish.setter
    def publish(self, publish):
        self._publish = plural.Unique('name', type=spec.busFiltered)

        for bus in publish or ():
            self._publish.safe_add(bus)

    @property
    def subscribe(self):
        return self._subscribe

    @subscribe.setter
    def subscribe(self, subscribe):
        self._subscribe = plural.Unique('name', type=spec.busFiltered)

        for bus in subscribe or ():
            self._subscribe.safe_add(bus)
