import unittest

from mips import Mips
from pipeline import Pipeline

class TestPipeline(unittest.TestCase):
    def setUp(self):
        text = """00000000001001110100100000100000 ; I1: add R9,R1,R7
                  00000000000000010001000000011000 ; I2: mul R2,R0,R1
                  00100000000010100000000001100100 ; I3: addi R10,R0,100"""
        mips = Mips(text)
        self.pipeline = mips.pipeline
        
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
        self.assertEqual(self.pipeline._pipeline[3].instruction, None)
        self.pipeline.run()
        self.assertEqual(self.pipeline._pipeline[4].instruction, None)
        self.pipeline.run()


class TestPipelineDependencies(unittest.TestCase):
    def test_register_dependency(self):
        text = """00000000001001110100100000100000 ; I1: add R9,R1,R7
                  00000000000010010001000000100000 ; I2: add R2,R0,R9"""
        mips = Mips(text)
        self.pipeline = mips.pipeline

        # state before pipeline.run()
        # [_, _, _, _, _]
        self.pipeline.run()
        
        i1 = self.pipeline._pipeline[0].instruction
        self.assertEqual(self.pipeline._pipeline[0].instruction, i1)
        
        # [i1, _, _, _, _]
        self.pipeline.run()
        
        i2 = self.pipeline._pipeline[0].instruction
        self.assertEqual(self.pipeline._pipeline[0].instruction, i2)
        self.assertEqual(self.pipeline._pipeline[1].instruction, i1)
        
        # [i2, i1, _, _, _]
        self.pipeline.run()
        self.assertEqual(self.pipeline._pipeline[1].instruction, i2)
        self.assertEqual(self.pipeline._pipeline[2].instruction, i1)

        # [i2, _, i1, _, _]
        self.pipeline.run()
        self.assertEqual(self.pipeline._pipeline[1].instruction, i2)
        self.assertEqual(self.pipeline._pipeline[3].instruction, i1)

        # [i2, _, _, i1, _]
        self.pipeline.run()
        self.assertEqual(self.pipeline._pipeline[1].instruction, i2)
        self.assertEqual(self.pipeline._pipeline[4].instruction, i1)

        # [i2, _, _, _, i1]
        self.pipeline.run()
        self.assertEqual(self.pipeline._pipeline[1].instruction, i2)
        
        # [i2, _, _, _, _]
        self.pipeline.run()
        self.assertEqual(self.pipeline._pipeline[2].instruction, i2)
        
        # [_, i2, _, _, _]
        self.pipeline.run()
        
        # [_, _, i2, _, _]
        self.pipeline.run()
        self.assertEqual(self.pipeline._pipeline[4].instruction, i2)


if __name__ == "__main__":
    unittest.main()
