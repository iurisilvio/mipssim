
from instructions import NopInstruction

class MipsPhase(object):
    def __init__(self, pipeline):
        self._instruction = NopInstruction()
        self.done = False
        self.pipeline = pipeline
        self.registers = self.pipeline._mips.registers
        self.memory = self.pipeline._mips.memory
        
    def execute(self):
        raise NotImplementedError()

    def set_instruction(self, value):
        self._instruction = value
        self.done = False
        
    def get_instruction(self):
        return self._instruction
        
    instruction = property(get_instruction, set_instruction)


class InstructionFetch(MipsPhase):
    def execute(self):
        self.done = True
            
    
class InstructionDecode(MipsPhase):
    def execute(self):
        self.done = self.instruction.instruction_decode(self.registers)
        
    
class Execute(MipsPhase):
    def execute(self):
        self.done = self.instruction.execute()
        
    
class MemoryAccess(MipsPhase):
    def execute(self):
        self.done = self.instruction.memory_access(self.memory)
        
        
class WriteBack(MipsPhase):
    def execute(self):
        if self.done and not isinstance(self.instruction, NopInstruction):
            self.pipeline.instructions_completed += 1
        self.done = self.instruction.write_back(self.registers)
        
    
class Pipeline(object):
    def __init__(self, mips):
        self._mips = mips
        self._if = InstructionFetch(self)
        self.id = InstructionDecode(self)
        self.ex = Execute(self)
        self.mem = MemoryAccess(self)
        self.wb = WriteBack(self)
        self._array = (self._if, self.id, self.ex, self.mem, self.wb)
        
    def current_state(self):
        return {"if":self._if.current_state(),
                "id":self.id.current_state(),
                "ex":self.ex.current_state(),
                "mem":self.mem.current_state(),
                "wb":self.wb.current_state()}
                
    def __getitem__(self, key):
        return self._array[key]
        
    def __setitem__(self, key, value):
        self._array[key] = value
