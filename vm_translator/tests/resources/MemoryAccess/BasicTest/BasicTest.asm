// Instruction: MemoryInstruction(command='push', segment='constant', index='10')
@10
D=A
@SP
A=M
M=D
@SP
M=M+1
// Instruction: MemoryInstruction(command='pop', segment='local', index='0')
@LCL
D=M
@0
D=D+A
@R13
M=D
@SP
AM=M-1
D=M
@R13
A=M
M=D
// Instruction: MemoryInstruction(command='push', segment='constant', index='21')
@21
D=A
@SP
A=M
M=D
@SP
M=M+1
// Instruction: MemoryInstruction(command='push', segment='constant', index='22')
@22
D=A
@SP
A=M
M=D
@SP
M=M+1
// Instruction: MemoryInstruction(command='pop', segment='argument', index='2')
@ARG
D=M
@2
D=D+A
@R13
M=D
@SP
AM=M-1
D=M
@R13
A=M
M=D
// Instruction: MemoryInstruction(command='pop', segment='argument', index='1')
@ARG
D=M
@1
D=D+A
@R13
M=D
@SP
AM=M-1
D=M
@R13
A=M
M=D
// Instruction: MemoryInstruction(command='push', segment='constant', index='36')
@36
D=A
@SP
A=M
M=D
@SP
M=M+1
// Instruction: MemoryInstruction(command='pop', segment='this', index='6')
@THIS
D=M
@6
D=D+A
@R13
M=D
@SP
AM=M-1
D=M
@R13
A=M
M=D
// Instruction: MemoryInstruction(command='push', segment='constant', index='42')
@42
D=A
@SP
A=M
M=D
@SP
M=M+1
// Instruction: MemoryInstruction(command='push', segment='constant', index='45')
@45
D=A
@SP
A=M
M=D
@SP
M=M+1
// Instruction: MemoryInstruction(command='pop', segment='that', index='5')
@THAT
D=M
@5
D=D+A
@R13
M=D
@SP
AM=M-1
D=M
@R13
A=M
M=D
// Instruction: MemoryInstruction(command='pop', segment='that', index='2')
@THAT
D=M
@2
D=D+A
@R13
M=D
@SP
AM=M-1
D=M
@R13
A=M
M=D
// Instruction: MemoryInstruction(command='push', segment='constant', index='510')
@510
D=A
@SP
A=M
M=D
@SP
M=M+1
// Instruction: MemoryInstruction(command='pop', segment='temp', index='6')
@R5
D=A
@6
D=D+A
@R13
M=D
@SP
AM=M-1
D=M
@R13
A=M
M=D
// Instruction: MemoryInstruction(command='push', segment='local', index='0')
@LCL
D=M
@0
A=D+A
D=M
@SP
A=M
M=D
@SP
M=M+1
// Instruction: MemoryInstruction(command='push', segment='that', index='5')
@THAT
D=M
@5
A=D+A
D=M
@SP
A=M
M=D
@SP
M=M+1
// Instruction: ArithmeticInstruction(command='add')
@SP
AM=M-1
D=M
A=A-1
M=M+D
// Instruction: MemoryInstruction(command='push', segment='argument', index='1')
@ARG
D=M
@1
A=D+A
D=M
@SP
A=M
M=D
@SP
M=M+1
// Instruction: ArithmeticInstruction(command='sub')
@SP
AM=M-1
D=M
A=A-1
M=M-D
// Instruction: MemoryInstruction(command='push', segment='this', index='6')
@THIS
D=M
@6
A=D+A
D=M
@SP
A=M
M=D
@SP
M=M+1
// Instruction: MemoryInstruction(command='push', segment='this', index='6')
@THIS
D=M
@6
A=D+A
D=M
@SP
A=M
M=D
@SP
M=M+1
// Instruction: ArithmeticInstruction(command='add')
@SP
AM=M-1
D=M
A=A-1
M=M+D
// Instruction: ArithmeticInstruction(command='sub')
@SP
AM=M-1
D=M
A=A-1
M=M-D
// Instruction: MemoryInstruction(command='push', segment='temp', index='6')
@R5
D=A
@6
A=D+A
D=M
@SP
A=M
M=D
@SP
M=M+1
// Instruction: ArithmeticInstruction(command='add')
@SP
AM=M-1
D=M
A=A-1
M=D+M
