#!/usr/bin/env python

import byteplay as bp
import sys
import os

def optimize_source(source):
    # First pass: Remove any unknown operators
    source = filter(lambda x: x in ["+", "-", ">", "<", ".", ",", "[", "]"],
            source)

    # Truncate long sequences of the same operation
    keep_running = True
    while keep_running:
        keep_running = False

        for pos, op in enumerate(source):
            if op not in ["+", "-", ">", "<", ".", ","]:
                continue

            length = 1
            try:
                while source[pos+length] == op:
                    length += 1
            except IndexError:
                length -= 1

            if length > 1:
                source[pos:pos+length] = [(op, length)]
                # Start over again
                keep_running = True
                break
    return source

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

    def dot(count):
        # Prepare call to sys.stdout.write(chr(...))
        c.append((bp.LOAD_GLOBAL, "sys"))
        c.append((bp.LOAD_ATTR, "stdout"))
        c.append((bp.LOAD_ATTR, "write"))
        c.append((bp.LOAD_GLOBAL, "chr"))

        # Get value
        c.append((bp.LOAD_FAST, "memory"))
        c.append((bp.LOAD_FAST, "ptr"))
        c.append((bp.BINARY_SUBSCR, None))

        # Call chr
        c.append((bp.CALL_FUNCTION, 1))

        if count > 1:
            c.append((bp.LOAD_CONST, count))
            c.append((bp.BINARY_MULTIPLY, None))

        # Call sys.stdout.write
        c.append((bp.CALL_FUNCTION, 1))
        # Drop return-value
        c.append((bp.POP_TOP, None))

        # Flush
        c.append((bp.LOAD_GLOBAL, "sys"))
        c.append((bp.LOAD_ATTR, "stdout"))
        c.append((bp.LOAD_ATTR, "flush"))
        c.append((bp.CALL_FUNCTION, 0))
        c.append((bp.POP_TOP, None))

    def comma(count):
        c.append((bp.LOAD_GLOBAL, "ord"))
        c.append((bp.LOAD_FAST, "sys"))
        c.append((bp.LOAD_ATTR, "stdin"))
        c.append((bp.LOAD_ATTR, "read"))
        c.append((bp.LOAD_CONST, count))
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

    labels = []
    labelpos = {}

    def start_loop(label):
        c.append((label, None))
        c.append((bp.LOAD_FAST, "memory"))
        c.append((bp.LOAD_FAST, "ptr"))
        c.append((bp.BINARY_SUBSCR, None))
        c.append((bp.LOAD_CONST, 0))
        c.append((bp.COMPARE_OP, "=="))

        # We don't know the label of the end-of-loop position, so store a
        # temporary marker and get back to it later
        c.append((bp.POP_JUMP_IF_TRUE, None))
        labelpos[label] = len(c)-1

    def end_loop(startlabel):
        endlabel = bp.Label()

        # Update goto end-of-loop label
        start = labelpos[startlabel]
        c[start] = (bp.POP_JUMP_IF_TRUE, endlabel)

        c.append((endlabel, None))
        c.append((bp.LOAD_FAST, "memory"))
        c.append((bp.LOAD_FAST, "ptr"))
        c.append((bp.BINARY_SUBSCR, None))
        c.append((bp.LOAD_CONST, 0))
        c.append((bp.COMPARE_OP, "=="))
        c.append((bp.POP_JUMP_IF_FALSE, startlabel))

    # Translate Brainfuck to Python bytecode
    for pos, op in enumerate(optimize_source(source)):
        start = len(c)-1

        count = 1
        if isinstance(op, tuple):
            op, count = op

        if op == ">":
            move(count)
        elif op == "<":
            move(-count)
        elif op == "+":
            add(count)
        elif op == "-":
            add(-count)
        elif op == ".":
            dot(count)
        elif op == ",":
            comma(count)
        elif op == "[":
            labels.append(bp.Label())
            start_loop(labels[-1])
        elif op == "]":
            end_loop(labels.pop())
        else:
            print("Unknown operator: %s" % op)
            sys.exit(1)
            continue
        end = len(c)-1

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
    export = False
    for arg in sys.argv[1:]:
        if arg == "-e":
            export = True
            break

    for filename in sys.argv[1:]:
        if filename[0] == "-":
            continue
        with open(filename, "rt") as file:
            name = os.path.splitext(os.path.basename(filename))[0]
            program = make_function(to_code(compile(list(file.read())),
                name=name))
            if not export:
                program()
            else:
                import marshal
                s = marshal.dumps(program.func_code)
                with open(name + ".marshalled", "wb") as f:
                    f.write(s)
