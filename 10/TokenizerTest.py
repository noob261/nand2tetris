from JackTokenizer import JackTokenizer, TokenType

if __name__ == "__main__":
    import sys, os
    filepath = sys.argv[1]
    jt = JackTokenizer(filepath)
    parts = filepath.split(os.sep)
    parts[-2] = f"My{parts[-2]}"
    i = parts[-1].index(".")
    parts[-1] = parts[-1][:i] + "T" + ".xml"
    outdir = os.path.join(*parts[:-1])
    
    if not os.path.exists(outdir):
        os.makedirs(outdir)

    with open(os.path.join(outdir, parts[-1]), "w+") as f:
        f.write("<tokens>\n")
        while jt.hasMoreTokens():
            jt.advance()
            tktp = jt.tokenType()
            if tktp == TokenType.KEYWORD:
                f.write(f"<keyword> {jt.symbol()} </keyword>")
            elif tktp == TokenType.SYMBOL:
                f.write(f"<symbol> {jt.symbol()} </symbol>")
            elif tktp == TokenType.IDENTIFIER:
                f.write(f"<identifier> {jt.identifier()} </identifier>")
            elif tktp == TokenType.INT_CONST:
                f.write(f"<integerConstant> {jt.intVal()} </integerConstant>")
            elif tktp == TokenType.STRING_CONST:
                f.write(f"<stringConstant> {jt.stringVal()[1:-1]} </stringConstant>")  
            f.write("\n")
        f.write("</tokens>\n")              