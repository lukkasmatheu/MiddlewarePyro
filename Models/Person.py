from unicodedata import name


class Person:
    def __init__(self,name,uri,publicKey):
        self.name = name
        self.publicKey= publicKey
        self.referenceRemote = uri

    @classmethod
    def from_dict(self, data):
        return self(data['name'], data['referenceRemote'], data['publicKey'])