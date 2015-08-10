import sys

pointer = 0
memory = [0] * 30000
program = open(sys.argv[1], "rb")

while True:
    instruction = program.read(1)

    if instruction == "":
        break # program is finished
    if instruction == ">":
        pointer += 1
        if pointer > len(memory):
            pointer = 0
    elif instruction == "<":
        pointer -= 1
        if pointer < 0:
            pointer = len(memory)-1
    elif instruction == "+":
        memory[pointer] += 1
    elif instruction == "-":
        memory[pointer] -= 1
    elif instruction == ".":
        sys.stdout.write(chr(memory[pointer]))
        sys.stdout.flush()
    elif instruction == ",":
        memory[pointer] = ord(sys.stdin.read(1))
    elif instruction == "[":
        if memory[pointer] == 0:
            while program.read(1) != "]":
                pass
    elif instruction == "]":
        continue
    else:
        # Skip unknown instructions. 
        # This makes it possible to write
        # comments in the code!
        continue
