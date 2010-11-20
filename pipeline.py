
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
        self.done = self.instruction.write_back(self.registers)
        
    
class Pipeline(object):
    def __init__(self, mips):
        self._mips = mips
        self._pipeline = [InstructionFetch(self),
                          InstructionDecode(self),
                          Execute(self),
                          MemoryAccess(self),
                          WriteBack(self)]
        self.instructions_completed = 0
        
    def run(self):
        for phase in self._pipeline:
            if phase.instruction and not phase.done:
                phase.execute()
                
        for i in reversed(xrange(5)):
            phase = self._pipeline[i]
            next_phase = self._pipeline[i+1] if i < 4 else None
            
            if phase.done:
                if next_phase:
                    if next_phase.instruction is None:
                        self._pipeline[i+1].instruction = phase.instruction
                        self._pipeline[i].instruction = None
                else:
                    self.instructions_completed += 1
                    self._pipeline[i].instruction = None
                    
        if self._pipeline[0].instruction is None:
            self._pipeline[0].instruction = self.fetch_instruction()
            
        for p in self._pipeline:
            if p.instruction == None:
                p.instruction = NopInstruction()
            
            
    def fetch_instruction(self):
        return self._mips.fetch_instruction()
        
    def current_state(self):
        _if = self._pipeline[0].instruction
        _id = self._pipeline[1].instruction
        _ex = self._pipeline[2].instruction
        _mem = self._pipeline[3].instruction
        _wb = self._pipeline[4].instruction
    
        return {"if":_if.current_state() if _if else None,
                "id":_id.current_state() if _id else None,
                "ex":_ex.current_state() if _ex else None,
                "mem":_mem.current_state() if _mem else None,
                "wb":_wb.current_state() if _wb else None}
        
    
