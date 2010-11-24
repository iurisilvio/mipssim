import unittest

from mips import Mips

class TestExamples(unittest.TestCase):

    def test_project_example(self):
        text = """00100000000010100000000001100100 ; I1: addi R10,R0,100
                  10101100000000000000000000011000 ; I2: sw R0,24(R0)
                  10101100000000000000000000011100 ; I3: sw R0,28(R0)
                  10001100000001100000000000011100 ; I4: lw R6,28(R0)
                  00000000110001100011100000011000 ; I5: mul R7,R6,R6
                  10001100000000010000000000011000 ; I6: lw R1,24(R0)
                  00000000001001110100100000100000 ; I7: add R9,R1,R7
                  10101100000010010000000000011000 ; I8: sw R9,24(R0)
                  00100000110001100000000000000001 ; I9: addi R6,R6,1
                  10101100000001100000000000011100 ; I10: sw R6,28(R0)
                  00011100110010100000000000001100 ; I11: ble R6,R10,12"""
        mips = Mips(text)
        mips.run()
        self.assertEqual(mips.memory[24], 338350)
        
    def test_if_example_with_beq_false(self):
        text = """00100000000000010000000000000011 ; I1: addi R1,R0,3
                  00100000000000100000000000000010 ; I2: addi R2,R0,2
                  00010100001000100000000000000000 ; I3: beq R1,R2,0
                  00001000000000000000000000011000 ; I4: jmp 24
                  00100000000000010000000000000101 ; I5: addi R1,R0,5
                  00001000000000000000000000011100 ; I6: jmp 28
                  00100000000000010000000000000111 ; I7: addi R1,R0,7"""
        mips = Mips(text)
        mips.run()
        self.assertEqual(mips.registers[1], 7)
        
    def test_if_example_with_beq_true(self):
        text = """00100000000000010000000000000010 ; I1: addi R1,R0,2
                  00100000000000100000000000000010 ; I2: addi R2,R0,2
                  00010100001000100000000000000000 ; I3: beq R1,R2,0
                  00001000000000000000000000011000 ; I4: jmp 24
                  00100000000000010000000000000101 ; I5: addi R1,R0,5
                  00001000000000000000000000011100 ; I6: jmp 28
                  00100000000000010000000000000111 ; I7: addi R1,R0,7"""
        mips = Mips(text)
        mips.run()
        self.assertEqual(mips.registers[1], 5)
    
