import unittest

from interpreter import Interpreter

class TestCompile(unittest.TestCase):

    def test_add(self):
        code = "add R9,R1,R7"
        interpreter = Interpreter(code)
        interpreter.compile()
        self.assertEqual(len(interpreter.instructions), 1)
        self.assertEqual(interpreter.instructions[0], "00000000001001110100100000100000 ; I1: add R9,R1,R7")
        
    def test_addi(self):
        code = "addi R6,R5,1"
        interpreter = Interpreter(code)
        interpreter.compile()
        self.assertEqual(len(interpreter.instructions), 1)
        self.assertEqual(interpreter.instructions[0], "00100000101001100000000000000001 ; I1: addi R6,R5,1")

    def test_beq(self):
        code = """nop
                  LOOP:
                  nop
                  beq R1,R2,LOOP"""
        interpreter = Interpreter(code)
        interpreter.compile()
        self.assertEqual(len(interpreter.instructions), 3)
        self.assertEqual(interpreter.instructions[2], "00010100001000101111111111111100 ; I3: beq R1,R2,-4")
        
    def test_ble(self):
        code = """nop
                  LOOP:
                  nop
                  ble R1,R2,LOOP"""
        interpreter = Interpreter(code)
        interpreter.compile()
        self.assertEqual(len(interpreter.instructions), 3)
        self.assertEqual(interpreter.instructions[2], "00011100001000100000000000000100 ; I3: ble R1,R2,4")
        
    def test_bne(self):
        code = """nop
                  LOOP:
                  bne R1,R2,LOOP"""
        interpreter = Interpreter(code)
        interpreter.compile()
        self.assertEqual(len(interpreter.instructions), 2)
        self.assertEqual(interpreter.instructions[1], "00010000001000100000000000000000 ; I2: bne R1,R2,0")
        
    def test_jmp_back(self):
        code = """label:
                  jmp label"""
        interpreter = Interpreter(code)
        interpreter.compile()
        self.assertEqual(len(interpreter.instructions), 1)
        self.assertEqual(interpreter.instructions[0], "00001000000000000000000000000000 ; I1: jmp 0")
        self.assertEqual(interpreter.labels.get("label"), 0)

    def test_jmp_forward(self):
        code = """jmp label
                  label:"""
        interpreter = Interpreter(code)
        interpreter.compile()
        self.assertEqual(len(interpreter.instructions), 1)
        self.assertEqual(interpreter.instructions[0], "00001000000000000000000000000100 ; I1: jmp 4")
        self.assertEqual(interpreter.labels.get("label"), 4)

    def test_lw(self):
        code = "lw R1,24(R0)"
        interpreter = Interpreter(code)
        interpreter.compile()
        self.assertEqual(interpreter.instructions[0], "10001100000000010000000000011000 ; I1: lw R1,24(R0)")
        
    def test_mul(self):
        code = "mul R9,R1,R7"
        interpreter = Interpreter(code)
        interpreter.compile()
        self.assertEqual(len(interpreter.instructions), 1)
        self.assertEqual(interpreter.instructions[0], "00000000001001110100100000011000 ; I1: mul R9,R1,R7")

    def test_nop(self):
        code = "nop"
        interpreter = Interpreter(code)
        interpreter.compile()
        self.assertEqual(interpreter.instructions[0], "00000000000000000000000000000000 ; I1: nop")
        
    def test_sub(self):
        code = "sub R9,R1,R7"
        interpreter = Interpreter(code)
        interpreter.compile()
        self.assertEqual(len(interpreter.instructions), 1)
        self.assertEqual(interpreter.instructions[0], "00000000001001110100100000100010 ; I1: sub R9,R1,R7")
    
    def test_sw(self):
        code = "sw R1,24(R0)"
        interpreter = Interpreter(code)
        interpreter.compile()
        self.assertEqual(interpreter.instructions[0], "10101100000000010000000000011000 ; I1: sw R1,24(R0)")

    def test_label(self):
        """A label is just to mark a point, it is ignored in bytecode generation."""
        code = "label:"
        interpreter = Interpreter(code)
        interpreter.compile()
        self.assertEqual(len(interpreter.instructions), 0)

    def test_ignoring_label_to_string(self):
        """ Bytecode should not have label names."""
        code = """nop
                  label:
                  nop"""
        interpreter = Interpreter(code)
        interpreter.compile()
        self.assertFalse("label" in str(interpreter))

    def test_uppercase_instruction(self):
        code = "ADD R9,R1,R7"
        interpreter = Interpreter(code)
        interpreter.compile()
        self.assertEqual(interpreter.instructions[0], "00000000001001110100100000100000 ; I1: add R9,R1,R7")

    def test_uppercase_instruction(self):
        code = "BLEH R9,R1,R7"
        interpreter = Interpreter(code)
        self.assertRaises(Exception, interpreter.compile)


class TestInterpreter(unittest.TestCase):
    def test_example(self):
        example = """addi R10,R0,100
                     sw R0,24(R0)
                     sw R0,28(R0)
                     LOOP:
                     lw R6,28(R0)
                     mul R7,R6,R6
                     lw R1,24(R0)
                     add R9,R1,R7
                     sw R9,24(R0)
                     addi R6,R6,1
                     sw R6,28(R0)
                     ble R6,R10,LOOP"""

        text = ["00100000000010100000000001100100 ; I1: addi R10,R0,100",
                "10101100000000000000000000011000 ; I2: sw R0,24(R0)",
                "10101100000000000000000000011100 ; I3: sw R0,28(R0)",
                "10001100000001100000000000011100 ; I4: lw R6,28(R0)",
                "00000000110001100011100000011000 ; I5: mul R7,R6,R6",
                "10001100000000010000000000011000 ; I6: lw R1,24(R0)",
                "00000000001001110100100000100000 ; I7: add R9,R1,R7",
                "10101100000010010000000000011000 ; I8: sw R9,24(R0)",
                "00100000110001100000000000000001 ; I9: addi R6,R6,1",
                "10101100000001100000000000011100 ; I10: sw R6,28(R0)",
                "00011100110010100000000000001100 ; I11: ble R6,R10,12"]
        interpreter = Interpreter(example)
        interpreter.compile()

        for compiled, correct in zip(interpreter.instructions, text):
            self.assertEqual(compiled, correct)
        
    def test_if_example(self):
        example = """addi R1,R0,3
                     addi R2,R0,2
                     beq R1,R2,EQ
                     jmp NE
                     EQ:
                     addi R1,R0,5
                     jmp END
                     NE:
                     addi R1,R0,7
                     END:"""

        text = ["00100000000000010000000000000011 ; I1: addi R1,R0,3",
                "00100000000000100000000000000010 ; I2: addi R2,R0,2",
                "00010100001000100000000000001000 ; I3: beq R1,R2,8",
                "00001000000000000000000000011000 ; I4: jmp 24",
                "00100000000000010000000000000101 ; I5: addi R1,R0,5",
                "00001000000000000000000000011100 ; I6: jmp 28",
                "00100000000000010000000000000111 ; I7: addi R1,R0,7"]

        interpreter = Interpreter(example)
        interpreter.compile()

        for compiled, correct in zip(interpreter.instructions, text):
            self.assertEqual(compiled, correct)
        
    
class TestBinaryOperations(unittest.TestCase):
    def setUp(self):
        self.interpreter = Interpreter()

    def test_to_bin(self):
        self.assertEqual(self.interpreter._to_bin(0), '0')
        self.assertEqual(self.interpreter._to_bin(2), '10')
        self.assertEqual(self.interpreter._to_bin(-2, 5), '11110')
        self.assertEqual(self.interpreter._to_bin(-4, 5), '11100')
        self.assertEqual(self.interpreter._to_bin(-7, 5), '11001')
        self.assertEqual(self.interpreter._to_bin(-8, 5), '11000')
        self.assertEqual(self.interpreter._to_bin(12, 5), '01100')        
    

