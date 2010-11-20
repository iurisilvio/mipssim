from copy import copy

class RegisterInUseException(BaseException):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return "<RegisterInUseException %s>" % self.value

class Registers(object):
    def __init__(self, size=32, **kwargs):
        self._array = [0] * size
        self._locks = set()
        self._dict = kwargs

    def __getitem__(self, key):
        if key in self._locks:
            raise RegisterInUseException(key)

        if isinstance(key, int):
            value = self._array[key]
        elif isinstance(key, basestring):
            value = self._dict.get(key)
        else:
            raise AttributeError()
        return value
            
    def __setitem__(self, key, value):
        if key in self._locks:
            raise RegisterInUseException(key)
    
        if isinstance(key, int):
            self._array[key] = value
        elif isinstance(key, basestring):
            self._dict[key] = value
        else:
            raise AttributeError()
            
    def lock(self, key):
        self._locks.add(key)
        
    def unlock(self, key):
        try:
            self._locks.remove(key)
        except KeyError:
            logging.info("Trying to unlock '%s' but it is not locked.", key)
            
    def current_state(self):
        return {"r":copy(self._array),
                "keys":copy(self._dict),
                "locks":copy(self._locks)}
