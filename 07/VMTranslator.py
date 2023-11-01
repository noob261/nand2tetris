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
    return f"@SP\nAM=M-1\nD=M\n@SP\nAM=M-1\n{cond}\n@COND{idx}\nD;{op}\n@SP\nA=M\nM=0\n@SP\nM=M+1\n@ELSE{idx}\n0;JMP\n(COND{idx})\n@SP\nA=M\nM=-1\n@SP\nM=M+1\n(ELSE{idx})\n"


def getBinOpCode(op):
    return f"@SP\nM=M-1\nA=M\nD=M\n@SP\nM=M-1\nA=M\n{op}\n@SP\nA=M\nM=D\n@SP\nM=M+1\n"


def getUniOpCode(op):
    return f"@SP\nM=M-1\nA=M\nD=M\n@SP\nA=M\n{op}\n@SP\nM=M+1\n"


def getMainSegPushCode(seg):
    return f"D=A\n@{seg}\nD=D+M\nA=D\nD=M\n@SP\nA=M\nM=D\n@SP\nM=M+1\n"


def getMainSegPopCode(seg, i):
    return (
        f"@{i}\nD=A\n@{seg}\nD=D+M\n@i\nM=D\n@SP\nM=M-1\n@SP\nA=M\nD=M\n@i\nA=M\nM=D\n"
    )


def getPointerPushCode(base):
    return f"@{base}\nD=M\n@SP\nA=M\nM=D\n@SP\nM=M+1\n"


def getPointerPopCode(base):
    return f"@SP\nM=M-1\nA=M\nD=M\n@{base}\nM=D\n"


def getRestoreCode(idx, seg):
    return f"@{idx}\nD=A\n@R13\nA=M-D\nD=M\n@{seg}\nM=D\n"
    # return f"@{num}\nD=A\n@{argCnt}\nD=D+A\n@ARG\nA=M+D\nD=M\n@{seg}\nM=D\n"


def saveSegBeforeCall(seg):
    return f"@{seg}\nD=M\n@SP\nA=M\nM=D\n@SP\nM=M+1\n"


class CommandType(Enum):
    C_ARITHMETIC = 0
    C_PUSH = 1
    C_POP = 2
    C_FUNCTION = 3
    C_CALL = 4
    C_RETURN = 5
    C_LABEL = 6
    C_GOTO = 7
    C_IF = 8


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
                line = line[: line.index(COMMENT)]
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
        elif curArr[0] == "label":
            return CommandType.C_LABEL
        elif curArr[0] == "goto":
            return CommandType.C_GOTO
        elif curArr[0].startswith("if"):
            return CommandType.C_IF
        elif curArr[0] == "return":
            return CommandType.C_RETURN
        elif curArr[0] == "function":
            return CommandType.C_FUNCTION
        elif curArr[0] == "call":
            return CommandType.C_CALL

    def getFirstArg(self, tp) -> str:
        if tp == CommandType.C_ARITHMETIC:
            return self.curArr[0]
        else:
            return self.curArr[1]

    def getSecondArg(self, tp) -> int:
        if (
            tp == CommandType.C_PUSH
            or tp == CommandType.C_POP
            or tp == CommandType.C_FUNCTION
            or tp == CommandType.C_CALL
        ):
            return int(self.curArr[2])


# writes the assembly code that implements the parsed command
class CodeWriter:
    def __init__(self, filename, isDir) -> None:
        self.f = open(filename, "w")
        self.idx = 0
        self.retCounter = 0
        self.isDir = isDir
        if isDir:
            self.f.write("@261\nD=A\n@SP\nM=D\n")
            self.f.write("@Sys.init\n0;JMP\n")

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

    def writePush(self) -> None:
        parser = self.parser
        tp = CommandType.C_PUSH
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
            self.f.write(f"@{i}\nD=A\n@5\nD=D+A\nA=D\nD=M\n@SP\nA=M\nM=D\n@SP\nM=M+1\n")
        elif firstArg == "static":
            self.f.write(f"@{self.filename}.{i}\nD=M\n@SP\nA=M\nM=D\n@SP\nM=M+1\n")
        elif firstArg == "pointer":
            if i == 0:
                self.f.write(getPointerPushCode("THIS"))
            elif i == 1:
                self.f.write(getPointerPushCode("THAT"))

    def writePop(self) -> None:
        parser = self.parser
        tp = CommandType.C_POP
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
                f"@{i}\nD=A\n@5\nD=D+A\n@i\nM=D\n@SP\nM=M-1\n@SP\nA=M\nD=M\n@i\nA=M\nM=D\n"
            )
        elif firstArg == "static":
            self.f.write(f"@SP\nM=M-1\nA=M\nD=M\n@{self.filename}.{i}\nM=D\n")
        elif firstArg == "pointer":
            if i == 0:
                self.f.write(getPointerPopCode("THIS"))
            elif i == 1:
                self.f.write(getPointerPopCode("THAT"))

    def writeEnd(self) -> None:
        self.f.write("(INFINITE_LOOP)\n@INFINITE_LOOP\n0;JMP")

    def setFileName(self, filename) -> None:
        self.filename = filename

    def setParser(self, parser) -> None:
        self.parser = parser

    def writeLabel(self) -> None:
        label = self.parser.getFirstArg(CommandType.C_LABEL)
        self.f.write(f"({label})\n")

    def writeGoTo(self) -> None:
        label = self.parser.getFirstArg(CommandType.C_GOTO)
        self.f.write(f"@{label}\n0;JMP\n")

    def writeIf(self) -> None:
        label = self.parser.getFirstArg(CommandType.C_IF)
        self.f.write(f"@SP\nAM=M-1\nD=M\n@{label}\nD;JLT\n")

    def writeFunction(self) -> None:
        self.argCnt = self.parser.getSecondArg(CommandType.C_FUNCTION)
        self.f.write(f"({self.parser.getFirstArg(CommandType.C_FUNCTION)})\n")
        # push nVars 0 values (initializes the local variables to 0)
        if self.isDir and self.argCnt:
            self.f.write(
                f"@0\nD=A\n@i\nM=D\n@{self.argCnt}\nD=A\n@j\nM=D\n(LCL_LOOP${self.retCounter})\n@i\nD=M\n@j\nD=M-D\n@LCL_OUT_LOOP${self.retCounter}\nD;JEQ\n@0\nD=A\n@SP\nA=M\nM=D\n@SP\nM=M+1\n@i\nM=M+1\n@LCL_LOOP${self.retCounter}\n0;JMP\n(LCL_OUT_LOOP${self.retCounter})\n"
            )

    def writeCall(self) -> None:
        self.argCnt = self.parser.getSecondArg(CommandType.C_CALL)
        retLabel = f"{self.filename}$ret.{self.retCounter}"
        self.f.write(f"@{retLabel}\nD=A\n@SP\nA=M\nM=D\n@SP\nM=M+1\n")

        self.f.write(saveSegBeforeCall("LCL"))
        self.f.write(saveSegBeforeCall("ARG"))
        self.f.write(saveSegBeforeCall("THIS"))
        self.f.write(saveSegBeforeCall("THAT"))
        # ARG = SP – 5 – nArgs // Repositions ARG
        self.f.write(f"@5\nD=A\n@{self.argCnt}\nD=D+A\n@SP\nD=M-D\n@ARG\nM=D\n")
        # LCL = SP // Repositions LCL
        self.f.write("@SP\nD=M\n@LCL\nM=D\n")
        # Generates and pushes this label

        self.retCounter += 1
        # Transfers control to the callee
        funcName = self.parser.getFirstArg(CommandType.C_CALL)
        self.f.write(f"@{funcName}\n0;JMP\n")
        # Injects this label into the code
        self.f.write(f"({retLabel})\n")

    def writeReturn(self) -> None:
        # restore caller segment address
        # gets the address at the frame’s end
        self.f.write("@LCL\nD=M\n@R13\nM=D\n")
        # gets the return address
        self.f.write("@5\nD=A\n@R13\nA=M-D\nD=M\n@R14\nM=D\n")

        # set return value
        self.f.write("@SP\nM=M-1\nA=M\nD=M\n@ARG\nA=M\nM=D\n")
        # repositions SP
        self.f.write("@1\nD=A\n@ARG\nD=D+M\n@SP\nM=D\n")

        self.f.write(getRestoreCode(1, "THAT"))
        self.f.write(getRestoreCode(2, "THIS"))
        self.f.write(getRestoreCode(3, "ARG"))
        self.f.write(getRestoreCode(4, "LCL"))
        # jump return address
        self.f.write("@R14\nA=M\n0;JMP\n")

    def close(self) -> None:
        self.f.close()


# boostrap class
class Main:
    def translateSingleVm(self, codeWriter, parser):
        while parser.hasMoreLines():
            parser.advance()
            tp = parser.getCommandType()
            if tp == CommandType.C_ARITHMETIC:
                codeWriter.writeArithmethic()
            elif tp == CommandType.C_PUSH:
                codeWriter.writePush()
            elif tp == CommandType.C_POP:
                codeWriter.writePop()
            elif tp == CommandType.C_LABEL:
                codeWriter.writeLabel()
            elif tp == CommandType.C_IF:
                codeWriter.writeIf()
            elif tp == CommandType.C_GOTO:
                codeWriter.writeGoTo()
            elif tp == CommandType.C_RETURN:
                codeWriter.writeReturn()
            elif tp == CommandType.C_FUNCTION:
                codeWriter.writeFunction()
            elif tp == CommandType.C_CALL:
                codeWriter.writeCall()

    def translate(self):
        filepath = sys.argv[1]

        isFile = filepath.endswith(".vm")

        if isFile:
            destpath = filepath.replace(".vm", ".asm")
            parser = Parser(filepath)
            codeWriter = CodeWriter(destpath, False)
            codeWriter.setParser(parser)
            filename = os.path.basename(filepath)
            codeWriter.setFileName(filename[:-3])
            self.translateSingleVm(codeWriter, parser)
        else:
            dirname = filepath[filepath.rindex("\\") + 1 :]
            destpath = f"{filepath}\{dirname}.asm"
            codeWriter = CodeWriter(destpath, True)
            for entry in os.scandir(filepath):
                entryPath = entry.path
                if not entryPath.endswith(".vm"):
                    continue
                parser = Parser(entryPath)
                codeWriter.setParser(parser)
                filename = os.path.basename(entryPath)
                codeWriter.setFileName(filename[:-3])
                self.translateSingleVm(codeWriter, parser)

        # codeWriter.writeEnd()
        codeWriter.close()


if __name__ == "__main__":
    import sys
    import os

    main = Main()
    main.translate()
