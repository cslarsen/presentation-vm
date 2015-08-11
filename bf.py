#!/usr/bin/env python

import sys
from collections import deque

class Machine(object):
    def __init__(self, code, memory=30000):
        self.stack = deque([])

        self.code = code
        self.cptr = 0

        self.memory = [0]*memory
        self.mptr = 0

        # Memoization for skip_block
        self.skip_memo = {}

    @property
    def byte(self):
        return self.memory[self.mptr]

    @byte.setter
    def byte(self, value):
        self.memory[self.mptr] = value

    def next(self):
        try:
            i = self.code[self.cptr]
            self.cptr += 1
            return i
        except IndexError:
            raise StopIteration()

    def dispatch(self, i):
        if i == ">":
            self.mptr += 1
        elif i == "<":
            self.mptr -= 1
        elif i == "+":
            self.byte = (self.byte + 1) % 256
        elif i == "-":
            self.byte = (self.byte - 1) % 256
        elif i == ".":
            sys.stdout.write(chr(self.byte))
            sys.stdout.flush()
        elif i == ",":
            self.byte = ord(sys.stdin.read(1))
        elif i == "[":
            if self.byte != 0:
                self.stack.append(self.cptr-1)
            else:
                self.skip_block()
        elif i == "]":
            ret = self.stack.pop()
            if self.byte != 0:
                self.cptr = ret
        else:
            # Ignore unknown instructions
            pass

    def skip_block(self):
        # Memoize
        if self.cptr in self.skip_memo:
            self.cptr = self.skip_memo[self.cptr]
            return
        else:
            cptr = self.cptr

        count = 1
        while count > 0:
            i = self.next()
            if i == "[":
                count += 1
            elif i == "]":
                count -= 1

        # Memoize
        self.skip_memo[cptr] = self.cptr

    def run(self):
        try:
            while True:
                self.dispatch(self.next())
        except StopIteration:
            pass

if __name__ == "__main__":
    for f in sys.argv[1:]:
        with open(f, "rb") as file:
            m = Machine(list(file.read()))
            m.run()
