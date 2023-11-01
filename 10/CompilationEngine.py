import xml.etree.ElementTree as ET
from typing import Type
from jackTokenizer import TokenType, JackTokenizer


def createChild(p, child, text):
    e = ET.SubElement(p, child)
    e.text = f" {text} "
    return e


def setDefault(p, child):
    e = ET.SubElement(p, child)
    e.text = "\n"
    return e


def setKw(p, text):
    return createChild(p, "keyword", text)


def setIdentifier(p, text):
    return createChild(p, "identifier", text)


def setSymbol(p, text):
    return createChild(p, "symbol", text)


class CompilationEngine:
    def __init__(self, jt: Type[JackTokenizer], outfilepath) -> None:
        self.jt = jt
        self.outfilepath = outfilepath
        self.root = ET.Element("class")
        self.tree = ET.ElementTree(self.root)
        self.statMap = {
            "let": self.compileLet,
            "if": self.compileIf,
            "while": self.compileWhile,
            "do": self.compileDo,
            "return": self.compileReturn,
        }

    def compileClass(self):
        jt = self.jt
        while jt.hasMoreTokens():
            jt.advance()
            tktp = jt.tokenType()
            if tktp == TokenType.KEYWORD:
                kw = jt.symbol()
                if kw == "static" or kw == "field":
                    self.compileClassVarDec(kw)
                elif kw == "function" or kw == "constructor" or kw == "method":
                    self.compileSubroutine(kw)
                else:
                    setKw(self.root, kw)
            elif tktp == TokenType.IDENTIFIER:
                setIdentifier(self.root, jt.identifier())
            elif tktp == TokenType.SYMBOL:
                setSymbol(self.root, jt.symbol())
        ET.indent(self.tree, space="  ", level=0)
        self.tree.write(self.outfilepath, short_empty_elements=False)

    def compileClassVarDec(self, kw):
        clsVarEle = setDefault(self.root, "classVarDec")
        setKw(clsVarEle, kw)
        while self.jt.hasMoreTokens():
            self.jt.advance()
            tktp = self.jt.tokenType()
            if tktp == TokenType.SYMBOL:
                symbol = self.jt.symbol()
                setSymbol(clsVarEle, symbol)
                if symbol == ";":
                    break
            elif tktp == TokenType.KEYWORD:
                setKw(clsVarEle, self.jt.keyWord())
            elif tktp == TokenType.IDENTIFIER:
                setIdentifier(clsVarEle, self.jt.identifier())

    def compileSubroutine(self, kw):
        subRoutineEle = setDefault(self.root, "subroutineDec")
        setKw(subRoutineEle, kw)
        while self.jt.hasMoreTokens():
            self.jt.advance()
            tktp = self.jt.tokenType()
            if tktp == TokenType.SYMBOL:
                symbol = self.jt.symbol()
                setSymbol(subRoutineEle, symbol)
                if symbol == "(":
                    self.compileParameterList(subRoutineEle)
                    setSymbol(subRoutineEle, ")")
                    self.compileSubroutineBody(subRoutineEle)
                    return
            elif tktp == TokenType.KEYWORD:
                setKw(subRoutineEle, self.jt.keyWord())
            elif tktp == TokenType.IDENTIFIER:
                setIdentifier(subRoutineEle, self.jt.identifier())

    def compileParameterList(self, p):
        plEle = setDefault(p, "parameterList")
        while self.jt.hasMoreTokens():
            self.jt.advance()
            tktp = self.jt.tokenType()
            if tktp == TokenType.SYMBOL:
                symbol = self.jt.symbol()
                if symbol == ")":
                    return
                else:
                    setSymbol(plEle, symbol)
            elif tktp == TokenType.KEYWORD:
                setKw(plEle, self.jt.keyWord())
            elif tktp == TokenType.IDENTIFIER:
                setIdentifier(plEle, self.jt.identifier())

    def compileSubroutineBody(self, p):
        srbEle = setDefault(p, "subroutineBody")
        while self.jt.hasMoreTokens():
            self.jt.advance()
            tktp = self.jt.tokenType()
            if tktp == TokenType.SYMBOL:
                symbol = self.jt.symbol()
                setSymbol(srbEle, symbol)
                if symbol != "{":
                    self.compileStatements(srbEle)
                    setSymbol(srbEle, "}")
                    return
            elif tktp == TokenType.KEYWORD:
                if self.jt.keyWord() == "var":
                    self.compileVarDec(srbEle)
                else:
                    self.compileStatements(srbEle)
                    setSymbol(srbEle, "}")
                    return

    def compileVarDec(self, p):
        varEle = setDefault(p, "varDec")
        setKw(varEle, "var")
        while self.jt.hasMoreTokens():
            self.jt.advance()
            tktp = self.jt.tokenType()
            if tktp == TokenType.IDENTIFIER:
                setIdentifier(varEle, self.jt.identifier())
            elif tktp == TokenType.KEYWORD:
                setKw(varEle, self.jt.keyWord())
            elif tktp == TokenType.SYMBOL:
                symbol = self.jt.symbol()
                setSymbol(varEle, symbol)
                if symbol == ";":
                    return

    def compileStatements(self, p):
        statEle = setDefault(p, "statements")
        cnt = 0
        while self.jt.hasMoreTokens():
            if not cnt:   #process vardec
                if self.jt.tokenType() != TokenType.KEYWORD:
                    self.jt.advance()
            else:
                self.jt.advance()
            cnt += 1
            tktp = self.jt.tokenType()
            if tktp == TokenType.KEYWORD:
                kw = self.jt.keyWord()
                self.statMap[kw](statEle)
            elif tktp == TokenType.SYMBOL:
                if self.jt.symbol() == "}":
                    return

    def compileLet(self, p):
        #'let' varName '=' expression ';’
        lsEle = setDefault(p, "letStatement")
        setKw(lsEle, "let")
        while self.jt.hasMoreTokens():
            self.jt.advance()
            tktp = self.jt.tokenType()
            if tktp == TokenType.IDENTIFIER:
                setIdentifier(lsEle, self.jt.identifier())
            elif tktp == TokenType.SYMBOL:
                symbol = self.jt.symbol()
                setSymbol(lsEle, symbol)
                if symbol == "=":
                    self.compileExpression(lsEle)
                    setSymbol(lsEle, ";")
                    return

    def compileIf(self, p):
        ifEle = setDefault(p, "ifStatement")
        setKw(ifEle, "if")
        while self.jt.hasMoreTokens():
            self.jt.advance()
            tktp = self.jt.tokenType()
            if tktp == TokenType.IDENTIFIER:
                setIdentifier(ifEle, self.jt.identifier())
            elif tktp == TokenType.SYMBOL:
                symbol = self.jt.symbol()
                setSymbol(ifEle, symbol)
                if symbol == "(":
                    self.compileExpression(ifEle)
                elif symbol == "{":
                    self.compileStatements(ifEle)
                    setSymbol(ifEle, "}")
                    #check if 'else' condition exists
                    if self.jt.peek() == "else":
                        self.jt.advance()
                        setKw(ifEle, self.jt.keyWord())
                        self.jt.advance()
                        setSymbol(ifEle, self.jt.symbol()) #{
                        self.compileStatements(ifEle)
                        setSymbol(ifEle, "}")
                    return


    def compileWhile(self, p):
        whileEle = setDefault(p, "whileStatement")
        setKw(whileEle, "while")
        while self.jt.hasMoreTokens():
            self.jt.advance()
            tktp = self.jt.tokenType()
            if tktp == TokenType.IDENTIFIER:
                setIdentifier(whileEle, self.jt.identifier())
            elif tktp == TokenType.SYMBOL:
                symbol = self.jt.symbol()
                setSymbol(whileEle, symbol)
                if symbol == "(":
                    self.compileExpression(whileEle)
                elif symbol == "{":
                    self.compileStatements(whileEle)
                    setSymbol(whileEle, "}")
                    return


    def compileDo(self, p):
        doEle = setDefault(p, "doStatement")
        setKw(doEle, "do")
        while self.jt.hasMoreTokens():
            self.jt.advance()
            tktp = self.jt.tokenType()
            if tktp == TokenType.IDENTIFIER:
                setIdentifier(doEle, self.jt.identifier())
            elif tktp == TokenType.SYMBOL:
                symbol = self.jt.symbol()
                setSymbol(doEle, symbol)
                if symbol == "(":
                    self.compileExpressionList(doEle)
                    setSymbol(doEle, ")")
                elif symbol == ";":
                    return

    def compileReturn(self, p):
        returnEle = setDefault(p, "returnStatement")
        setKw(returnEle, "return")
        self.jt.advance()
        if self.jt.symbol() != ";":
            self.compileExpression(returnEle, False)
        setSymbol(returnEle, ";")

    def compileExpression(self, p, flag=True):
        expEle = setDefault(p, "expression")
        self.compileTerm(expEle, flag)

    def compileTerm(self, p, flag):
        termEle = setDefault(p, "term")
        if flag:
            self.jt.advance()
        tktp = self.jt.tokenType()
        if tktp == TokenType.IDENTIFIER:
            setIdentifier(termEle, self.jt.identifier())
        elif tktp == TokenType.KEYWORD:
            setKw(termEle, self.jt.keyWord())

    def compileExpressionList(self, p) -> int:
        exprLsEle = setDefault(p, "expressionList")
        while self.jt.hasMoreTokens():
            self.jt.advance()
            tktp = self.jt.tokenType()
            if tktp == TokenType.IDENTIFIER or tktp == TokenType.KEYWORD:
                self.compileExpression(exprLsEle, False)
            elif tktp == TokenType.SYMBOL:
                if self.jt.symbol() == ")":
                    break
                else:
                    setSymbol(exprLsEle, self.jt.symbol())
