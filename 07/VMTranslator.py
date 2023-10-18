from enum import Enum
from typing import Type

COMMENT = "//"
ARITHMETIC_OPS = set()
ARITHMETIC_OPS.add("eq")
ARITHMETIC_OPS.add("lt")
ARITHMETIC_OPS.add("gt")
ARITHMETIC_OPS.add("add")
ARITHMETIC_OPS.add("sub")
ARITHMETIC_OPS.add("neg")
ARITHMETIC_OPS.add("and")
ARITHMETIC_OPS.add("or")
ARITHMETIC_OPS.add("not")


def getComparisonCode(cond, op, idx):
    return f'@SP\nM=M-1\nA=M\nD=M\n@SP\nM=M-1\nA=M\n{cond}\n@COND{idx}\nD;{op}\n@SP\nA=M\nM=0\n@SP\nM=M+1\n@ELSE{idx}\n0;JMP\n(COND{idx})\n@SP\nA=M\nM=-1\n@SP\nM=M+1\n(ELSE{idx})\n'


def getBinOpCode(op):
    return f"@SP\nM=M-1\nA=M\nD=M\n@SP\nM=M-1\nA=M\n{op}\n@SP\nA=M\nM=D\n@SP\nM=M+1\n"


def getUniOpCode(op):
    return f"@SP\nM=M-1\nA=M\nD=M\n@SP\nA=M\n{op}\n@SP\nM=M+1\n"


def getMainSegPushCode(seg):
    return f"D=A\n@{seg}\nD=D+M\nA=D\nD=M\n@SP\nA=M\nM=D\n@SP\nM=M+1\n"


def getMainSegPopCode(seg, i):
    return f"@{i}\nD=A\n@{seg}\nD=D+M\n@i\nM=D\n@SP\nM=M-1\n@SP\nA=M\nD=M\n@i\nA=M\nM=D\n"


def getPointerPushCode(base):
    return f"@{base}\nD=M\n@SP\nA=M\nM=D\n@SP\nM=M+1\n"


def getPointerPopCode(base):
    return f"@SP\nM=M-1\nA=M\nD=M\n@{base}\nM=D\n"

class CommandType(Enum):
    C_ARITHMETIC = 0
    C_PUSH = 1
    C_POP = 2
    C_FUNCTION = 3
    C_CALL = 4
    C_RETURN = 5


# parses each VM command into its lexical elements
class Parser:
    def __init__(self, filename) -> None:
        with open(filename) as f:
            self.lines = f.readlines()

        tmp = []
        for line in self.lines:
            line = line.strip()
            if line.startswith(COMMENT) or not line:
                continue
            # remove inline comments
            if COMMENT in line:
                line = line[:line.index(COMMENT)]
                line = line.strip()
            tmp.append(line)
        self.lines = tmp
        self.curLineNum = 0

    def hasMoreLines(self) -> bool:
        return self.curLineNum < len(self.lines)

    def advance(self) -> None:
        self.curLine = self.lines[self.curLineNum]
        arr = self.curLine.split(" ")
        self.curArr = [a for a in arr if a]
        self.curLineNum += 1

    def getCommandType(self) -> Type[CommandType]:
        curArr = self.curArr
        if curArr[0] == "push":
            return CommandType.C_PUSH
        elif curArr[0] in ARITHMETIC_OPS:
            return CommandType.C_ARITHMETIC
        elif curArr[0] == "pop":
            return CommandType.C_POP

    def getFirstArg(self, tp) -> str:
        if tp == CommandType.C_ARITHMETIC:
            return self.curArr[0]
        else:
            return self.curArr[1]

    def getSecondArg(self, tp) -> int:
        if tp == CommandType.C_PUSH or tp == CommandType.C_POP or tp == CommandType.C_FUNCTION or tp == CommandType.C_CALL:
            return int(self.curArr[2])


# writes the assembly code that implements the parsed command
class CodeWriter:
    def __init__(self, filename, parser) -> None:
        self.f = open(filename, "w")
        self.parser = parser
        self.idx = 0

    def writeArithmethic(self) -> None:
        parser = self.parser
        firstArg = parser.getFirstArg(CommandType.C_ARITHMETIC)
        if firstArg == "add":
            self.f.write(getBinOpCode("D=D+M"))
        elif firstArg == "sub":
            self.f.write(getBinOpCode("D=M-D"))
        elif firstArg == "neg":
            self.f.write(getUniOpCode("M=-D"))
        elif firstArg == "eq":
            self.f.write(getComparisonCode("D=D-M", "JEQ", self.idx))
            self.idx += 1
        elif firstArg == "gt":
            self.f.write(getComparisonCode("D=M-D", "JGT", self.idx))
            self.idx += 1
        elif firstArg == "lt":
            self.f.write(getComparisonCode("D=M-D", "JLT", self.idx))
            self.idx += 1
        elif firstArg == "and":
            self.f.write(getBinOpCode("D=D&M"))
        elif firstArg == "or":
            self.f.write(getBinOpCode("D=D|M"))
        elif firstArg == "not":
            self.f.write(getUniOpCode("M=!D"))

    def writePush(self, filename) -> None:
        parser = self.parser
        firstArg = parser.getFirstArg(tp)
        i = parser.getSecondArg(tp)
        if firstArg == "constant":
            self.f.write(f"@{i}\n")
            self.f.write("D=A\n@SP\nA=M\nM=D\n@SP\nM=M+1\n")
        elif firstArg == "local":
            self.f.write(f"@{i}\n")
            self.f.write(getMainSegPushCode("LCL"))
        elif firstArg == "argument":
            self.f.write(f"@{i}\n")
            self.f.write(getMainSegPushCode("ARG"))
        elif firstArg == "this":
            self.f.write(f"@{i}\n")
            self.f.write(getMainSegPushCode("THIS"))
        elif firstArg == "that":
            self.f.write(f"@{i}\n")
            self.f.write(getMainSegPushCode("THAT"))
        elif firstArg == "temp":
            self.f.write(f"@{i}\n")
            self.f.write(
                f"@{i}\nD=A\n@5\nD=D+A\nA=D\nD=M\n@SP\nA=M\nM=D\n@SP\nM=M+1\n")
        elif firstArg == "static":
            self.f.write(f"@{filename}.{i}\nD=M\n@SP\nA=M\nM=D\n@SP\nM=M+1\n")
        elif firstArg == "pointer":
            if i == 0:
                self.f.write(getPointerPushCode("THIS"))
            elif i == 1:
                self.f.write(getPointerPushCode("THAT"))

    def writePop(self, filename) -> None:
        parser = self.parser
        firstArg = parser.getFirstArg(tp)
        i = parser.getSecondArg(tp)
        if firstArg == "local":
            self.f.write(getMainSegPopCode("LCL", i))
        elif firstArg == "argument":
            self.f.write(getMainSegPopCode("ARG", i))
        elif firstArg == "this":
            self.f.write(getMainSegPopCode("THIS", i))
        elif firstArg == "that":
            self.f.write(getMainSegPopCode("THAT", i))
        elif firstArg == "temp":
            self.f.write(
                f"@{i}\nD=A\n@5\nD=D+A\n@i\nM=D\n@SP\nM=M-1\n@SP\nA=M\nD=M\n@i\nA=M\nM=D\n")
        elif firstArg == "static":
            self.f.write(f"@SP\nM=M-1\nA=M\nD=M\n@{filename}.{i}\nM=D\n")
        elif firstArg == "pointer":
            if i == 0:
                self.f.write(getPointerPopCode("THIS"))
            elif i == 1:
                self.f.write(getPointerPopCode("THAT"))


    def writeEnd(self) -> None:
        self.f.write("(INFINITE_LOOP)\n@INFINITE_LOOP\n0;JMP")

    def close(self) -> None:
        self.f.close()


if __name__ == "__main__":
    import sys, os
    filepath = sys.argv[1:][0]
    destpath = filepath.replace(".vm", ".asm")

    filename = os.path.basename(filepath)

    parser = Parser(sys.argv[1:][0])
    codeWriter = CodeWriter(destpath, parser)

    while parser.hasMoreLines():
        parser.advance()
        tp = parser.getCommandType()

        if tp == CommandType.C_ARITHMETIC:
            codeWriter.writeArithmethic()
        elif tp == CommandType.C_PUSH:
            codeWriter.writePush(filename[:-3])
        elif tp == CommandType.C_POP:
            codeWriter.writePop(filename[:-3])
    codeWriter.writeEnd()
    codeWriter.close()
