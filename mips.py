from __future__ import division
from instructions import Instruction, NopInstruction
from pipeline import Pipeline
from registers import Registers

REGISTERS_SIZE = 32
MEMORY_SIZE = 100

    
class Mips(object):
    def __init__(self, instructions):
        self.instructions = instructions.split("\n")

        self.registers = Registers(size=REGISTERS_SIZE, pc=0)
        self.memory = [None] * MEMORY_SIZE
        self.history = []

        self.pipeline = Pipeline(self)
        self.clocks = 0
        
    def fetch_instruction(self):
        instruction_number = int(self.registers["pc"] / 4)
        
        try:
            instruction = Instruction(self.instructions[instruction_number])
            self.registers["pc"] += 4
        except IndexError:
            instruction = None
        
        return instruction

    def run(self):
        while True:
            self.history.append(self.current_state())
            self.pipeline.run()
            self.clocks += 1
            
            if all(isinstance(p.instruction, NopInstruction) for p in self.pipeline._pipeline):
                self.history.append(self.current_state())
                break
                
        #file("out.txt", 'w').write("\n".join([str(state) for state in self.history]))
        
    def current_state(self):
        instructions_completed = self.pipeline.instructions_completed
        throughput = instructions_completed / self.clocks if self.clocks > 0 else 0
    
        state = {"pipeline":self.pipeline.current_state(),
                 "registers":self.registers.current_state()["r"],
                 "clock":self.clocks,
                 "pc":self.registers["pc"],
                 "instructions_completed":instructions_completed,
                 "throughput":throughput}
        return state


if __name__ == "__main__":
    print "MIPS"
