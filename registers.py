

class Registers(object):
    def __init__(self, size=32, **kwargs):
        self.array = [0] * size
        self.dict = kwargs

    def __getitem__(self, key):
        if isinstance(key, int):
            value = self.array[key]
        elif isinstance(key, basestring):
            value = self.dict.get(key)
        else:
            raise AttributeError()
            
        return value
            
    def __setitem__(self, key, value):
        if isinstance(key, int):
            self.array[key] = value
        elif isinstance(key, basestring):
            self.dict[key] = value
        else:
            raise AttributeError()
