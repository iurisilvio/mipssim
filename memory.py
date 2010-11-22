

class Memory(object):
    def __init__(self, size=1024):
        self._array = [0] * size
        self.history = []
        
    def __getitem__(self, key):
        value = self._array[key]
        self.history.append(('lw', key, value))
        return value
        
    def __setitem__(self, key, value):
        self.history.append(('sw', key, value))
        self._array[key] = value
