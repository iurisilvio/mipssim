_events = {}

def add_listener(event, method):
    if not _events.get(event):
        _events[event] = []
    _events[event].append(method)
    
def trigger(event, *args, **kwargs):
    listeners = _events.get(event, [])
    
    for listener in listeners:
        listener(*args, **kwargs)
        
    
