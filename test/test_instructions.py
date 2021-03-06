import unittest

import instructions
from instructions import Instruction
from registers import Registers, RegisterInUseException


class MipsStub(object):
    def __init__(self, registers=None, memory=None, data_forwarding=False):
        self.registers = registers
        self.memory = memory
        self.pc = 0
        self.data_forwarding = data_forwarding

    def jump(self, pc):
        self.pc = pc
        

class TestBasicInstances(unittest.TestCase):
    def test_line(self):
        text = "00000000001001110100100000100000 ; I7: add R9,R1,R7"
        instruction = Instruction(text)
        self.assertEqual(instruction.bytecode, "00000000001001110100100000100000")
        self.assertEqual(instruction.text, "I7: add R9,R1,R7")
        
    def test_line_with_empty_text(self):
        text = "00000000001001110100100000100000;"
        instruction = Instruction(text)
        self.assertEqual(instruction.bytecode, "00000000001001110100100000100000")
        self.assertEqual(instruction.text, "")

    def test_line_without_semicolon(self):
        text = "00000000001001110100100000100000"
        instruction = Instruction(text)
        self.assertEqual(instruction.bytecode, "00000000001001110100100000100000")
        self.assertEqual(instruction.text, "")
        

class TestInstructionR(unittest.TestCase):
    def setUp(self):
        self.text = "00000000001001110100100000100000 ; I7: add R9,R1,R7"
        self.instruction = Instruction(self.text)
    
    def test_creation(self):
        self.assertEqual(type(self.instruction), instructions.AddInstruction)

    def test_parameters_existence(self):
        self.assertTrue(hasattr(self.instruction, 'opcode'))
        self.assertTrue(hasattr(self.instruction, 'rs'))
        self.assertTrue(hasattr(self.instruction, 'rt'))
        self.assertTrue(hasattr(self.instruction, 'rd'))
        self.assertTrue(hasattr(self.instruction, 'shamt'))
        self.assertTrue(hasattr(self.instruction, 'funct'))

    def test_parameters_value(self):
        self.assertEqual(self.instruction.opcode, "000000")
        self.assertEqual(self.instruction.rs, 1)
        self.assertEqual(self.instruction.rt, 7)
        self.assertEqual(self.instruction.rd, 9)
        self.assertEqual(self.instruction.shamt, "00000")
        self.assertEqual(self.instruction.funct, "100000")


class TestInstructionI(unittest.TestCase):
    def setUp(self):
        self.text = "00100000000010100000000001100100 ; I1: addi R10,R0,100"
        self.instruction = Instruction(self.text)
    
    def test_creation(self):
        self.assertEqual(type(self.instruction), instructions.AddiInstruction)

    def test_parameters_existence(self):
        self.assertTrue(hasattr(self.instruction, 'opcode'))
        self.assertTrue(hasattr(self.instruction, 'rs'))
        self.assertTrue(hasattr(self.instruction, 'rt'))
        self.assertTrue(hasattr(self.instruction, 'immediate'))

    def test_parameters_value(self):
        self.assertEqual(self.instruction.opcode, "001000")
        self.assertEqual(self.instruction.rs, 0)
        self.assertEqual(self.instruction.rt, 10)
        self.assertEqual(self.instruction.immediate, 100)


class TestInstructionJ(unittest.TestCase):
    def setUp(self):
        self.text = "00001000000000000000000000101010 ; I3: jmp 42"
        self.instruction = Instruction(self.text)
    
    def test_creation(self):
        self.assertEqual(type(self.instruction), instructions.JmpInstruction)

    def test_parameters_existence(self):
        self.assertTrue(hasattr(self.instruction, 'opcode'))
        self.assertTrue(hasattr(self.instruction, 'target_address'))

    def test_parameters_value(self):
        self.assertEqual(self.instruction.opcode, "000010")
        self.assertEqual(self.instruction.target_address, 42)


class TestInstructionInvalid(unittest.TestCase):
    def test_invalid_opcode(self):
        text = "11111100000000000000000000101010"
        self.assertRaises(KeyError, Instruction, text)

    def test_invalid_funct(self):
        text = "00000000000000000000000000101010"
        self.assertRaises(KeyError, Instruction, text)


class BaseTestInstruction(object):
    def instruction_decode(self):
        self.instruction.instruction_decode(self._mips)
    
    def execute(self):
        self.instruction_decode()
        while not self.instruction.execute(self._mips):
            pass
        return True

    def memory_access(self):
        self.execute()
        self.instruction.memory_access(self._mips)

    def write_back(self):
        self.memory_access()
        self.instruction.write_back(self._mips)
        
    def test_all_true_returns(self):
        self.assertTrue(self.instruction.instruction_decode(self._mips))
        self.assertTrue(self.instruction.execute(self._mips))
        self.assertTrue(self.instruction.memory_access(self._mips))
        self.assertTrue(self.instruction.write_back(self._mips))
        

class TestAddInstruction(BaseTestInstruction, unittest.TestCase):
    def setUp(self):
        self.text = "00000000001001110100100000100000 ; I7: add R9,R1,R7"
        self.instruction = Instruction(self.text)

        registers = Registers()
        registers[1] = 3
        registers[7] = 2
        registers[9] = 4
        self._mips = MipsStub(registers, memory=[])
        
    def test_instruction_fetch(self):
        self.assertTrue(isinstance(self.instruction, instructions.AddInstruction))

    def test_instruction_decode(self):
        BaseTestInstruction.instruction_decode(self)
        
    def test_execute(self):
        self.assertTrue(BaseTestInstruction.execute(self))
        self.assertEqual(self.instruction.rd_value, 5)
        # don't change registers
        self.assertEqual(self._mips.registers[1], 3)
        self.assertEqual(self._mips.registers[7], 2)
        
    def test_execute_with_data_forward(self):
        self._mips.data_forwarding = True
        self.assertTrue(BaseTestInstruction.execute(self))
        self.assertEqual(self._mips.registers[9], 5)
        
    def test_memory_access(self):
        BaseTestInstruction.memory_access(self)
                
    def test_write_back(self):
        BaseTestInstruction.write_back(self)
        self.assertEqual(self._mips.registers[1], 3)
        self.assertEqual(self._mips.registers[7], 2)
        # register changed
        self.assertEqual(self._mips.registers[9], 5)
        
    def test_register_lock(self):
        BaseTestInstruction.instruction_decode(self)
        self.assertRaises(RegisterInUseException, self._mips.registers.__getitem__, 9)
        
    def test_register_unlock(self):
        BaseTestInstruction.write_back(self)
        self._mips.registers[9]
        
    
class TestAddiInstruction(BaseTestInstruction, unittest.TestCase):
    def setUp(self):
        self.text = "00100000110001100000000000000001 ; I9: addi R6,R6,1"
        self.instruction = Instruction(self.text)

        registers = Registers()
        registers[6] = 4
        memory = []
        self._mips = MipsStub(registers, memory=[])
            
    def test_instruction_decode(self):
        BaseTestInstruction.instruction_decode(self)
        self.assertEqual(self.instruction.rs_value, 4)
        
    def test_execute(self):
        self.assertTrue(BaseTestInstruction.execute(self))
        self.assertEqual(self.instruction.rt_value, 5)
        
    def test_execute_with_data_forward(self):
        self._mips.data_forwarding = True
        self.assertTrue(BaseTestInstruction.execute(self))
        self.assertEqual(self._mips.registers[6], 5)
        
    def test_memory_access(self):
        BaseTestInstruction.memory_access(self)
                
    def test_write_back(self):
        BaseTestInstruction.write_back(self)
        # register changed
        self.assertEqual(self._mips.registers[6], 5)
        
    def test_register_lock(self):
        BaseTestInstruction.instruction_decode(self)
        self.assertRaises(RegisterInUseException, self._mips.registers.__getitem__, 6)
        
    def test_register_unlock(self):
        BaseTestInstruction.write_back(self)
        self._mips.registers[6]
    

class TestBeqInstruction(BaseTestInstruction, unittest.TestCase):
    def setUp(self):
        self.text = "00010100001000110000000000001010 ; I20: beq R1,R2,10"
        self.instruction = Instruction(self.text)

        registers = Registers()
        registers[1] = 4
        registers[3] = 4
        self._mips = MipsStub(registers, memory=[])
        self.instruction.pc = self._mips.pc
        
    def test_instruction_decode(self):
        BaseTestInstruction.instruction_decode(self)
        self.assertEqual(self.instruction.rs_value, 4)
        self.assertEqual(self.instruction.rt_value, 4)
        self.assertEqual(self.instruction.immediate, 10)
        self.assertEqual(self.instruction.pc, 0)
        
    def test_execute_with_jump(self):
        self.assertTrue(BaseTestInstruction.execute(self))
        self.assertEqual(self.instruction.pc, 10)
        self.assertEqual(self._mips.pc, 10)
        
    def test_execute_without_jump(self):
        self._mips.registers[3] = 2
        BaseTestInstruction.execute(self)
        self.assertEqual(self.instruction.pc, 0)
        self.assertEqual(self._mips.pc, 0)

    def test_memory_access(self):
        BaseTestInstruction.memory_access(self)
                
    def test_write_back(self):
        BaseTestInstruction.write_back(self)
        
    
class TestBleInstruction(BaseTestInstruction, unittest.TestCase):
    def setUp(self):
        self.text = "00011100110010100000000000010100 ; I11: ble R6,R10,20"
        self.instruction = Instruction(self.text)

        registers = Registers()
        registers[6] = 3
        registers[10] = 8
        self._mips = MipsStub(registers, memory=[])
        self.instruction.pc = self._mips.pc
        
    def test_instruction_decode(self):
        BaseTestInstruction.instruction_decode(self)
        self.assertEqual(self.instruction.rs_value, 3)
        self.assertEqual(self.instruction.rt_value, 8)
        self.assertEqual(self.instruction.immediate, 20)
        self.assertEqual(self.instruction.pc, 0)
        
    def test_execute_with_jump(self):
        self.assertTrue(BaseTestInstruction.execute(self))
        self.assertEqual(self.instruction.pc, 20)
        self.assertEqual(self._mips.pc, 20)
        
    def test_execute_without_jump(self):
        self._mips.registers[10] = 2
        BaseTestInstruction.execute(self)
        self.assertEqual(self.instruction.pc, 0)
        self.assertEqual(self._mips.pc, 0)
        
    def test_memory_access(self):
        BaseTestInstruction.memory_access(self)
                
    def test_write_back(self):
        BaseTestInstruction.write_back(self)


    
class TestBneInstruction(BaseTestInstruction, unittest.TestCase):
    def setUp(self):
        self.text = """00010000001000101111111111111000 ; I2: bne R1,R2,-8"""
        self.instruction = Instruction(self.text)

        registers = Registers()
        registers[1] = 3
        registers[2] = 8
        self._mips = MipsStub(registers, memory=[])
        self._mips.pc = 4
        self.instruction.pc = self._mips.pc
        
    def test_instruction_decode(self):
        BaseTestInstruction.instruction_decode(self)
        self.assertEqual(self.instruction.rs_value, 3)
        self.assertEqual(self.instruction.rt_value, 8)
        self.assertEqual(self.instruction.immediate, -8)
        self.assertEqual(self.instruction.pc, 4)
        
    def test_execute_with_jump(self):
        self.assertTrue(BaseTestInstruction.execute(self))
        self.assertEqual(self.instruction.pc, 0)
        self.assertEqual(self._mips.pc, 0)
        
    def test_execute_without_jump(self):
        self._mips.registers[2] = 3
        self.assertTrue(BaseTestInstruction.execute(self))
        self.assertEqual(self.instruction.pc, 4)
        self.assertEqual(self._mips.pc, 4)

    def test_memory_access(self):
        BaseTestInstruction.memory_access(self)
                
    def test_write_back(self):
        BaseTestInstruction.write_back(self)
        
    
class TestJmpInstruction(BaseTestInstruction, unittest.TestCase):
    def setUp(self):
        self.text = "00001000000000000000000011001000 ; I15: jmp 200"
        self.instruction = Instruction(self.text)

        registers = Registers()
        self._mips = MipsStub(registers, memory=[])
    
    def test_instruction_decode(self):
        BaseTestInstruction.instruction_decode(self)
        self.assertEqual(self.instruction.pc, 200)
        self.assertEqual(self._mips.pc, 0)
        
    def test_execute(self):
        self.assertTrue(BaseTestInstruction.execute(self))
        self.assertEqual(self._mips.pc, 200)
        
    def test_memory_access(self):
        BaseTestInstruction.memory_access(self)
                
    def test_write_back(self):
        BaseTestInstruction.write_back(self)
        
        
class TestLwInstruction(BaseTestInstruction, unittest.TestCase):
    def setUp(self):
        self.text = "10001100000000010000000000011000 ; I15: lw R1,24(R0)"
        self.instruction = Instruction(self.text)
        
        registers = Registers()
        registers[0] = 12
        registers[1] = 4
        memory = [0] * 64
        memory[36] = 6
        self._mips = MipsStub(registers, memory)


    def test_instruction_decode(self):
        BaseTestInstruction.instruction_decode(self)
        self.assertEqual(self.instruction.rs_value, 12)
        self.assertEqual(self.instruction.immediate, 24)
        
    def test_execute(self):
        self.assertTrue(BaseTestInstruction.execute(self))
        self.assertEqual(self.instruction.target_address, 36)
        
    def test_memory_access(self):
        BaseTestInstruction.memory_access(self)
        self.assertEqual(self.instruction.rt_value, 6)
                
    def test_write_back(self):
        BaseTestInstruction.write_back(self)
        self.assertEqual(self._mips.registers[1], 6)
        
    def test_register_lock(self):
        BaseTestInstruction.instruction_decode(self)
        self.assertRaises(RegisterInUseException, self._mips.registers.__getitem__, 1)
        
    def test_register_unlock(self):
        BaseTestInstruction.write_back(self)
        self._mips.registers[1]
        
    
class TestMulInstruction(BaseTestInstruction, unittest.TestCase):
    def setUp(self):
        self.text = "00000000001001110100100000011000 ; I4: mul R9,R1,R7"
        self.instruction = Instruction(self.text)
        
        registers = Registers()
        registers[1] = 3
        registers[7] = 2
        registers[9] = 4
        self._mips = MipsStub(registers, memory=[])
        
    def test_instruction_decode(self):
        BaseTestInstruction.instruction_decode(self)
        self.assertEqual(self.instruction.rs_value, 3)
        self.assertEqual(self.instruction.rt_value, 2)
        
    def test_execute(self):
        BaseTestInstruction.execute(self)
        self.assertEqual(self.instruction.rd_value, 6)
        self.assertEqual(self._mips.registers[1], 3)
        self.assertEqual(self._mips.registers[7], 2)
        
    def test_execute_with_data_forward(self):
        self._mips.data_forwarding = True
        BaseTestInstruction.execute(self)
        self.assertEqual(self._mips.registers[9], 6)
        
    def test_memory_access(self):
        BaseTestInstruction.memory_access(self)
                
    def test_write_back(self):
        BaseTestInstruction.write_back(self)
        self.assertEqual(self._mips.registers[1], 3)
        self.assertEqual(self._mips.registers[7], 2)
        self.assertEqual(self._mips.registers[9], 6)
        
    def test_all_true_returns(self):
        self.assertTrue(self.instruction.instruction_decode(self._mips))
        self.assertFalse(self.instruction.execute(self._mips))
        self.assertTrue(self.instruction.execute(self._mips))
        self.assertTrue(self.instruction.memory_access(self._mips))
        self.assertTrue(self.instruction.write_back(self._mips))

    def test_register_lock(self):
        BaseTestInstruction.instruction_decode(self)
        self.assertRaises(RegisterInUseException, self._mips.registers.__getitem__, 9)
        
    def test_register_unlock(self):
        BaseTestInstruction.write_back(self)
        self._mips.registers[9]
        
        
class TestNopInstruction(BaseTestInstruction, unittest.TestCase):
    def setUp(self):
        self.text = "00000000000000000000000000000000 ; I4: nop"
        self.instruction = Instruction(self.text)

        registers = Registers()
        self._mips = MipsStub(registers, memory=[])
    
    def test_instruction_decode(self):
        BaseTestInstruction.instruction_decode(self)
        
    def test_execute(self):
        self.assertTrue(BaseTestInstruction.execute(self))
        
    def test_memory_access(self):
        BaseTestInstruction.memory_access(self)
                
    def test_write_back(self):
        BaseTestInstruction.write_back(self)
        
        
class TestStallInstruction(BaseTestInstruction, unittest.TestCase):
    def setUp(self):
        from instructions import StallInstruction
        self.instruction = StallInstruction()
        
        registers = Registers()
        self._mips = MipsStub(registers, memory=[])
    
    def test_instruction_decode(self):
        BaseTestInstruction.instruction_decode(self)
        
    def test_execute(self):
        self.assertTrue(BaseTestInstruction.execute(self))
        
    def test_memory_access(self):
        BaseTestInstruction.memory_access(self)
                
    def test_write_back(self):
        BaseTestInstruction.write_back(self)
        
    
class TestSubInstruction(BaseTestInstruction, unittest.TestCase):
    def setUp(self):
        self.text = "00000000001001110100100000100010 ; I7: add R9,R1,R7"
        self.instruction = Instruction(self.text)
        
        registers = Registers()
        registers[1] = 3
        registers[7] = 2
        registers[9] = 4
        self._mips = MipsStub(registers, memory=[])
    
    def test_instruction_decode(self):
        BaseTestInstruction.instruction_decode(self)
        self.assertEqual(self.instruction.rs_value, 3)
        self.assertEqual(self.instruction.rt_value, 2)
        
    def test_execute(self):
        self.assertTrue(BaseTestInstruction.execute(self))
        self.assertEqual(self.instruction.rd_value, 1)
        # don't change registers
        self.assertEqual(self._mips.registers[1], 3)
        self.assertEqual(self._mips.registers[7], 2)
        
    def test_memory_access(self):
        BaseTestInstruction.memory_access(self)
        
    def test_write_back(self):
        BaseTestInstruction.write_back(self)
        self.assertEqual(self._mips.registers[1], 3)
        self.assertEqual(self._mips.registers[7], 2)
        # register changed
        self.assertEqual(self._mips.registers[9], 1)
        
    def test_register_lock(self):
        BaseTestInstruction.instruction_decode(self)
        self.assertRaises(RegisterInUseException, self._mips.registers.__getitem__, 9)
        
    def test_register_unlock(self):
        BaseTestInstruction.write_back(self)
        self._mips.registers[9]
        
    
class TestSwInstruction(BaseTestInstruction, unittest.TestCase):
    def setUp(self):
        self.text = "10101100000010010000000000011000 ; I15: sw R9,24(R0)"
        self.instruction = Instruction(self.text)
        
        registers = Registers()
        registers[0] = 12
        registers[9] = 4
        memory = [0] * 64
        memory[36] = 6
        self._mips = MipsStub(registers, memory)

    def test_instruction_decode(self):
        BaseTestInstruction.instruction_decode(self)
        self.assertEqual(self.instruction.rs_value, 12)
        self.assertEqual(self.instruction.rt_value, 4)
        self.assertEqual(self.instruction.immediate, 24)
        
    def test_execute(self):
        self.assertTrue(BaseTestInstruction.execute(self))
        self.assertEqual(self.instruction.memory_address, 36)
        
    def test_memory_access(self):
        BaseTestInstruction.memory_access(self)
        self.assertEqual(self._mips.memory[self.instruction.memory_address], 4)
                
    def test_write_back(self):
        BaseTestInstruction.write_back(self)
        
    
