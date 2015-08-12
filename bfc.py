#!/usr/bin/env python

import byteplay as bp
import sys

def compile_example(source):
    code = []
    code.append((bp.LOAD_CONST, "Hello there"))
    code.append((bp.PRINT_ITEM, None))
    code.append((bp.PRINT_NEWLINE, None))
    code.append((bp.LOAD_CONST, None))
    code.append((bp.RETURN_VALUE, None))
    return code

def compile(source, memsize=100000):
    c = []

    # TODO:
    # Labels: Each [ and ] need an associated label,
    #         so at "[" we can JZ while_end and at
    #         "]" we can JNZ while_begin

    # import sys
    c.append((bp.LOAD_CONST, -1))
    c.append((bp.LOAD_CONST, None))
    c.append((bp.IMPORT_NAME, "sys"))
    c.append((bp.STORE_FAST, "sys"))

    # memory = [0]*memsize
    c.append((bp.LOAD_CONST, 0))
    c.append((bp.BUILD_LIST, 1))
    c.append((bp.LOAD_CONST, memsize))
    c.append((bp.BINARY_MULTIPLY, None))
    c.append((bp.STORE_FAST, "memory"))

    # ptr = 0
    c.append((bp.LOAD_CONST, 0))
    c.append((bp.STORE_FAST, "ptr"))

    def add(value):
        c.append((bp.LOAD_FAST, "memory"))
        c.append((bp.LOAD_FAST, "ptr"))
        c.append((bp.DUP_TOPX, 2))
        c.append((bp.BINARY_SUBSCR, None))
        c.append((bp.LOAD_CONST, value))
        c.append((bp.INPLACE_ADD, None))
        c.append((bp.ROT_THREE, None))
        c.append((bp.STORE_SUBSCR, None))

    plus = lambda: add(1)
    minus = lambda: add(-1)

    def dot():
        c.append((bp.LOAD_GLOBAL, "sys"))
        c.append((bp.LOAD_ATTR, "stdout"))
        c.append((bp.LOAD_ATTR, "write"))
        c.append((bp.LOAD_GLOBAL, "chr"))
        c.append((bp.LOAD_FAST, "memory"))
        c.append((bp.LOAD_FAST, "ptr"))
        c.append((bp.BINARY_SUBSCR, None))
        c.append((bp.CALL_FUNCTION, 1))
        c.append((bp.CALL_FUNCTION, 1))
        c.append((bp.POP_TOP, None))

    def comma():
        c.append((bp.LOAD_GLOBAL, "ord"))
        c.append((bp.LOAD_FAST, "sys"))
        c.append((bp.LOAD_ATTR, "stdin"))
        c.append((bp.LOAD_ATTR, "read"))
        c.append((bp.LOAD_CONST, 1))
        c.append((bp.CALL_FUNCTION, 1))
        c.append((bp.CALL_FUNCTION, 1))
        c.append((bp.LOAD_FAST, "memory"))
        c.append((bp.LOAD_FAST, "ptr"))
        c.append((bp.STORE_SUBSCR, None))

    def move(amount):
        c.append((bp.LOAD_FAST, "ptr"))
        c.append((bp.LOAD_CONST, amount))
        c.append((bp.INPLACE_ADD, None))
        c.append((bp.STORE_FAST, "ptr"))

    right = lambda: move(1)
    left = lambda: move(-1)

    # Build jump map
    def build_jumpmap():
        return {}
    jumpmap = build_jumpmap()

    def start_loop():
        pass

    def end_loop():
        pass

    # Translate Brainfuck to Python bytecode
    for op in source:
        if op == ">":
            right()
        elif op == "<":
            left()
        elif op == "+":
            plus()
        elif op == "-":
            minus()
        elif op == ".":
            dot()
        elif op == ",":
            comma()
        elif op == "[":
            start_loop()
        elif op == "]":
            end_loop()
        else:
            pass

    # return None
    c.append((bp.LOAD_CONST, None))
    c.append((bp.RETURN_VALUE, None))
    return c


def to_code(bytecode, name = "", docstring="", filename=""):
    arglist = ()
    freevars = []
    varargs = False
    varkwargs = False
    newlocals = True
    firstlineno = 1

    codeobj = bp.Code(bytecode, freevars=freevars, args=arglist,
            varargs=varargs, varkwargs=varkwargs, newlocals=newlocals,
            name=name, filename=filename, firstlineno=firstlineno,
            docstring=docstring)

    return codeobj

def make_function(codeobj):
    func = lambda: None
    func.__doc__ = codeobj.docstring
    func.__name__ == codeobj.name
    func.func_code = bp.Code.to_code(codeobj)
    return func

if __name__ == "__main__":
    for filename in sys.argv[1:]:
        with open(filename, "rt") as file:
            program = make_function(to_code(compile(file.read())))
            try:
                program()
            except Exception as e:
                print("Error: %s" % e)
                sys.exit(1)
