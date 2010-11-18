import unittest

from registers import Registers, RegisterInUseException

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
        
    def test_locked_register(self):
        self.registers.lock(3)
        self.assertRaises(RegisterInUseException, self.registers.__getitem__, 3)
        self.assertRaises(RegisterInUseException, self.registers.__setitem__, 3, "anything")
    
    def test_unlock_register(self):
        self.registers[3] = 4

        self.registers.lock(3)
        self.registers.unlock(3)
        
        self.assertEquals(self.registers[3], 4)
        self.registers[3] = 0
        self.assertEquals(self.registers[3], 0)



class TestRegisterInUseException(unittest.TestCase):
    def setUp(self):
        self.exception = RegisterInUseException(3)
        
    def test_exception(self):
        def raise_exception(exception):
            raise exception
            
        self.assertRaises(RegisterInUseException, raise_exception, self.exception)
    
    
if __name__ == "__main__":
    unittest.main()
