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

RE_NOP = re.compile(r"^(?P<instruction>nop)$")
RE_JMP = re.compile(r"^(?P<instruction>jmp) (?P<label>\w+)$")
RE_LOAD_STORE = re.compile(r"^(?P<instruction>\w+) (?P<rt>R\d+),(?P<immediate>\d+)\((?P<rs>R\d+)\)$")
RE_WITH_IMMEDIATE = re.compile(r"^(?P<instruction>\w+) (?P<rt>R\d+),(?P<rs>R\d+),(?P<immediate>\d+)$")
RE_WITH_LABEL = re.compile(r"^(?P<instruction>\w+) (?P<rs>R\d+),(?P<rt>R\d+),(?P<label>\w+)$")
RE_WITH_REGISTER = re.compile(r"^(?P<instruction>\w+) (?P<rd>R\d+),(?P<rs>R\d+),(?P<rt>R\d+)$")
RE_LABEL = re.compile(r"^(?P<label>\w+):$")

map_re = {NOP:RE_NOP,
          JMP:RE_JMP,
          LW:RE_LOAD_STORE,
          SW:RE_LOAD_STORE,
          ADDI:RE_WITH_IMMEDIATE,
          BEQ:RE_WITH_LABEL,
          BLE:RE_WITH_LABEL,
          BNE:RE_WITH_LABEL,
          ADD:RE_WITH_REGISTER,
          MUL:RE_WITH_REGISTER,
          SUB:RE_WITH_REGISTER}

map_opcode = {ADD:"000000",
              ADDI:"001000",
              BEQ:"000101",
              BLE:"000111",
              BNE:"000100",
              JMP:"000010",
              LW:"100011",
              MUL:"000000",
              NOP:"000000",
              SUB:"000000",
              SW:"101011"}
              
map_funct = {ADD:"100000",
             MUL:"011000",
             NOP:"000000",
             SUB:"100010"}


class Interpreter(object):


    def __init__(self, text=None):
        splitted_text = text.split("\n") if text else []
        self.text_instructions = [t.strip() for t in splitted_text if t.strip()]
        self.bytecode_instructions = []
        self.labels = {}
        
    def _parse_line(self, line):
        data = line.split(" ", 1)
        instruction = data[0]
        tokens_re = None
        is_label = False
        
        if instruction in _instructions:
            tokens_re = map_re[instruction]
        else:
            # label
            tokens_re = RE_LABEL
            is_label = True
        
        matches = tokens_re.match(line)
        
        if matches:
            tokens = matches.groupdict()
            if tokens:
                if is_label:
                    tokens["instruction"] = "label"
                return tokens

        raise Exception(line)
        
    def _compile_line(self, tokens, pc):
        instruction = tokens["instruction"]
        
        if instruction in _instructions:
            opcode = map_opcode[instruction]
        
            if instruction in  NOP:
                bytecode = self._to_bin(0, 32)
            if instruction == JMP:
                target_address = self._to_bin(self.labels[tokens.get("label")], 26)
                bytecode = "%s%s" % (opcode, target_address)
            if instruction in (ADDI, LW, SW, BEQ, BLE, BNE):
                rs = self._register_to_bin(tokens.get("rs"))
                rt = self._register_to_bin(tokens.get("rt"))

                if instruction in (BEQ, BNE):
                    label_position = self.labels[tokens.get("label")]
                    immediate = self._to_bin(label_position - pc - 4, 16)
                elif instruction == BLE:
                    label_position = self.labels[tokens.get("label")]
                    immediate = self._to_bin(label_position, 16)
                else:
                    immediate = self._to_bin(tokens.get("immediate"), 16)

                bytecode = "%s%s%s%s" % (opcode, rs, rt, immediate)

            if instruction in (ADD, MUL, SUB):
                rs = self._register_to_bin(tokens.get("rs"))
                rt = self._register_to_bin(tokens.get("rt"))
                rd = self._register_to_bin(tokens.get("rd"))
                shamt = "00000"
                funct = map_funct[instruction]
                bytecode = "%s%s%s%s%s%s" % (opcode, rs, rt, rd, shamt, funct)
                
            return bytecode

    def _register_to_bin(self, register):
        return self._to_bin(int(register.strip("R")), 5) 
        
    def _to_bin(self, number, length=0):
        """
        Convert `number` to binary, appending zeros to left to return a string with length.
        If `number` is negative, two complement is used.
        """
        if number >= 0:
            zeros = "0" * length
            binary = bin(int(number))[2:]
        else:
            zeros = "1" * length
            # two complement
            binary = bin(~int(number) + 1)[2:]
        return ("%s%s" % (zeros, binary))[-length:]

        
    def parse(self):
        result = []
        pc = 0
        for instruction in self.text_instructions:
            tokens = self._parse_line(instruction)
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
            self.bytecode_instructions.append(self._compile_line(instruction, pc))
            
    def __str__(self):
        result = ""
        text_instructions = [text for text in self.text_instructions if not text.endswith(":")]
        for instruction, bytecode in zip(text_instructions, self.bytecode_instructions):
            result += "%s ; %s\n" % (bytecode, instruction)
            
        return result
        
        
    def get_bytecode(self):
        return "\n".join(self.bytecode_instructions)
        
    bytecode = property(get_bytecode)
    
    
if __name__ == "__main__":
    import sys
    text = file(sys.argv[1]).read()
    interpreter = Interpreter(text)
    interpreter.compile()
    print interpreter

