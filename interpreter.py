import re

ADD = "add"
ADDI = "addi"
BEQ = "beq"
BLE = "ble"
BNE = "bne"
JMP = "jmp"
LW = "lw"
MUL = "mul"
NOP = "nop"
SUB = "sub"
SW = "sw"
LABEL = "label"

_instructions = [ADD, ADDI, BEQ, BLE, BNE, JMP, LW, MUL, NOP, SUB, SW]


class Interpreter(object):

    def __init__(self, text=None):
        splitted_text = text.split("\n") if text else []
        self.text_instructions = [t.strip() for t in splitted_text]
        self.bytecode_instructions = []
        self.labels = {}
        
    def _parse(self, line):
        data = line.split(" ", 1)
        instruction = data[0]
        tokens_re = None
        
        if instruction in _instructions:
            if instruction == NOP:
                tokens_re = re.compile("^(?P<instruction>nop)$")
            elif instruction == JMP:
                tokens_re = re.compile("^(?P<instruction>jmp) (?P<label>\w+)$")
            elif instruction in [LW, SW]:
                tokens_re = re.compile("^(?P<instruction>\w+) (?P<rt>R\d+),(?P<immediate>\d+)\((?<rs>R\d+)\)$")
            elif instruction in [ADDI, BEQ, BLE, BNE]:
                tokens_re = re.compile("^(?P<instruction>\w+) (?P<rt>R\d+),(?P<rs>R\d+),(?P<immediate>\d+)$")
            elif instruction in [ADD, MUL, SUB]:
                tokens_re = re.compile("^(?P<instruction>\w+) (?P<rd>R\d+),(?P<rs>R\d+),(?P<rt>R\d+)$")
        else:
            # label
            tokens_re = re.compile("^(?P<label>\w+):$")
        
        if tokens_re:
            tokens = tokens_re.match(line).groupdict()
            if tokens:
                if tokens.get("label"):
                    tokens["instruction"] = "label"
                return tokens

        raise Exception()
        
    def _compile_line(self, tokens, labels={}):
        instruction = tokens["instruction"]
        
        if instruction in _instructions:
            if instruction in  NOP:
                bytecode = "00000000000000000000000000000000"
            if instruction == JMP:
                pass
        else:
            # label
            bytecode = ""
            
        return bytecode
        
    def parse(self):
        result = []
        pc = 0

        for instruction in self.text_instructions:
            tokens = self._parse(instruction)
            if tokens["instruction"] == LABEL:
                self.labels[tokens["label"]] = pc
            else:
                result.append(tokens)
                pc += 4

        return result
        
    def compile(self):
        parsed_instructions = self.parse()
        self.bytecode_instructions = []
        pc = 0
        
        for instruction in parsed_instructions:
            pc += 4
            self.bytecode_instructions.append(self._compile_line(instruction))
            
    def __str__(self):
        result = ""
        for instruction, bytecode in zip(self.instructions, self.bytecode):
            result += "%s ; %s\n" % (bytecode, instruction)
            
        return result
        

