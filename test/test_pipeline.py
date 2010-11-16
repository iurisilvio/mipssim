import unittest

from mips import Mips
from pipeline import Pipeline

class TestPipeline(unittest.TestCase):
    def setUp(self):
        text = """00000000001001110100100000100000 ; I1: add R9,R1,R7
                  00000000000000010001000000011000 ; I2: mul R2,R0,R1
                  00100000000010100000000001100100 ; I3: addi R10,R0,100"""
    
        mips = Mips(text)
        self.pipeline = Pipeline(mips)
        
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
        self.print_(self.pipeline._pipeline)
        self.pipeline.run()
        self.print_(self.pipeline._pipeline)

    def print_(self, arr):
        print [item.instruction.text if item.instruction else None for item in arr]
    
if __name__ == "__main__":
    unittest.main()
