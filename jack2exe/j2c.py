"""
 *                             jack to exe
 *
 *                      14 march MMXXI PUBLIC DOMAIN
 *           The author disclaims copyright to this source code.
 *
 *
"""

import re
import codegen

ast = codegen.ast
current = ast
tokens = []
className = ""
c_ = ""
t_ = ""
m = "f"

def wri(txt):
    fi1 = open("j2exe.c", "a+")
    fi1.write(txt)
    fi1.close()

def h(txt):
    wri(txt)

def c(txt):
    global c_
    c_ = c_ + txt

def t(txt):
    global t_
    t_ = t_ + txt

def identifier_():
    return tokens.pop(0)

def match(txt):
    if tokens[0] == txt:
        tokens.pop(0)
        return 1
    else:
        print "syntax error: expected '" + txt + "' got '" + tokens[0] + "'"
        exit(-1)

def classVarDec_():
    global className
    p = className + "__"
    l = h;
    if tokens[0] == "static":
        tokens.pop(0)
        l = t
    elif tokens[0] == "field":
        tokens.pop(0)
        p = "";
    else:
        return 0
    type_ = identifier_()
    varName = identifier_()
    l("var " + p + varName)
    while tokens[0] == ",":
        tokens.pop(0)
        varName = identifier_()
        l(", " + p + varName)
    l(";")
    match(";")
    return 1
       
def stringConstant_():
    if (tokens[0][0] == "\""):
        strin = tokens.pop(0)
        return 1
    return 0

def integerConstant_():
    if (is_integer(tokens[0][0])):
        num = tokens.pop(0)
        return 1
    return 0

def is_integer(t):    
    if (ord(t[0]) >= ord("0") and ord(t[0]) <= ord("9")):
        return 1
    return 0

def is_identifier():    
    if (tokens[0][0] == "_"  or
        (ord(tokens[0][0]) >= ord("a") and ord(tokens[0][0]) <= ord("z"))  or
            (ord(tokens[0][0]) >= ord("A") and ord(tokens[0][0]) <= ord("Z"))): 
        return 1
    return 0

def term_():
    if integerConstant_():
        return 1
    elif stringConstant_():
        return 1
    elif subroutineCall_():
        return 1
    elif tokens[1] == "[":
        varName = tokens.pop(0)
        match("[")
        expression_()
        match("]")
        return 1
    elif tokens[0] == "(":
        match("(")
        expression_()
        match(")")
        return 1
    elif tokens[0] == "-" or tokens[0] == "~":
        unaryOp = tokens.pop(0)
        term_()
        return 1
    elif is_identifier():
        varName = tokens.pop(0)
        return 1;
    return 0

def expression_():
    ret = 0;
    while term_():
        ret = 1
        if (tokens[0] == "+" or 
            tokens[0] == "-" or 
            tokens[0] == "+" or 
            tokens[0] == "/" or 
            tokens[0] == "*" or 
            tokens[0] == "&" or 
            tokens[0] == "|" or 
            tokens[0] == "<" or 
            tokens[0] == ">" or 
            tokens[0] == "="): 
            op = tokens.pop(0)
        else:
            return ret
    return ret

def subroutineCall_():
    global current
    last = current
    if is_identifier() == 0:
        return 0
    if (tokens[1] == "."):
        if tokens[3] != "(":
            return 0
        classVarName = identifier_()
        match(".")
    elif tokens[1] != "(":
        return 0
    subroutineName = identifier_()
    current = current.set("subroutineCall").add(subroutineName)
    current.set("classVarName").add(classVarName)
    match("(");
    current = current.set("parameters")
    if expression_():
        while tokens[0] == ",":
            tokens.pop(0)
            expression_()
    match(")");
    current = last
    return 1


def statement_():
    global current
    if tokens[0] == "let":
        tokens.pop(0)
        varName = identifier_()
        if tokens[0] == "[":
            match("[")
            expression_()
            match("]")
        match("=")
        expression_()
        match(";")
    elif tokens[0] == "if":
        tokens.pop(0)
        match("(")
        match(")")
        match("{")
        while (statement_()):
            pass
        match("}")
        if tokens[0] == "else":
            match("else")
            match("{")
            while (statement_()):
                pass
            match("}")
    elif tokens[0] == "while":
        tokens.pop(0)
        match("(")
        match(")")
        match("{")
        while (statement_()):
            pass
        match("}")
    elif tokens[0] == "do":
        tokens.pop(0)
        subroutineCall_()
        match(";")
        c(";")
    elif tokens[0] == "return":
        tokens.pop(0)
        expression_()
        match(";")
    else:
        return 0
    return 1

def subroutineDec_():
    global className
    global m
    global current
    last = current
    m = "c"
    if tokens[0] == "constructor":
        tokens.pop(0)
        current = current.set("constructor")
    elif tokens[0] == "function":
        tokens.pop(0)
        current = current.set("function")
        m = "f"
    elif tokens[0] == "method":
        tokens.pop(0)
        current = current.set("method")
        m = "m"
    else:
        return 0
    type_ = identifier_()
    subroutineName = identifier_()
    
    current = current.add(subroutineName)
    current.set("RetType").add(type_)

    c("\n")
    c(type_ + " " + className + "__" + subroutineName + " ( ")
    match("(")
    if tokens[0] != ")":
        type_ = identifier_()
        paramName = identifier_()
        c("var " + paramName)
        current.set("paramName").add(paramName).add(type_)
        while tokens[0] == ",":
            tokens.pop(0)
            type_ = identifier_()
            paramName = identifier_()
            current.set("paramName").add(paramName).add(type_)
            c(", var " + paramName)
    match(")")
    match("{")
    c(") {")
    while tokens[0] == "var":
        type_ = identifier_()
        varName = identifier_()
        c("var " + varName)
        current.set("varName").add(varName).add(type_)
        while tokens[0] == ",":
            tokens.pop(0)
            varName = identifier_()
            current.set("varName").add(varName).add(type_)
            c(", var " + varName)
        match(";");
        c(";");
        
    while (statement_()):
        pass
    match("}")
    c("}")
    current = last
    return 1


def class_(txt):
    global className
    global ast
    global current
    match("class")
    className = identifier_()
    match("{")

    class_n = current.add(className)
    current = class_n.add("classVarDec");
    while (classVarDec_()):
        pass
    h("} " + className + ";")
    current = class_n.add("subroutineDec");
    while (subroutineDec_()):
        pass
    match("}");
    current = ast
    return 1


incomment = 0
s = ""

def tokenize(x):
    global incomment
    global s
    insinglec = 0
    inquote = 0
    r = []
    l = ""
    for c in x:
        if inquote == 0 and c == "*" and l == "/" and incomment == 0:
            incomment = 1
            if s != "":
                r.append(s)
            s = ""
            s = s + "/"
        
        elif inquote == 0 and c == "/" and l == "*" and incomment == 1:
            incomment = 0
            s = s + "*/"
            c = ""
            print s
            s = ""
        elif inquote == 1 and c == "\"":
            inquote = 0
            s = s + l + c
            r.append(s)
            s = ""
            c = ""
        elif incomment == 1 or insinglec == 1 or inquote == 1:
            s = s + l
        elif l == "\"":
            inquote = 1
            if s != "":
                r.append(s)
            s = "\""
        elif c == "/" and l == "/":
            insinglec = 1
            if s != "":
                r.append(s)
            s = "/"
        elif l == " " or l == "\t" or l == "\n" or l == "\r":
            if s != "":
                r.append(s)
            s = ""
        elif (l == "(" or l == ")" or l == "{" or l == "}"
            or l == "[" or l == "]" or l == ";" or l == "," 
            or l == "=" or l == "+" or l == "-" or l == "*"
            or l == "/" or l == "<" or l == ">" or l == "&"
            or l == "|" or l == "." or l == "~"):
            if s != "":
                r.append(s)
            s = l
            r.append(s)
            s = ""
        else:
            s = s + l
        l = c
    s = s + l
    if incomment == 0:
        if insinglec == 1:
            s = ""
        elif s != "" and s != " " and s != "\n"  and s != "\t":
            r.append(s)
            s =  ""
        else :
            s = ""
    return r

def parse (f):
    global tokens
    global c_
    tokens = []
    fi = open(f, "r");
    for x in fi:
        for y in tokenize(x):
            tokens.append(y)

    while len(tokens) > 0:
        class_(tokens[0])
    fi.close()



import os
from os import walk

if os.path.exists("j2exe.c"):
    os.remove("j2exe.c")

_, _, files = next(walk("jexe"), (None, None, []))

h("typedef union var {")
h("  void *pointer;")
h("  short int_;")
h("  unsigned short char_;")
h("  int boolean_;")
h("} var;")

for f in files:
    parse("jexe/" + f)

wri(t_)
c("\n")
c("int main(int argc, char *argv[]) {")
c("  Main__main();")
c("  return 0;")
c("}")
wri(c_)

print ast

