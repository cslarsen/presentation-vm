#!/usr/bin/env python

import sys

memptr = 0
memory = [0] * 30000

codeptr = 0
code = list(open(sys.argv[1], "rb").read())
code.append(None) # end-of-code marker

loops = []

def debug():
    print("code[%d] == '%c' memory[%d] == %d" % (codeptr, code[codeptr], memptr,
        int(memory[memptr])))

while True:

    instruction = code[codeptr]
    #debug()

    if instruction is None:
        break # code is finished
    if instruction == ">":
        memptr += 1
        if memptr > len(memory):
            memptr = 0
    elif instruction == "<":
        memptr -= 1
        if memptr < 0:
            memptr = len(memory)-1
    elif instruction == "+":
        memory[memptr] += 1
    elif instruction == "-":
        memory[memptr] -= 1
    elif instruction == ".":
        sys.stdout.write(chr(memory[memptr]))
        sys.stdout.flush()
    elif instruction == ",":
        memory[memptr] = ord(sys.stdin.read(1))
    elif instruction == "[":
        loops.append(codeptr)
        if memory[memptr] == 0:
            # Scan to next matching "]"
            count = 1
            codeptr += 1
            while count != 0:
                if code[codeptr] == "[":
                    count += 1
                elif code[codeptr] == "]":
                    count -= 1
                codeptr += 1
    elif instruction == "]":
        if memory[memptr] == 0:
            codeptr = loops.pop()
            continue
        else:
            codeptr = loops[-1]
            continue
    else:
        # Skip unknown instructions
        pass

    codeptr += 1
