from __future__ import division

import instructions
from instructions import Instruction, NopInstruction
from registers import Registers
from memory import Memory

REGISTERS_SIZE = 32
MEMORY_SIZE = 100
MIPS_MAX_AGE = 10000
    
class Mips(object):
    def __init__(self, instructions=None, data_forwarding=False):
        self.instructions = instructions.split("\n") if instructions else []
        self.data_forwarding = data_forwarding
        
        self.registers = Registers(size=REGISTERS_SIZE)
        self.memory = Memory(size=MEMORY_SIZE)
        self.history = []

        self.pc = 0
        self.clocks = 0
        self.instructions_completed = 0
        
        self._if = InstructionFetch(self)
        self._id = InstructionDecode(self)
        self._ex = Execute(self)
        self._mem = MemoryAccess(self)
        self._wb = WriteBack(self)
        self.pipeline = (self._if, self._id, self._ex, self._mem, self._wb)

    def run(self, life=MIPS_MAX_AGE):
        while True:
            self.history.append(self.current_state())
            self.execute_pipeline()
            self.clocks += 1
            
            if self.clocks > life or all(isinstance(p.instruction, NopInstruction) for p in self.pipeline):
                self.history.append(self.current_state())
                break

    def _go_forward_pipeline(self):
        if self.pipeline[4].done:
            self.pipeline[4].instruction = None
                        
        for a, b in reversed(zip(self.pipeline[:-1], self.pipeline[1:])):
            if a.done and b.instruction is None:
                b.instruction = a.instruction
                a.instruction = None
    
    def execute_pipeline(self):
        self._go_forward_pipeline()

        for phase in self.pipeline:
            phase.execute()
            if not phase.instruction:
                phase.instruction = NopInstruction()

    def jump(self, pc):
        self._if.instruction.unlock_registers(self)
        self._if.instruction = NopInstruction()
        self._id.instruction.unlock_registers(self)
        self._id.instruction = NopInstruction()
        self.pc = pc
    
    def current_state(self):
        instructions_completed = self.instructions_completed
        throughput = instructions_completed / self.clocks if self.clocks > 0 else 0
    
        state = {"pipeline":[p.instruction.current_state() for p in self.pipeline],
                 "registers":self.registers.current_state(),
                 "memory":self.memory.history[-4:],
                 "clock":self.clocks,
                 "pc":self.pc,
                 "instructions_completed":instructions_completed,
                 "throughput":throughput}
        return state
        
    
class MipsPhase(object):
    def __init__(self, mips):
        self._mips = mips
        self._instruction = NopInstruction()
        self.done = True
        
    def execute(self):
        raise NotImplementedError()

    def set_instruction(self, value):
        self._instruction = value
        self.done = isinstance(value, NopInstruction) or value is None
        
    def get_instruction(self):
        return self._instruction
        
    instruction = property(get_instruction, set_instruction)

class InstructionFetch(MipsPhase):
    def execute(self):
        if not self.instruction:
            instruction_number = int(self._mips.pc / 4)
            
            try:
                instruction = Instruction(self._mips.instructions[instruction_number])
                self._mips.pc += 4
            except IndexError:
                instruction = None
            
            self.instruction = instruction

        self.done = not self.instruction is None

    
class InstructionDecode(MipsPhase):
    def _on_register_changed(self, **kwargs):
        for key, value in kwargs.items():
            self.registers[key] = value

    def execute(self):
        if self.instruction:
            self.done = self.instruction.instruction_decode(self._mips)
        else:
            self.done = True
        
    
class Execute(MipsPhase):
    def execute(self):
        if self.instruction:
            self.done = self.instruction.execute(self._mips)
        else:
            self.done = True
        
    
class MemoryAccess(MipsPhase):
    def execute(self):
        if self.instruction:
            self.done = self.instruction.memory_access(self._mips)
        else:
            self.done = True
        
        
class WriteBack(MipsPhase):
    def execute(self):
        if self.instruction:
            self.done = self.instruction.write_back(self._mips)
            if self.done and not isinstance(self.instruction, NopInstruction):
                self._mips.instructions_completed += 1
        else:
            self.done = True
    

