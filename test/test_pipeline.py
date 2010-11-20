import unittest

from mips import Mips
from pipeline import Pipeline
from instructions import NopInstruction

class TestPipeline(unittest.TestCase):
    def setUp(self):
        text = """00000000001001110100100000100000 ; I1: add R9,R1,R7
                  00000000000000010001000000011000 ; I2: mul R2,R0,R1
                  00100000000010100000000001100100 ; I3: addi R10,R0,100"""
        mips = Mips(text)
        self.pipeline = mips.pipeline

    def test_pipeline_start_with_nop(self):
        for p in self.pipeline._pipeline:
            self.assertTrue(isinstance(p.instruction, NopInstruction))
        
    def test_first_pipeline_run(self):
        self.pipeline.run()
        self.assertEqual(self.pipeline._pipeline[0].instruction.text, "I1: add R9,R1,R7")
        
    def test_two_pipeline_run(self):
        self.pipeline.run()
        self.pipeline.run()
        self.assertEqual(self.pipeline._pipeline[0].instruction.text, "I2: mul R2,R0,R1")
        self.assertEqual(self.pipeline._pipeline[1].instruction.text, "I1: add R9,R1,R7")
    
    def test_bubble(self):
        self.pipeline.run()
        self.pipeline.run()
        self.pipeline.run()
        self.pipeline.run()
        self.pipeline.run()
        self.assertTrue(isinstance(self.pipeline._pipeline[3].instruction, NopInstruction))
        self.pipeline.run()
        self.assertTrue(isinstance(self.pipeline._pipeline[4].instruction, NopInstruction))
        self.pipeline.run()


class TestPipelineDependencies(unittest.TestCase):
    def test_register_dependency(self):
        text = """00000000001001110100100000100000 ; I1: add R9,R1,R7
                  00000000000010010001000000100000 ; I2: add R2,R0,R9"""
        mips = Mips(text)

        # state before pipeline.run()
        # [_, _, _, _, _]
        mips.pipeline.run()
        
        i1 = mips.pipeline._pipeline[0].instruction
        self.assertEqual(mips.pipeline._pipeline[0].instruction, i1)
        
        # [i1, _, _, _, _]
        mips.pipeline.run()
        
        i2 = mips.pipeline._pipeline[0].instruction
        self.assertEqual(mips.pipeline._pipeline[0].instruction, i2)
        self.assertEqual(mips.pipeline._pipeline[1].instruction, i1)
        
        # [i2, i1, _, _, _]
        mips.pipeline.run()
        self.assertEqual(mips.pipeline._pipeline[1].instruction, i2)
        self.assertEqual(mips.pipeline._pipeline[2].instruction, i1)

        # [i2, _, i1, _, _]
        mips.pipeline.run()
        self.assertEqual(mips.pipeline._pipeline[1].instruction, i2)
        self.assertEqual(mips.pipeline._pipeline[3].instruction, i1)

        # [i2, _, _, i1, _]
        mips.pipeline.run()
        self.assertEqual(mips.pipeline._pipeline[1].instruction, i2)
        self.assertEqual(mips.pipeline._pipeline[4].instruction, i1)

        # [i2, _, _, _, i1]
        mips.pipeline.run()
        self.assertEqual(mips.pipeline._pipeline[1].instruction, i2)
        
        # [i2, _, _, _, _]
        mips.pipeline.run()
        self.assertEqual(mips.pipeline._pipeline[2].instruction, i2)
        
        # [_, i2, _, _, _]
        mips.pipeline.run()
        
        # [_, _, i2, _, _]
        mips.pipeline.run()
        self.assertEqual(mips.pipeline._pipeline[4].instruction, i2)

    def test_jump_dependency(self):
        text = """00000000001001110100100000100000 ; I1: add R9,R1,R7
                  00001000000000000000000000000000 ; I2: jmp 0"""
        mips = Mips(text)

        # state before pipeline.run()
        # [_, _, _, _, _]
        mips.pipeline.run()
        i1 = mips.pipeline._pipeline[0].instruction

        # [i1, _, _, _, _]
        mips.pipeline.run()
        
        i2 = mips.pipeline._pipeline[0].instruction
        self.assertEqual(mips.pipeline._pipeline[0].instruction, i2)
        self.assertEqual(mips.pipeline._pipeline[1].instruction, i1)
        
        # [i2, i1, _, _, _]
        mips.pipeline.run()
        self.assertEqual(mips.pipeline._pipeline[1].instruction, i2)
        self.assertEqual(mips.pipeline._pipeline[2].instruction, i1)

        # [_, i2, i1, _, _]
        mips.pipeline.run()
        self.assertEqual(mips.pipeline._pipeline[2].instruction, i2)
        self.assertEqual(mips.pipeline._pipeline[3].instruction, i1)

        # [_, _, i2, i1, _]
        mips.pipeline.run()
        self.assertEqual(mips.pipeline._pipeline[3].instruction, i2)
        self.assertEqual(mips.pipeline._pipeline[4].instruction, i1)
        
        # [_, _, _, i2, i1]
        mips.pipeline.run()
        self.assertEqual(mips.pipeline._pipeline[4].instruction, i2)
        
        # [_, _, _, _, i2]
        mips.pipeline.run()
        # after this last run: [i1, _, _, _, _]
        
        self.assertEqual(mips.registers["pc"], 4)
        self.assertEqual(mips.pipeline._pipeline[0].instruction.text, i1.text)

        # [i1, _, _, _, _]
        mips.pipeline.run()
        # after this last run: [i2, i1, _, _, _]
        self.assertEqual(mips.pipeline._pipeline[0].instruction.text, i2.text)
        self.assertEqual(mips.pipeline._pipeline[1].instruction.text, i1.text)
        
    def test_beq_branch(self):
        text = """00000000000000000000000000000000 ; I1: nop
                  00010100001000101111111111111000 ; I2: beq R1,R2,-8"""
        mips = Mips(text)
        mips.registers[1] = 5
        mips.registers[2] = 5

        # state before pipeline.run()
        # [_, _, _, _, _]
        mips.pipeline.run()
        i1 = mips.pipeline._pipeline[0].instruction

        # [i1, _, _, _, _]
        mips.pipeline.run()
        
        i2 = mips.pipeline._pipeline[0].instruction
        
        # [i2, i1, _, _, _]
        mips.pipeline.run()

        # [_, i2, i1, _, _]
        mips.pipeline.run()

        # [_, _, i2, i1, _]
        mips.pipeline.run()

        # [_, _, _, i2, i1]
        mips.pipeline.run()

        # [_, _, _, _, i2]
        mips.pipeline.run()
        # after this last run: [i1, _, _, _, _]
        
        self.assertTrue(isinstance(mips.pipeline._pipeline[4].instruction, NopInstruction))
        self.assertEqual(mips.registers["pc"], 4)
        self.assertEqual(mips.pipeline._pipeline[0].instruction.text, i1.text)

        # [i1, _, _, _, _]
        mips.pipeline.run()

        # after this last run: [i2, i1, _, _, _]
        self.assertEqual(mips.pipeline._pipeline[0].instruction.text, i2.text)
        self.assertEqual(mips.pipeline._pipeline[1].instruction.text, i1.text)
        
    def test_beq_pass(self):
        text = """00000000000000000000000000000000 ; I1: nop
                  00010100001000101111111111111000 ; I2: beq R1,R2,-8"""
        mips = Mips(text)
        mips.registers[1] = 1
        mips.registers[2] = 2

        # state before pipeline.run()
        # [_, _, _, _, _]
        mips.pipeline.run()
        i1 = mips.pipeline._pipeline[0].instruction

        # [i1, _, _, _, _]
        mips.pipeline.run()
        
        i2 = mips.pipeline._pipeline[0].instruction
        
        # [i2, i1, _, _, _]
        mips.pipeline.run()

        # [_, i2, i1, _, _]
        mips.pipeline.run()

        # [_, _, i2, i1, _]
        mips.pipeline.run()
        
        # [_, _, _, i2, i1]
        mips.pipeline.run()
        
        # [_, _, _, _, i2]
        mips.pipeline.run()

        # after this last run: [_, _, _, _, _]
        self.assertEqual(mips.registers["pc"], 8)
        self.assertTrue(isinstance(mips.pipeline._pipeline[0].instruction, NopInstruction))

    
if __name__ == "__main__":
    unittest.main()
