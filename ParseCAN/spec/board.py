from .. import spec, plural


class BoardType:
    def __init__(self, name, arch=None, location=None, publish=None, subscribe=None):
        self.name = name
        self.arch = arch
        self.location = location
        self.__publish = plural.unique('name', type=spec.busFiltered)
        self.__subscribe = plural.unique('name', type=spec.busFiltered)

        for bus in publish or ():
            self.__publish.safe_add(bus)

        for bus in subscribe or ():
            self.__subscribe.safe_add(bus)

    @property
    def publish(self):
        return self.__publish

    @property
    def subscribe(self):
        return self.__subscribe
