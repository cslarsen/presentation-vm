#!/usr/bin/env python

import sys
import marshal
import types

def load_func(filename, name="func"):
    with open(filename, "rb") as file:
        code = marshal.loads(file.read())
        func = types.FunctionType(code, globals(), name)
        return func

if __name__ == "__main__":
    for filename in sys.argv[1:]:
        program = load_func(filename)
        program()
