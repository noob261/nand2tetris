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

    def getFirstArg(self, tp) -> str:
        if tp == CommandType.C_ARITHMETIC:
            return self.curArr[0]
        else:
            return self.curArr[1]

    def getSecondArg(self, tp) -> int:
        if tp == CommandType.C_PUSH or tp == CommandType.C_POP or tp == CommandType.C_FUNCTION or tp == CommandType.C_CALL:
            return self.curArr[2]


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

    def writePushPop(self) -> None:
        parser = self.parser
        if parser.getFirstArg(tp) == "constant":
            i = parser.getSecondArg(tp)
            self.f.write(f"@{i}\n")
            self.f.write("D=A\n@SP\nA=M\nM=D\n@SP\nM=M+1\n")

    def writeEnd(self) -> None:
        self.f.write("(INFINITE_LOOP)\n@INFINITE_LOOP\n0;JMP")

    def close(self) -> None:
        self.f.close()


if __name__ == "__main__":
    import sys
    filename = sys.argv[1:][0]
    destname = filename.replace(".vm", ".asm")

    parser = Parser(sys.argv[1:][0])
    codeWriter = CodeWriter(destname, parser)

    while parser.hasMoreLines():
        parser.advance()
        tp = parser.getCommandType()

        if tp == CommandType.C_ARITHMETIC:
            codeWriter.writeArithmethic()
        elif tp == CommandType.C_PUSH:
            codeWriter.writePushPop()
    codeWriter.writeEnd()
    codeWriter.close()
