import unittest

from interpreter import Interpreter

class TestCompile(unittest.TestCase):
    def test_nop(self):
        code = "nop"
        interpreter = Interpreter(code)
        interpreter.compile()
        self.assertEqual(interpreter.bytecode_instructions[0], "00000000000000000000000000000000")
        
    def test_label(self):
        code = "label:"
        interpreter = Interpreter(code)
        interpreter.compile()
        self.assertEqual(len(interpreter.bytecode_instructions), 0)
        
    def test_jmp_back(self):
        code = """label:
                  jmp label"""
        interpreter = Interpreter(code)
        interpreter.compile()
        self.assertEqual(len(interpreter.bytecode_instructions), 1)
        self.assertEqual(interpreter.bytecode_instructions[0], "00001000000000000000000000000000")
        self.assertEqual(interpreter.labels.get("label"), 0)

    def test_jmp_forward(self):
        code = """jmp label
                  label:"""
        interpreter = Interpreter(code)
        interpreter.compile()
        self.assertEqual(len(interpreter.bytecode_instructions), 1)
        self.assertEqual(interpreter.bytecode_instructions[0], "00001000000000000000000000000000")
        self.assertEqual(interpreter.labels.get("label"), 4)


    
if __name__ == "__main__":
    unittest.main()
    
