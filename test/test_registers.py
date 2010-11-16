import unittest

from registers import Registers

class TestRegisters(unittest.TestCase):
    def setUp(self):
        self.registers = Registers(pc=0)
        
    def test_access_indexed_register(self):
        self.assertEqual(self.registers[0], 0)
        self.assertEqual(self.registers[10], 0)
    
    def test_change_indexed_registers(self):
        self.registers[3] = 10
        self.assertEqual(self.registers[3], 10)
        
    def test_access_to_keyword_register(self):
        self.assertEqual(self.registers["pc"], 0)
    
    def test_change_keyword_register(self):
        self.registers["pc"] += 4
        self.assertEqual(self.registers["pc"], 4)
        
    
if __name__ == "__main__":
    unittest.main()
