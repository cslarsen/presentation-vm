import sys

class Machine(object):
    def __init__(self, code, memory=30000):
        self.stack = []

        self.code = code
        self.cptr = 0

        self.memory = [0]*memory
        self.mptr = 0

        self.silent = True

    @property
    def byte(self):
        return self.memory[self.mptr]

    @byte.setter
    def byte(self, value):
        self.memory[self.mptr] = value

    def next(self):
        if self.cptr >= len(self.code):
            raise StopIteration()

        i = self.code[self.cptr]
        self.cptr += 1

        if not self.silent:
            sys.stdout.write("%s" % i)
            sys.stdout.flush()

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
            self.byte -= 1
        elif i == ".":
            sys.stdout.write(chr(self.byte))
            sys.stdout.flush()
        elif i == ",":
            sys.stdout.flush()
            self.byte = ord(sys.stdin.read(1))
        elif i == "[":
            self.stack.append(self.cptr-1)
            if self.byte == 0:
                self.skip_block()
                self.stack.pop()
        elif i == "]":
            self.cptr = self.stack[-1]
        else:
            pass

    def skip_block(self):
        count = 1
        while count > 0:
            i = self.next()
            if i == "[":
                count += 1
            elif i == "]":
                count -= 1

    def run(self):
        try:
            while True:
                self.step()
        except StopIteration:
            pass

if __name__ == "__main__":
    for f in sys.argv[1:]:
        with open(f, "rb") as file:
            m = Machine(list(file.read()))
            m.run()
