import logging

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
            return instruction
            instruction.text = text
            
        
    def __new__(cls, line):
        bytecode, text = line.split(";")
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
        
    def instruction_decode(self, registers):
        return True
                
    def execute(self):
        self.execution_time -= 1
        return self.execution_time == 0
        
    def memory_access(self, memory):
        return True
                
    def write_back(self, registers):
        return True
        

class AddInstruction(BaseInstruction):
    def __init__(self):
        BaseInstruction.__init__(self,
            REG_DST=1, REG_WRITE=1, EXT_OP=None)
        
    def instruction_decode(self, registers):
        try:
            self.rs_value = registers[self.rs]
            self.rt_value = registers[self.rt]
            registers.lock(self.rd)
            return True
            
        except RegisterInUseException:
            print "AddInstruction blocked"
            return False
        
    def execute(self):
        BaseInstruction.execute(self)
        self.rd_value = self.rs_value + self.rt_value
        return self.execution_time == 0
        
    def write_back(self, registers):
        registers.unlock(self.rd)
        registers[self.rd] = self.rd_value
        return True


class AddiInstruction(BaseInstruction):
    def __init__(self):
        BaseInstruction.__init__(self,
            REG_DST=1, REG_WRITE=1, EXT_OP=1, ALU_SRC=1)
                                           
    def instruction_decode(self, registers):
        try:
            self.rs_value = registers[self.rs]
            registers.lock(self.rt)
            return True
        except RegisterInUseException:
            print "AddiInstruction blocked"
            return False

    def execute(self):
        BaseInstruction.execute(self)
        self.rt_value = self.rs_value + self.immediate
        return self.execution_time == 0
        
    def write_back(self, registers):
        registers.unlock(self.rt)
        registers[self.rt] = self.rt_value
        return True
        
        
class BeqInstruction(BaseInstruction):
    def __init__(self):
        BaseInstruction.__init__(self,
            REG_DST=None, MEM_TO_REG=None, BRANCH=1, EXT_OP=None)
                
    def instruction_decode(self, registers):
        self.rs_value = registers[self.rs]
        self.rt_value = registers[self.rt]
        self.pc = registers["pc"]
        return True
        
    def execute(self):
        BaseInstruction.execute(self)
        if self.rs_value == self.rt_value:
            self.pc = self.pc + self.immediate + 4
        return self.execution_time == 0
        
    def write_back(self, registers):
        registers["pc"] = self.pc
        return True
        
        
class BleInstruction(BaseInstruction):
    def __init__(self):
        BaseInstruction.__init__(self,
            REG_DST=None, MEM_TO_REG=None, BRANCH=1, EXT_OP=None)
                
    def instruction_decode(self, registers):
        self.rs_value = registers[self.rs]
        self.rt_value = registers[self.rt]
        self.pc = registers["pc"]
        return True
        
    def execute(self):
        BaseInstruction.execute(self)
        if self.rs_value <= self.rt_value:
            self.pc = self.immediate
        return self.execution_time == 0
        
    def write_back(self, registers):
        registers["pc"] = self.pc
        return True


class BneInstruction(BaseInstruction):
    def __init__(self):
        BaseInstruction.__init__(self,
            REG_DST=None, MEM_TO_REG=None, BRANCH=1, EXT_OP=None)
                
    def instruction_decode(self, registers):
        self.rs_value = registers[self.rs]
        self.rt_value = registers[self.rt]
        self.pc = registers["pc"]
        return True
        
    def execute(self):
        BaseInstruction.execute(self)
        if self.rs_value != self.rt_value:
            self.pc = self.pc + self.immediate + 4
        return self.execution_time == 0
                    
    def write_back(self, registers):
        registers["pc"] = self.pc
        return True
        
        
class JmpInstruction(BaseInstruction):
    def __init__(self):
        BaseInstruction.__init__(self,
            REG_DST=None, ALU_SRC=None, MEM_TO_REG=None, JUMP=1, EXT_OP=None)
                 
    def instruction_decode(self, registers):
        self.pc = self.target_address
        return True
        
    def write_back(self, registers):
        registers["pc"] = self.pc
        return True
        
    
class LwInstruction(BaseInstruction):
    def __init__(self):
        BaseInstruction.__init__(self,
            REG_DST=None, ALU_SRC=1, MEM_TO_REG=None, MEM_WRITE=1, EXT_OP=1)
                                           
    def instruction_decode(self, registers):
        try:
            self.rs_value = registers[self.rs]
            registers.lock(self.rt)
            return True
        except RegisterInUseException:
            print "LwInstruction blocked"
            return False
                                          
    def execute(self):
        BaseInstruction.execute(self)
        self.target_address = self.rs_value + self.immediate
        return self.execution_time == 0
        
    def memory_access(self, memory):
        self.rt_value = memory[self.target_address]
        return True
                
    def write_back(self, registers):
        registers.unlock(self.rt)
        registers[self.rt] = self.rt_value
        return True
        

class MulInstruction(BaseInstruction):
    def __init__(self):
        BaseInstruction.__init__(self, execution_time=2,
            REG_DST=1, REG_WRITE=1, EXT_OP=None)
                                  
    def instruction_decode(self, registers):
        try:
            self.rs_value = registers[self.rs]
            self.rt_value = registers[self.rt]
            registers.lock(self.rd)
            return True
        except RegisterInUseException:
            print "MulInstruction blocked"
            return False
        
    def execute(self):
        BaseInstruction.execute(self)
        self.rd_value = self.rs_value * self.rt_value
        return self.execution_time == 0
        
    def write_back(self, registers):
        registers.unlock(self.rd)
        registers[self.rd] = self.rd_value
        return True
        

class NopInstruction(BaseInstruction):
    def __init__(self):
        BaseInstruction.__init__(self,
            REG_DST=1, REG_WRITE=1, EXT_OP=None)
                                  

class SubInstruction(BaseInstruction):
    def __init__(self):
        BaseInstruction.__init__(self,
            REG_WRITE=1, EXT_OP=None)
        
    def instruction_decode(self, registers):
        try:
            self.rs_value = registers[self.rs]
            self.rt_value = registers[self.rt]
            registers.lock(self.rd)
            return True
        except RegisterInUseException:
            print "SubInstruction blocked"
            return False
        
    def execute(self):
        BaseInstruction.execute(self)
        self.rd_value = self.rs_value - self.rt_value
        return self.execution_time == 0

    def write_back(self, registers):
        registers.unlock(self.rd)
        registers[self.rd] = self.rd_value
        return True
        

class SwInstruction(BaseInstruction):
    def __init__(self):
        BaseInstruction.__init__(self,
            ALU_SRC=1, MEM_TO_REG=1, REG_WRITE=1, EXT_OP=1)
                                           
    def instruction_decode(self, registers):
        self.rs_value = registers[self.rs]
        self.rt_value = registers[self.rt]
        return True
                                  
    def execute(self):
        BaseInstruction.execute(self)
        self.memory_address = self.rs_value + self.immediate
        return self.execution_time == 0
        
    def memory_access(self, memory):
        memory[self.memory_address] = self.rt_value
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

