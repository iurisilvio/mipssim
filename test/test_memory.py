import unittest

from memory import Memory


class TestMemory(unittest.TestCase):
    def setUp(self):
        self.memory = Memory(size=64)
        
    def test_assign_value(self):
        self.memory[42] = 3
        self.assertEqual(self.memory[42], 3)
    
    def test_not_assigned_position(self):
        self.assertEqual(self.memory[30], 0)
        
    def test_store_add_to_history(self):
        self.memory[2] = 3
        self.assertEqual(self.memory.history[-1], ('sw', 2, 3))
        
    def test_load_add_to_history(self):
        self.memory[0]
        self.assertEqual(self.memory.history[-1], ('lw', 0, 0))
        
    def test_some_loads_and_stores(self):
        self.memory[0] = 1
        _ = self.memory[2]
        self.memory[5] = 2
        self.memory[10] = 3
        _ = self.memory[5]
        
        self.assertEqual(self.memory.history[0], ('sw', 0, 1))
        self.assertEqual(self.memory.history[1], ('lw', 2, 0))
        self.assertEqual(self.memory.history[2], ('sw', 5, 2))
        self.assertEqual(self.memory.history[3], ('sw', 10, 3))
        self.assertEqual(self.memory.history[4], ('lw', 5, 2))
        
    def test_access_out_of_memory(self):
        self.assertRaises(IndexError, self.memory.__getitem__, 100)
