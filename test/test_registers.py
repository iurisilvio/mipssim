import unittest

from registers import Registers, RegisterInUseException

class TestRegisters(unittest.TestCase):
    def setUp(self):
        self.registers = Registers()
        
    def test_access_register(self):
        self.assertEqual(self.registers[0], 0)
        self.assertEqual(self.registers[10], 0)
    
    def test_change_registers(self):
        self.registers[3] = 10
        self.assertEqual(self.registers[3], 10)
        
    def test_locked_register(self):
        self.registers.lock(3)
        self.assertRaises(RegisterInUseException, self.registers.__getitem__, 3)
    
    def test_unlock_register(self):
        self.registers[3] = 4

        self.registers.lock(3)
        self.registers.unlock(3)
        
        self.assertEqual(self.registers[3], 4)
        self.registers[3] = 0
        self.assertEqual(self.registers[3], 0)

    def test_not_number_key(self):
        self.assertRaises(AttributeError, self.registers.__getitem__, "key")
        self.assertRaises(AttributeError, self.registers.__setitem__, "key", "value")
        
    
class TestTemporaryRegisters(unittest.TestCase):
    def setUp(self):
        self.registers = Registers()
        self.registers[3] = 4
        self.registers.lock(3)
        
    def test_set_register_locked(self):
        self.registers[3] = 2
        self.assertEqual(self.registers._array[3], 4)
        self.assertEqual(self.registers._tmp[3], 2)
        
    def test_get_register_locked_without_tmp_value(self):
        self.assertRaises(RegisterInUseException, self.registers.__getitem__, 3)

    def test_get_register_locked_with_tmp_value(self):
        self.registers[3] = 2
        self.assertEqual(self.registers[3], 2)

    def test_get_register_after_unlock(self):
        self.registers[3] = 2
        self.registers.unlock(3)
        self.assertEqual(self.registers._array[3], 4)
        self.registers[3] = 2
        self.assertEqual(self.registers._array[3], 2)


class TestRegisterInUseException(unittest.TestCase):
    def setUp(self):
        self.exception = RegisterInUseException(3)
        
    def test_exception(self):
        def raise_exception(exception):
            raise exception
            
        self.assertRaises(RegisterInUseException, raise_exception, self.exception)
    
    
if __name__ == "__main__":
    unittest.main()
