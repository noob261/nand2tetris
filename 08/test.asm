//label pop from stack and cmp
@SP
M=M-1
A=M
D=M
@LABEL
D;JGT

//set return value
@SP
M=M-1
A=M
D=M
@ARG
M=D
//jump return address
@1
D=A
@ARG
D=D+M
@SP
M=D
//restore caller segment address
@1
D=A
@2
D=D+A
@ARG
A=M+D
D=M
@LCL
M=D
@2
D=A
@2
D=D+A
@ARG
D=D+M
M=D
@3
D=A
@2
D=D+A
@THIS
D=D+M
M=D
@4
D=A
@2
D=D+A
@THAT
D=D+M
M=D


//call
//save...
@LCL
D=M
@SP
A=M
M=D
@SP
M=M+1

//ARG = SP – 5 – nArgs // Repositions ARG
@5
D=A
@argCnt
D=D+A
@SP
A=M
D=M-D
@ARG
M=D


//push nVars 0 values
@0
D=A
@i
M=D
@nVars
D=A
@j
M=D
(LCL_LOOP$0)
@i
D=M
@j
D=D-M
@(LCL_OUT_LOOP$0)
D;JEQ
@0
D=A
@LCL
A=M
M=D
@LCL
M=M+1
@(LCL_LOOP$0)
0;JMP
(LCL_OUT_LOOP$0)


//restore by LCL
@LCL
D=M
@R13
M=D

@1
D=A
@R13
A=M-D
D=M
@THAT
M=D

