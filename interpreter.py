#!/usr/bin/env python

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
        self.instructions = []
        self.labels = {}
        
    def _parse_line(self, line):
        data = line.split(" ", 1)
        instruction = data[0].lower()
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
                text = "%s" % instruction
            if instruction == JMP:
                label_position = self.labels[tokens.get("label")]
                target_address = self._to_bin(label_position, 26)
                bytecode = "%s%s" % (opcode, target_address)
                text = "%s %s" % (instruction, label_position)
            if instruction in (ADDI, LW, SW, BEQ, BLE, BNE):
                rs = tokens.get("rs")
                rs_bin = self._register_to_bin(rs)
                rt = tokens.get("rt")
                rt_bin = self._register_to_bin(rt)

                if instruction in (BEQ, BNE):
                    label_position = self.labels[tokens.get("label")]
                    immediate = label_position - pc + 4
                elif instruction == BLE:
                    label_position = self.labels[tokens.get("label")]
                    immediate = label_position
                else:
                    immediate = tokens.get("immediate")
                    
                immediate_bin = self._to_bin(immediate, 16)
                    
                if instruction in (LW, SW):
                    text = "%s %s,%s(%s)" % (instruction, rt, immediate, rs)
                elif instruction in (ADDI):
                    text = "%s %s,%s,%s" % (instruction, rt, rs, immediate)
                else:
                    text = "%s %s,%s,%s" % (instruction, rs, rt, immediate)
                    
                bytecode = "%s%s%s%s" % (opcode, rs_bin, rt_bin, immediate_bin)

            if instruction in (ADD, MUL, SUB):
                rs = tokens.get("rs")
                rs_bin = self._register_to_bin(rs)
                rt = tokens.get("rt")
                rt_bin = self._register_to_bin(rt)
                rd = tokens.get("rd")
                rd_bin = self._register_to_bin(rd)
                shamt = "00000"
                funct = map_funct[instruction]
                bytecode = "%s%s%s%s%s%s" % (opcode, rs_bin, rt_bin, rd_bin, shamt, funct)
                text = "%s %s,%s,%s" % (instruction, rd, rs, rt)
                
            return "%s ; I%d: %s" % (bytecode, len(self.instructions) + 1, text)

    def _register_to_bin(self, register):
        return self._to_bin(int(register.strip("R")), 5) 
        
    def _to_bin(self, number, length=0):
        """
        Convert `number` to binary, appending zeros to left to return a string with length.
        If `number` is negative, two complement is used.
        """
        n = int(number)
        if n >= 0:
            binary = bin(abs(n))[2:]
            zeros = "0" * length
        else:
            t = ['0' if c == '1' else '1' for c in bin(abs(n))[2:]]
            
            for i in reversed(xrange(len(t))):
                if t[i] == '0':
                    t[i] = '1'
                    break
                elif t[i] == '1':
                    t[i] = '0'
                    
            t.insert(0, '1')
            binary = "".join(t)
            zeros = "1" * length
            
        return ("%s%s" % (zeros, binary))[-length:]
        
    def parse(self):
        result = []
        pc = 0
        for instruction in self.text_instructions:
            tokens = self._parse_line(instruction)
            if tokens["instruction"] == LABEL:
                self.labels[tokens["label"]] = pc
            else:
                tokens["instruction"] = tokens["instruction"].lower()
                result.append(tokens)
                pc += 4

        return result
        
    def compile(self):
        parsed_instructions = self.parse()
        self.instructions = []
        pc = 0
                
        for instruction in parsed_instructions:
            pc += 4
            self.instructions.append(self._compile_line(instruction, pc))
            
    def __str__(self):
        return "\n".join(self.instructions)
        
    
if __name__ == "__main__":
    import sys
    try:
        text = file(sys.argv[1]).read()
        interpreter = Interpreter(text)
        interpreter.compile()
        print interpreter
    except IndexError:
        print "usage: interpreter.py <filename>"
