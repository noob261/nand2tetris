from enum import Enum
from typing import Type

DOUBLE_QUOTE = "\""
COMMENTS = ("/*", "/**", "//", "*")
SYMBOLS = ["{", "}", "(", ")", "[", "]", ".", ",", ";",
           "+", "-", "*", "/", "&", "|", "<", ">", "=", "~"]
KEYWORDS = ["class", "constructor", "function", "method", "field", "static", "var", "int", "char", "boolean", "void",
            "true", "false", "null", "this", "let", "do", "if", "else", "while", "return"]
XML_ESCAPE = {"<": "&lt;", ">": "&gt;", "\"": "&quot;", "&": "&amp;"}


class KeyWord(Enum):
    CLASS = 1
    METHOD = 2
    FUNCTION = 3
    CONSTRUCTOR = 4
    INT = 5
    BOOLEAN = 6
    CHAR = 7
    VOID = 8
    VAR = 9
    STATIC = 10
    FIELD = 11
    LET = 12
    DO = 13
    IF = 14
    ELSE = 15
    WHILE = 16
    RETURN = 17
    TRUE = 18
    FALSE = 19
    NULL = 20
    THIS = 21


class TokenType(Enum):
    KEYWORD = 1
    SYMBOL = 2
    IDENTIFIER = 3
    INT_CONST = 4
    STRING_CONST = 5


KEYWORD_MAP = dict(zip(KEYWORDS, list(KeyWord)))


class JackTokenizer:
    def __init__(self, filepath) -> None:
        with open(filepath) as f:
            self.lines = f.readlines()
        self.lines = self._trim(self.lines)
        self.tokens = self._tokenize()

    def _trim(self, lines) -> Type[list]:
        tmp = []

        for line in lines:
            line = line.strip()
            if line.startswith(COMMENTS) or not line:
                continue
            # remove inline comments
            for comment in COMMENTS:
                if comment in line:
                    line = line[:line.index(comment)]
                    line = line.strip()
            tmp.append(line)
        return tmp

    def _tokenize(self) -> Type[list]:
        tokens = []
        for line in self.lines:
            i = j = 0
            while i < len(line):
                quote = False
                cur = []
                while j < len(line):
                    # string constant
                    if quote:
                        cur.append(line[j])
                        # quote end
                        if line[j] == DOUBLE_QUOTE:
                            j += 1
                            break
                    else:
                        # space
                        if line[j] == " ":
                            j += 1
                            break
                        # symbol
                        if line[j] in SYMBOLS:
                            #append single symbol
                            if not cur:
                                cur.append(line[j])
                                j += 1
                            break
                        cur.append(line[j])
                        # quote start
                        if line[j] == DOUBLE_QUOTE:
                            quote = True
                    j += 1
                if cur:
                    tokens.append("".join(cur))
                i = j
        return tokens

    def hasMoreTokens(self) -> bool:
        return len(self.tokens) != 0

    def advance(self) -> None:
        self.curToken = self.tokens.pop(0)

    def tokenType(self) -> Type[TokenType]:
        tk = self.curToken
        if tk.isdigit():
            return TokenType.INT_CONST

        if tk.startswith(DOUBLE_QUOTE) and tk.endswith(DOUBLE_QUOTE):
            return TokenType.STRING_CONST

        if tk in SYMBOLS:
            return TokenType.SYMBOL

        if tk in KEYWORDS:
            return TokenType.KEYWORD

        return TokenType.IDENTIFIER

    def keyWord(self) -> Type[KeyWord]:
        return KEYWORD_MAP[self.curToken]

    def symbol(self) -> str:
        return XML_ESCAPE.get(self.curToken, self.curToken)

    def identifier(self) -> str:
        return self.curToken

    def intVal(self) -> int:
        return int(self.curToken)

    def stringVal(self) -> str:
        return self.curToken
    

# if __name__ == "__main__":
#     jt = JackTokenizer(r"E:\coding\myproject\courses\nand2tetris\projects\10\ArrayTest\Main.jack")
#     while jt.hasMoreTokens():
#         jt.advance()
#         print(jt.symbol())
