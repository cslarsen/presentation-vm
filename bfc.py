#!/usr/bin/env python

import byteplay as bp
import sys

def compile(source):
    code = []
    code.append((bp.LOAD_CONST, "Hello there"))
    code.append((bp.PRINT_ITEM, None))
    code.append((bp.PRINT_NEWLINE, None))
    code.append((bp.LOAD_CONST, None))
    code.append((bp.RETURN_VALUE, None))
    return code

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
                retval = program()
            except Exception as e:
                print("Error: %s" % e)
                sys.exit(1)
