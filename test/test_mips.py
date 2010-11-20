import unittest

from mips import Mips
import instructions

class TestMips(unittest.TestCase):
    def setUp(self):
        text = """00000000001001110100100000100000 ; I1: add R9,R1,R7
                  00000000000000010001000000011000 ; I2: mul R2,R0,R1
                  00100000000010100000000001100100 ; I3: addi R10,R0,100"""
        self.mips = Mips(text)
        
    def test_fetch_instruction(self):
        instruction = self.mips.fetch_instruction()
        self.assertTrue(isinstance(instruction, instructions.AddInstruction))
        self.assertEqual(self.mips.registers["pc"], 4)
        
    
