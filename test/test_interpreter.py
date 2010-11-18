import unittest

from interpreter import Interpreter

class TestCompile(unittest.TestCase):

    def test_add(self):
        code = "add R9,R1,R7"
        interpreter = Interpreter(code)
        interpreter.compile()
        self.assertEqual(len(interpreter.bytecode_instructions), 1)
        self.assertEqual(interpreter.bytecode_instructions[0], "00000000001001110100100000100000")
        
    def test_addi(self):
        code = "addi R6,R5,1"
        interpreter = Interpreter(code)
        interpreter.compile()
        self.assertEqual(len(interpreter.bytecode_instructions), 1)
        self.assertEqual(interpreter.bytecode_instructions[0], "00100000101001100000000000000001")

    def test_beq(self):
        code = """nop
                  LOOP:
                  nop
                  beq R1,R2,LOOP"""
        interpreter = Interpreter(code)
        interpreter.compile()
        self.assertEqual(len(interpreter.bytecode_instructions), 3)
        self.assertEqual(interpreter.bytecode_instructions[2], "00010100001000100000000000000100")
        
    def test_ble(self):
        code = """nop
                  LOOP:
                  nop
                  ble R1,R2,LOOP"""
        interpreter = Interpreter(code)
        interpreter.compile()
        self.assertEqual(len(interpreter.bytecode_instructions), 3)
        self.assertEqual(interpreter.bytecode_instructions[2], "00011100001000100000000000000100")
        
    def test_bne(self):
        code = """nop
                  LOOP:
                  bne R1,R2,LOOP"""
        interpreter = Interpreter(code)
        interpreter.compile()
        self.assertEqual(len(interpreter.bytecode_instructions), 2)
        self.assertEqual(interpreter.bytecode_instructions[1], "00010000001000100000000000000100")
        
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
        self.assertEqual(interpreter.bytecode_instructions[0], "00001000000000000000000000000100")
        self.assertEqual(interpreter.labels.get("label"), 4)

    def test_lw(self):
        code = "lw R1,24(R0)"
        interpreter = Interpreter(code)
        interpreter.compile()
        self.assertEqual(interpreter.bytecode_instructions[0], "10001100000000010000000000011000")
        
    def test_mul(self):
        code = "mul R9,R1,R7"
        interpreter = Interpreter(code)
        interpreter.compile()
        self.assertEqual(len(interpreter.bytecode_instructions), 1)
        self.assertEqual(interpreter.bytecode_instructions[0], "00000000001001110100100000011000")

    def test_nop(self):
        code = "nop"
        interpreter = Interpreter(code)
        interpreter.compile()
        self.assertEqual(interpreter.bytecode_instructions[0], "00000000000000000000000000000000")
        
    def test_sub(self):
        code = "sub R9,R1,R7"
        interpreter = Interpreter(code)
        interpreter.compile()
        self.assertEqual(len(interpreter.bytecode_instructions), 1)
        self.assertEqual(interpreter.bytecode_instructions[0], "00000000001001110100100000100010")
    
    def test_sw(self):
        code = "sw R1,24(R0)"
        interpreter = Interpreter(code)
        interpreter.compile()
        self.assertEqual(interpreter.bytecode_instructions[0], "10101100000000010000000000011000")

    def test_label(self):
        """A label is just to mark a point, it is ignored in bytecode generation."""
        code = "label:"
        interpreter = Interpreter(code)
        interpreter.compile()
        self.assertEqual(len(interpreter.bytecode_instructions), 0)


class TestInterpreter(unittest.TestCase):
    def test_example(self):
        example = """addi R10,R0,100
                     sw R0,24(R0)
                     sw R0,28(R0)
                     lw R6,28(R0)
                     mul R7,R6,R6
                     LOOP:
                     lw R1,24(R0)
                     add R9,R1,R7
                     sw R9,24(R0)
                     addi R6,R6,1
                     sw R6,28(R0)
                     ble R6,R10,LOOP"""

        bytecode = ["00100000000010100000000001100100",
                    "10101100000000000000000000011000",
                    "10101100000000000000000000011100",
                    "10001100000001100000000000011100",
                    "00000000110001100011100000011000",
                    "10001100000000010000000000011000",
                    "00000000001001110100100000100000",
                    "10101100000010010000000000011000",
                    "00100000110001100000000000000001",
                    "10101100000001100000000000011100",
                    "00011100110010100000000000010100"]
        interpreter = Interpreter(example)
        interpreter.compile()

        for compiled, correct in zip(interpreter.bytecode_instructions, bytecode):
            self.assertEqual(compiled, correct)
        


    
if __name__ == "__main__":
    unittest.main()
    
