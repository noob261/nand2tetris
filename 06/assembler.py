import sys

filename = sys.argv[1:][0]

with open(filename) as f:
    lines = f.readlines()

#dest file name
destname = filename.replace(".asm", ".hack")

#asm specification
spec = {}
spec["0"] = "0101010";spec["1"] = "0111111";spec["-1"] = "0111010";spec["D"] = "0001100"
spec["A"] = "0110000";spec["M"] = "1110000";spec["!D"] = "0001101";spec["!A"] = "0110001"
spec["!M"] = "1110001";spec["-D"] = "0001111";spec["-A"] = "0110011";spec["-M"] = "1110011"
spec["D+1"] = "0011111";spec["A+1"] = "0110111";spec["M+1"] = "1110111";spec["D-1"] = "0001110"
spec["A-1"] = "0110010";spec["M-1"] = "1110010";spec["D-1"] = "0001110";spec["A-1"] = "0110010"
spec["M-1"] = "1110010";spec["D+A"] = "0000010";spec["D+M"] = "1000010";spec["D-A"] = "0010011"
spec["D-M"] = "1010011";spec["A-D"] = "0000111";spec["M-D"] = "1000111";spec["D&A"] = "0000000"
spec["D&M"] = "1000000";spec["D|A"] = "0010101";spec["D|M"] = "1010101"

#dest
dest = {}
dest[""] = "000";dest["M"] = "001";dest["D"] = "010";dest["DM"] = "011";dest["MD"] = "011"
dest["A"] = "100";dest["AM"] = "101";dest["AD"] = "110";dest["ADM"] = "111"

#jump
jump = {}
jump[""] = "000";jump["JGT"] = "001";jump["JEQ"] = "010";jump["JGE"] = "011"
jump["JLT"] = "100";jump["JNE"] = "101";jump["JLE"] = "110";jump["JMP"] = "111"

#symbol table
st = {}
#predefined symbol
for i in range(16): 
    s = str(i)
    st["R" + s] = s

st["SCREEN"] = "16384"
st["KBD"] = "24576"
st["SP"] = "0"
st["LCL"] = "1"
st["ARG"] = "2"
st["THIS"] = "3"
st["THAT"] = "4"

CPRE = "111"
COMMENT = "//"

#first pass
lineNum = 0
tmp = []
for line in lines:
    line = line.strip()
    if line.startswith(COMMENT) or not line: continue
    #remove inline comments
    if COMMENT in line:
        line = line[:line.index(COMMENT)]
        line = line.strip()
    #pseudocommand
    if line.startswith("("):
        st[line[1:-1]] = str(lineNum)
    else:
        lineNum += 1
        tmp.append(line)

lines = tmp

def decToBin(num):
    return bin(int(num, 10))[2:].zfill(16)

#next available address for variable
available = 16

with open(destname, "w") as f:
    for line in lines:
        #a
        if line.startswith("@"):
            a = line[1:]
            #check symbol
            if a.isdigit(): 
                f.write(decToBin(a) + "\n")
            else: #symbol
                if a not in st: 
                    #variable
                    st[a] = str(available)
                    available += 1
                f.write(decToBin(st[a]) + "\n")
        else: #c
            t1 = line.split("=")
            if len(t1) == 1:
                dst, compAndJmp = "", t1[0]
            else:
                dst, compAndJmp = t1
            dst = dst.strip(); compAndJmp = compAndJmp.strip()

            t2 = compAndJmp.split(";")
            if len(t2) == 1:
                cmp, jmp = t2[0], ""
            else:
                cmp, jmp = t2

            cmp = cmp.strip(); jmp = jmp.strip()
            f.write(CPRE + spec[cmp] + dest[dst] + jump[jmp] + "\n")
