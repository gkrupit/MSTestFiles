// This file is part of www.nand2tetris.org
// and the book "The Elements of Computing Systems"
// by Nisan and Schocken, MIT Press.
// File name: projects/04/Mult.asm

// Multiplies R0 and R1 and stores the result in R2.
// (R0, R1, R2 refer to RAM[0], RAM[1], and RAM[2], respectively.)

@1
D=M
@i // iterator
M=D // RAM[i] = RAM[1]

@prod
M=0 // make sure product initialized to 0

(LOOP) // continue adding RAM[0] to prod until i == 0
    // if i == 0 goto END
    @i
    D=M
    @STOP
    D;JEQ

    @0
    D=M
    @prod
    M=D+M

    // i = i - 1
    @i
    M=M-1

    @LOOP
    0;JMP

(STOP)
    @prod
    D=M
    @2
    M=D

(END)
    @END
    0;JMP
