from .. import spec

class BoardSpec:
    def __init__(self, name, location=None, publish=None, subscribe=None):
        self.publish = {}
        self.subscribe = {}

    def upsert_publish(self, pub):
        assert isinstance(pub, spec.message)
        replacement = pub.name in self.publish and self.publish[pub.name] != pub
        self.publish[pub.name] = pub

        return replacement

    def upsert_subscribe(self, sub):
        assert isinstance(sub, spec.message)
        replacement = sub.name in self.subscribe and self.subscribe[sub.name] != sub
        self.subscribe[sub.name] = sub

        return replacement
