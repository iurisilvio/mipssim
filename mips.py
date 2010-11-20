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
        program_counter = self.registers["pc"]
        instruction_number = int(program_counter / 4)
        
        try:
            instruction = Instruction(self.instructions[instruction_number])
            self.registers["pc"] += 4
        except IndexError:
            instruction = None
        
        return instruction

    def run(self):
        assertion = lambda pipeline: all(isinstance(p.instruction, NopInstruction) for p in pipeline._pipeline)

        while True:
            self.history.append(self.current_state())
            self.pipeline.run()
            self.clocks += 1
            
            if assertion(self.pipeline):
                self.history.append(self.current_state())
                break
                
        #file("out.txt", 'w').write("\n".join([str(state) for state in self.history]))
        
    def current_state(self):
        state = {"pipeline":self.pipeline.current_state(),
                 "registers":self.registers.current_state()["r"],
                 "clock":self.clocks,
                 "pc":self.registers["pc"],
                 "instructions_completed":self.pipeline.instructions_completed}
        return state


if __name__ == "__main__":
    print "MIPS"
