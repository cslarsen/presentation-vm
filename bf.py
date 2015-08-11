import sys

class Machine(object):
    def __init__(self, code, memory=30000):
        self.stack = []

        self.code = code
        self.cptr = 0

        self.memory = [0]*memory
        self.mptr = 0

    @property
    def byte(self):
        return self.memory[self.mptr]

    @byte.setter
    def byte(self, value):
        self.memory[self.mptr] = value

    @property
    def instruction(self):
        return self.code[self.cptr]

    def next(self):
        i = self.instruction
        self.cptr += 1
        return i

    def step(self):
        i = self.next()
        self.dispatch(i)

    def dispatch(self, i):
        if i == "<":
            self.mptr -= 1
        elif i == ">":
            self.mptr += 1
        elif i == "+":
            self.byte += 1
        elif i == "-":
            self.byte += 1
        elif i == ".":
            sys.stdout.write(chr(self.byte))
            sys.stdout.flush()
        elif i == ",":
            print("INPUT")
            sys.stdout.flush()
            self.byte = ord(sys.stdin.read(1))
        elif i == "[":
            self.stack.append(self.cptr)
            if self.byte == 0:
                self.skip_block()
                self.stack.pop()
        elif i == "]":
            self.cptr = self.stack[-1]

    def skip_block(self):
        count = 1
        while count > 0:
            i = self.next()
            if i == "[":
                count += 1
            elif i == "]":
                count -= 1

    def run(self):
        while True:
            self.step()

if __name__ == "__main__":
    for f in sys.argv[1:]:
        with open(f, "rb") as file:
            print(f)
            try:
                m = Machine(list(file.read()))
                m.run()
            except IndexError:
                pass
