import unittest

from mips import Mips
import instructions
from instructions import (Instruction, AddInstruction, AddiInstruction,
                          MulInstruction, NopInstruction)

class TestOneInstructionOnMips(unittest.TestCase):
    def _exec_pipeline(self, times):
        for i in range(times):
            self.mips.execute_pipeline()

    def setUp(self):
        text = """00000000001001110100100000100000 ; I1: add R9,R1,R7"""
        self.mips = Mips(text)

    def test_first_step(self):
        self._exec_pipeline(1)
        self.assertTrue(isinstance(self.mips.pipeline[0].instruction, AddInstruction));
        self.assertTrue(self.mips.pipeline[0].done)

    def test_two_steps(self):
        self._exec_pipeline(2)
        self.assertTrue(isinstance(self.mips.pipeline[1].instruction, AddInstruction));
        self.assertTrue(self.mips.pipeline[1].done)

    def test_three_steps(self):
        self._exec_pipeline(3)
        self.assertTrue(isinstance(self.mips.pipeline[2].instruction, AddInstruction));
        self.assertTrue(self.mips.pipeline[2].done)

    def test_four_steps(self):
        self._exec_pipeline(4)
        self.assertTrue(isinstance(self.mips.pipeline[3].instruction, AddInstruction));
        self.assertTrue(self.mips.pipeline[3].done)

    def test_five_steps(self):
        self._exec_pipeline(5)
        self.assertTrue(isinstance(self.mips.pipeline[4].instruction, AddInstruction));
        self.assertTrue(self.mips.pipeline[4].done)

    def test_six_steps(self):
        self._exec_pipeline(6)
        for item in self.mips.pipeline:
            self.assertTrue(isinstance(item.instruction, NopInstruction));


class TestMipsPipelineSteps(unittest.TestCase):
    def setUp(self):
        self.mips = Mips()
        self.add = Instruction('00000000001001110100100000100000 ; I1: add R9,R1,R7')
        self.addi = Instruction('00100000000010100000000001100100 ; I2: addi R10,R0,100')
        
    def test_an_intermediary_step(self):
        self.add.instruction_decode(self.mips.registers)
        self.add.execute(self.mips.registers)
        self.addi.instruction_decode(self.mips.registers)

        self.mips.pipeline[2].instruction = self.addi
        self.mips.pipeline[3].instruction = self.add
        self.mips.execute_pipeline()
        self.assertEqual(self.mips.pipeline[2].instruction, self.addi)
        self.assertTrue(self.mips.pipeline[2].done)
        self.assertEqual(self.mips.pipeline[3].instruction, self.add)
        self.assertTrue(self.mips.pipeline[3].done)
        
        
class TestMips(unittest.TestCase):
    def setUp(self):
        text = """00000000001001110100100000100000 ; I1: add R9,R1,R7
                  00000000000000010001000000011000 ; I2: mul R2,R0,R1
                  00100000000010100000000001100100 ; I3: addi R10,R0,100"""
        self.mips = Mips(text)

    def test_first_step(self):
        self.mips.execute_pipeline()
        self.assertTrue(isinstance(self.mips.pipeline[0].instruction, AddInstruction))
        
    def test_mul_blocking(self):
        self.mips.execute_pipeline()
        self.mips.execute_pipeline()
        self.mips.execute_pipeline()
        self.mips.execute_pipeline()
        self.assertTrue(isinstance(self.mips.pipeline[1].instruction, AddiInstruction))
        self.assertTrue(isinstance(self.mips.pipeline[2].instruction, MulInstruction))
        self.assertTrue(isinstance(self.mips.pipeline[3].instruction, AddInstruction))
        self.mips.execute_pipeline()
        self.assertTrue(isinstance(self.mips.pipeline[1].instruction, AddiInstruction))
        self.assertTrue(isinstance(self.mips.pipeline[2].instruction, MulInstruction))
        self.assertTrue(isinstance(self.mips.pipeline[4].instruction, AddInstruction))


class TestGoForwardPipeline(unittest.TestCase):
    def setUp(self):
        self.mips = Mips()
        self.mips.pipeline[0].instruction = NopInstruction()
        self.mips.pipeline[0].done = True
        self.mips.pipeline[1].instruction = NopInstruction()
        self.mips.pipeline[1].done = True
        self.mips.pipeline[2].instruction = NopInstruction()
        self.mips.pipeline[2].done = False
        self.mips.pipeline[3].instruction = NopInstruction()
        self.mips.pipeline[3].done = True
        
    def test_bubble_problems(self):
        self.mips._go_forward_pipeline()
        self.assertTrue(isinstance(self.mips.pipeline[0].instruction, NopInstruction))
        self.assertTrue(isinstance(self.mips.pipeline[1].instruction, NopInstruction))
        self.assertTrue(isinstance(self.mips.pipeline[2].instruction, NopInstruction))
        self.assertTrue(self.mips.pipeline[3].instruction is None)
        self.assertTrue(isinstance(self.mips.pipeline[4].instruction, NopInstruction))
        
        
class TestInstructionDependencies(unittest.TestCase):
    def setUp(self):
        text = '''00000000001001110100100000100000 ; I1: add R9,R1,R7
                  00000000011010010000100000100000 ; I2: add R1,R3,R9'''
        self.mips = Mips(text)
        self.mips.enable_bypassing(False)
        
    def test_first_stall(self):
        mips = self.mips
        mips.execute_pipeline()
        mips.execute_pipeline()
        mips.execute_pipeline()
        self.assertTrue(isinstance(mips.pipeline[1].instruction, AddInstruction))
        self.assertTrue(isinstance(mips.pipeline[2].instruction, AddInstruction))
        mips.execute_pipeline()
        self.assertTrue(isinstance(mips.pipeline[1].instruction, AddInstruction))
        self.assertTrue(isinstance(mips.pipeline[3].instruction, AddInstruction))
    
    def test_i2_continue_after_i1_finished(self):
        mips = self.mips
        mips.execute_pipeline()
        mips.execute_pipeline()
        mips.execute_pipeline()
        mips.execute_pipeline()
        mips.execute_pipeline()
        mips.execute_pipeline()
        self.assertTrue(isinstance(mips.pipeline[1].instruction, AddInstruction))
        mips.execute_pipeline()
        self.assertTrue(isinstance(mips.pipeline[2].instruction, AddInstruction))


class TestBranching(unittest.TestCase):
    def test_without_branch(self):
        text = '''00100000010000100000000000000101 ; I1: addi R2,R2,5
                  00100000001000010000000000001010 ; I2: addi R1,R1,10
                  00011100001000100000000000000100 ; I3: ble R1,R2,4
                  00100000001000010000000001000000 ; I4: addi R1,R1,64'''
        self.mips = Mips(text)
        self.mips.run()
        self.assertEqual(self.mips.registers[1], 74)

    def test_with_branch(self):
        text = '''00100000010000100000000000100011 ; I1: addi R2,R2,35
                  00100000001000010000000000001101 ; I2: addi R1,R1,13
                  00011100001000100000000000000100 ; I3: ble R1,R2,4
                  00100000001000010000000000100000 ; I4: addi R1,R1,32'''
        self.mips = Mips(text)
        self.mips.run()

        self.assertEqual(self.mips.registers[1], 71)


class TestBypassing(unittest.TestCase):
    def setUp(self):
        text = """00100000000000010000000000000011 ; I1: addi R1,R0,3
                  00100000001000100000000000000010 ; I2: addi R2,R1,2"""
        self.mips = Mips(text)
        
    def test_without_bypassing(self):
        self.mips.enable_bypassing(False)
        self.mips.execute_pipeline()
        self.mips.execute_pipeline()
        self.mips.execute_pipeline()
        self.assertTrue(isinstance(self.mips.pipeline[1].instruction, AddiInstruction))
        self.assertTrue(isinstance(self.mips.pipeline[2].instruction, AddiInstruction))
        self.mips.execute_pipeline()
        self.mips.execute_pipeline()
        self.assertTrue(isinstance(self.mips.pipeline[1].instruction, AddiInstruction))
        self.assertTrue(isinstance(self.mips.pipeline[4].instruction, AddiInstruction))
        self.mips.execute_pipeline()
        self.assertTrue(isinstance(self.mips.pipeline[1].instruction, AddiInstruction))
        self.mips.execute_pipeline()
        self.assertTrue(isinstance(self.mips.pipeline[2].instruction, AddiInstruction))


    def test_with_bypassing(self):
        self.mips.enable_bypassing(True)
        self.mips.execute_pipeline()
        self.mips.execute_pipeline()
        self.mips.execute_pipeline()
        self.assertTrue(isinstance(self.mips.pipeline[1].instruction, AddiInstruction))
        self.assertTrue(isinstance(self.mips.pipeline[2].instruction, AddiInstruction))
        self.mips.execute_pipeline()
        self.assertTrue(isinstance(self.mips.pipeline[1].instruction, AddiInstruction))
        self.assertTrue(isinstance(self.mips.pipeline[3].instruction, AddiInstruction))
        self.mips.execute_pipeline()
        self.assertTrue(isinstance(self.mips.pipeline[2].instruction, AddiInstruction))
        self.assertTrue(isinstance(self.mips.pipeline[4].instruction, AddiInstruction))
        self.mips.execute_pipeline()
        self.assertTrue(isinstance(self.mips.pipeline[3].instruction, AddiInstruction))
        
    
