+
@SP
M=M-1
A=M
D=M
@SP
M=M-1
A=M
D=D+M
@SP
A=M
M=D
@SP
M=M+1

-
@SP
M=M-1
A=M
D=M
@SP
M=M-1
A=M
D=M-D
@SP
A=M
M=D
@SP
M=M+1

-y
@SP
M=M-1
A=M
D=M
@SP
A=M
M=-D
@SP
M=M+1

x==y
@SP
M=M-1
D=M
M=M-1
D=D-M
@COND
D;JEQ
@SP
M=0
M=M+1
(COND)
@SP
M=-1
M=M+1

x>y
@SP
M=M-1
D=M
M=M-1
D=D-M
@COND
D;JGT
@SP
M=0
M=M+1
(COND)
@SP
M=-1
M=M+1


x<y
@SP
M=M-1
D=M
M=M-1
D=D-M
@COND
D;JLT
@SP
M=0
M=M+1
(COND)
@SP
M=-1
M=M+1

x&y
@SP
M=M-1
D=M
M=M-1
D=M-D
M=D
M=M+1


//push local i
@i
D=A
@LCL
D=D+M
A=D
D=M
@SP
A=M
M=D
@SP
M=M+1

//pop local i

@i
D=A
@LCL
D=D+M
@i
M=D
@SP
M=M-1
@SP
A=M
D=M
@i
A=M
M=D

//push temp i
@i
D=A
@5
D=D+A
A=D
D=M
@SP
A=M
M=D
@SP
M=M+1


//pop temp i
@i
D=A
@5
D=D+A
@i
M=D
@SP
A=M
D=M
@i
A=M
M=D
@SP
M=M-1