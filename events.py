import logging

_events = {}

def add_listener(event, method):
    if not _events.get(event):
        _events[event] = []
    _events[event].append(method)

def remove_listener(event, method):
    listeners = _events.get(event, [])
    try:
        listeners.remove(method)
    except ValueError:
        logging.info("Method '%s' not listening event '%s'" % (repr(method), event))
    
def trigger(event, *args, **kwargs):
    listeners = _events.get(event, [])
    
    for listener in listeners:
        listener(*args, **kwargs)

