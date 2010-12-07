import logging
from copy import copy

from registers import RegisterInUseException

ALU_SRC = "ALU_SRC"
REG_DST = "REG_DST"
MEM_TO_REG = "MEM_TO_REG"
REG_WRITE = "REG_WRITE"
MEM_WRITE = "MEM_WRITE"
BRANCH = "BRANCH"
JUMP = "JUMP"
EXT_OP = "EXT_OP"

class Instruction(object):
    """Factory"""
    
    class R(object):
        def __new__(cls, bytecode, text):
            try:
                funct = bytecode[26:32]
                instruction = map_r_instruction_funct[funct]()
            except KeyError:
                logging.info("Invalid funct to R instruction: '%s ; %s'.", 
                              bytecode, text)
                raise
                
            instruction.bytecode = bytecode
            instruction.opcode = bytecode[0:6]
            instruction.rs = int(bytecode[6:11], 2)
            instruction.rt = int(bytecode[11:16], 2)
            instruction.rd = int(bytecode[16:21], 2)
            instruction.shamt = bytecode[21:26]
            instruction.funct = bytecode[26:32]
            instruction.text = text
            return instruction
            
        
    class I(object):
        def __new__(cls, bytecode, text):
            try:
                opcode = bytecode[0:6]
                instruction = map_i_instruction[opcode]()
            except KeyError:
                logging.info("Invalid opcode to I instruction: '%s ; %s'.", 
                              bytecode, text)
                raise

            instruction.bytecode = bytecode
            instruction.opcode = bytecode[0:6]
            instruction.rs = int(bytecode[6:11], 2)
            instruction.rt = int(bytecode[11:16], 2)
            instruction.immediate = int(bytecode[16:32], 2)
            
            if bytecode[16] == '1': # immediate is a two complement number
                instruction.immediate -= (1 << 16)
                
            instruction.text = text
            return instruction
            
        
    class J(object):
        def __new__(cls, bytecode, text):
            try:
                opcode = bytecode[0:6]
                instruction = map_j_instruction[opcode]()
            except KeyError:
                logging.info("Invalid opcode to J instruction: '%s ; %s'.", 
                              bytecode, text)
                raise
                
            instruction.bytecode = bytecode
            instruction.opcode = bytecode[0:6]
            instruction.target_address = int(bytecode[6:32], 2)
            instruction.text = text
            return instruction
            
        
    def __new__(cls, line):
        try:
            bytecode, text = line.split(";")
        except ValueError:
            bytecode = line
            text = ""
            
        bytecode = bytecode.strip()
        text = text.strip()
        
        opcode = bytecode[0:6]
        try:
            instruction_type = map_opcode_type[opcode]
            return instruction_type(bytecode, text)
            
        except KeyError:
            logging.info("Invalid opcode to instruction: '%s'.", line)
            raise


class BaseInstruction(object):
    def __init__(self, **kwargs):
        self.flags = {REG_DST:kwargs.get(REG_DST, 0),
                      ALU_SRC:kwargs.get(ALU_SRC, 0),
                      MEM_TO_REG:kwargs.get(MEM_TO_REG, 0),
                      REG_WRITE:kwargs.get(REG_WRITE, 0),
                      MEM_WRITE:kwargs.get(MEM_WRITE, 0),
                      BRANCH:kwargs.get(BRANCH, 0),
                      JUMP:kwargs.get(JUMP, 0),
                      EXT_OP:kwargs.get(EXT_OP, 0)}
                      
        self.execution_time = kwargs.get("execution_time", 1)
        self._to_lock = kwargs.get("to_lock", [])
        
    def instruction_decode(self, mips=None):
        self.lock_registers(mips)
        return True
        
    def execute(self, mips=None):
        self.execution_time -= 1
        return self.execution_time == 0
        
    def memory_access(self, mips=None):
        return True
        
    def write_back(self, mips=None):
        self.unlock_registers(mips)
        return True
        
    def lock_registers(self, mips):
        for register in self._to_lock:
            mips.registers.lock(register)

    def unlock_registers(self, mips):
        for register in self._to_lock:
            mips.registers.unlock(register)
                
    def current_state(self):
        state = {"text":self.text,
                 "flags":copy(self.flags)}
        return state
        
    
class AddInstruction(BaseInstruction):
    def __init__(self):
        BaseInstruction.__init__(self,
            REG_DST=1, REG_WRITE=1, EXT_OP=None)
        
    def instruction_decode(self, mips):
        try:
            self.rs_value = mips.registers[self.rs]
            self.rt_value = mips.registers[self.rt]
            self._to_lock.append(self.rd)
            BaseInstruction.instruction_decode(self, mips)
            return True
        except RegisterInUseException:
            return False
        
    def execute(self, mips):
        BaseInstruction.execute(self)
        self.rd_value = self.rs_value + self.rt_value
        if mips.data_forwarding:
            mips.registers[self.rd] = self.rd_value
        return self.execution_time == 0
        
    def write_back(self, mips):
        BaseInstruction.write_back(self, mips)
        mips.registers[self.rd] = self.rd_value
        return True


class AddiInstruction(BaseInstruction):
    def __init__(self):
        BaseInstruction.__init__(self,
            REG_DST=1, REG_WRITE=1, EXT_OP=0, ALU_SRC=1)
            
    def instruction_decode(self, mips):
        try:
            self.rs_value = mips.registers[self.rs]
            self._to_lock.append(self.rt)
            BaseInstruction.instruction_decode(self, mips)
            return True
        except RegisterInUseException:
            return False

    def execute(self, mips):
        BaseInstruction.execute(self)
        self.rt_value = self.rs_value + self.immediate
        if mips.data_forwarding:
            mips.registers[self.rt] = self.rt_value
        return self.execution_time == 0
        
    def write_back(self, mips):
        BaseInstruction.write_back(self, mips)
        mips.registers[self.rt] = self.rt_value
        return True
        
        
class BeqInstruction(BaseInstruction):
    def __init__(self):
        BaseInstruction.__init__(self,
            REG_DST=None, MEM_TO_REG=None, BRANCH=1, EXT_OP=None)
            
    def instruction_decode(self, mips):
        try:
            self.rs_value = mips.registers[self.rs]
            self.rt_value = mips.registers[self.rt]
            return True
        except RegisterInUseException:
            return False
        
    def execute(self, mips):
        BaseInstruction.execute(self)
        if self.rs_value == self.rt_value:
            self.pc = self.pc + self.immediate
            mips.jump(self.pc)
        return self.execution_time == 0
        
        
class BleInstruction(BaseInstruction):
    def __init__(self):
        BaseInstruction.__init__(self,
            REG_DST=None, ALU_SRC=1, MEM_TO_REG=None, BRANCH=1, EXT_OP=None)
                
    def instruction_decode(self, mips):
        try:
            self.rs_value = mips.registers[self.rs]
            self.rt_value = mips.registers[self.rt]
            return True
        except RegisterInUseException:
            return False
        
    def execute(self, mips):
        BaseInstruction.execute(self)
        if self.rs_value <= self.rt_value:
            self.pc = self.immediate
            mips.jump(self.pc)
        return self.execution_time == 0
        

class BneInstruction(BaseInstruction):
    def __init__(self):
        BaseInstruction.__init__(self,
            REG_DST=None, MEM_TO_REG=None, BRANCH=1, EXT_OP=None)
                
    def instruction_decode(self, mips):
        try:
            self.rs_value = mips.registers[self.rs]
            self.rt_value = mips.registers[self.rt]
            return True
        except RegisterInUseException:
            return False
        
    def execute(self, mips):
        BaseInstruction.execute(self)
        if self.rs_value != self.rt_value:
            self.pc = self.pc + self.immediate + 4
            mips.jump(self.pc)
        return self.execution_time == 0
        
    
class JmpInstruction(BaseInstruction):
    def __init__(self):
        BaseInstruction.__init__(self,
            REG_DST=None, ALU_SRC=None, MEM_TO_REG=None, JUMP=1, EXT_OP=None)
                 
    def instruction_decode(self, mips):
        self.pc = self.target_address
        return True
        
    def execute(self, mips):
        BaseInstruction.execute(self)
        mips.jump(self.pc)
        return True
        
    
class LwInstruction(BaseInstruction):
    def __init__(self):
        BaseInstruction.__init__(self,
            ALU_SRC=1, MEM_TO_REG=1, REG_WRITE=1, EXT_OP=1)
                                           
    def instruction_decode(self, mips):
        try:
            self.rs_value = mips.registers[self.rs]
            self._to_lock.append(self.rt)
            BaseInstruction.instruction_decode(self, mips)
            return True
        except RegisterInUseException:
            return False
                 
    def execute(self, mips):
        BaseInstruction.execute(self)
        self.target_address = self.rs_value + self.immediate
        return self.execution_time == 0
        
    def memory_access(self, mips):
        self.rt_value = mips.memory[self.target_address]
        return True
                
    def write_back(self, mips):
        BaseInstruction.write_back(self, mips)
        mips.registers[self.rt] = self.rt_value
        return True
        

class MulInstruction(BaseInstruction):
    def __init__(self):
        BaseInstruction.__init__(self, execution_time=2,
            REG_DST=1, REG_WRITE=1, EXT_OP=None)
                                  
    def instruction_decode(self, mips):
        try:
            self.rs_value = mips.registers[self.rs]
            self.rt_value = mips.registers[self.rt]
            self._to_lock.append(self.rd)
            BaseInstruction.instruction_decode(self, mips)
            return True
        except RegisterInUseException:
            return False
        
    def execute(self, mips):
        if BaseInstruction.execute(self):
            self.rd_value = self.rs_value * self.rt_value
            if mips.data_forwarding:
                mips.registers[self.rd] = self.rd_value
            return True
        return False
        
    def write_back(self, mips):
        mips.registers.unlock(self.rd)
        mips.registers[self.rd] = self.rd_value
        return True
        

class NopInstruction(BaseInstruction):
    def __init__(self):
        BaseInstruction.__init__(self)
        
    
class StallInstruction(NopInstruction):
    def __init__(self):
        NopInstruction.__init__(self)
        self.text = "stall"
        
    
class SubInstruction(BaseInstruction):
    def __init__(self):
        BaseInstruction.__init__(self,
            REG_WRITE=1, EXT_OP=None)
        
    def instruction_decode(self, mips):
        try:
            self.rs_value = mips.registers[self.rs]
            self.rt_value = mips.registers[self.rt]
            self._to_lock.append(self.rd)
            BaseInstruction.instruction_decode(self, mips)
            return True
        except RegisterInUseException:
            return False
        
    def execute(self, mips):
        BaseInstruction.execute(self)
        self.rd_value = self.rs_value - self.rt_value
        if mips.data_forwarding:
            mips.registers[self.rd] = self.rd_value
        return self.execution_time == 0

    def write_back(self, mips):
        BaseInstruction.write_back(self, mips)
        mips.registers[self.rd] = self.rd_value
        return True
        

class SwInstruction(BaseInstruction):
    def __init__(self):
        BaseInstruction.__init__(self,
            REG_DST=None, ALU_SRC=1, MEM_TO_REG=None, MEM_WRITE=1, EXT_OP=1)
                                           
    def instruction_decode(self, mips):
        try:
            self.rs_value = mips.registers[self.rs]
            self.rt_value = mips.registers[self.rt]
            return True
        except RegisterInUseException:
            return False

    def execute(self, mips):
        BaseInstruction.execute(self)
        self.memory_address = self.rs_value + self.immediate
        return self.execution_time == 0
        
    def memory_access(self, mips):
        mips.memory[self.memory_address] = self.rt_value
        return True
        
        
map_opcode_type = {"000000":Instruction.R,
                   "000010":Instruction.J,
                   "000100":Instruction.I,
                   "000101":Instruction.I,
                   "000111":Instruction.I,
                   "001000":Instruction.I,
                   "100011":Instruction.I,
                   "101011":Instruction.I}

map_r_instruction_funct = {"100000":AddInstruction,
                           "011000":MulInstruction,
                           "000000":NopInstruction,
                           "100010":SubInstruction}

map_i_instruction = {"001000":AddiInstruction,
                     "000101":BeqInstruction,
                     "000111":BleInstruction,
                     "000100":BneInstruction,
                     "100011":LwInstruction,
                     "101011":SwInstruction}

map_j_instruction = {"000010":JmpInstruction}

