from copy import copy
import logging

class RegisterInUseException(BaseException):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return "<RegisterInUseException %s>" % self.value
        
    
class Registers(object):
    def __init__(self, size=32, **kwargs):
        self._array = [0] * size
        self._locks = set()
        self._tmp = {}
        
    def __getitem__(self, key):
        if key in self._locks:
            try:
                return self._tmp[key]
            except KeyError:
                raise RegisterInUseException(key)

        if isinstance(key, int):
            value = self._array[key]
        else:
            raise AttributeError()
        return value
            
    def __setitem__(self, key, value):
        if key in self._locks:
            self._tmp[key] = value
        elif isinstance(key, int):
            self._array[key] = value
        else:
            raise AttributeError()
            
    def lock(self, key):
        self._locks.add(key)
        
    def unlock(self, key):
        try:
            self._locks.remove(key)
            try:
                self._tmp.pop(key)
            except KeyError:
                pass
        except KeyError:
            logging.info("Trying to unlock '%s' but it is not locked.", key)
    
    def current_state(self):
        return copy(self._array)
