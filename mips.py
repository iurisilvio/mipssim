from instructions import Instruction

REGISTERS_SIZE = 32
MEMORY_SIZE = 1024

from pipeline import Pipeline
from registers import Registers
    
class Mips(object):
    def __init__(self, instructions):
        self.instructions = instructions.split("\n")

        self.registers = Registers(size=REGISTERS_SIZE, pc=0)
        self.memory = [None] * MEMORY_SIZE
        self.history = []

        self.pipeline = Pipeline(self)
        
    def fetch_instruction(self):
        program_counter = self.registers["pc"]
        instruction_number = int(program_counter / 4)
        self.registers["pc"] += 4
        
        try:
            instruction = Instruction(self.instructions[instruction_number])
        except IndexError:
            instruction = None
        
        return instruction


if __name__ == "__main__":
    print "MIPS"
