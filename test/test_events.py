import unittest

class TestEvents(unittest.TestCase):
    def setUp(self):
        import events
        self.events = events
        self.count = 0

    def listener(self, *args, **kwargs):
        count = sum(args) if args else 1
        self.count += count

    def test_trigger_without_listeners(self):
        self.events.trigger("test")
    
    def test_add_listener(self):
        self.events.add_listener("test", self.listener)
        self.assertEqual(len(self.events._events["test"]), 1)

    def test_trigger(self):
        self.events.add_listener("test", self.listener)
        self.events.trigger("test")
        self.assertEqual(self.count, 1)
        
    def test_listener_with_parameters(self):
        self.events.add_listener("test", self.listener)
        self.events.trigger("test", 1, 2)
        self.assertEqual(self.count, 3)
        
    def test_remove_listener(self):
        self.events.add_listener("test", self.listener)
        self.events.remove_listener("test", self.listener)
        
    def test_remove_inexistent_listener(self):
        self.events.remove_listener("test", self.listener)
        

