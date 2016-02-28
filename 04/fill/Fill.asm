// This file is part of www.nand2tetris.org
// and the book "The Elements of Computing Systems"
// by Nisan and Schocken, MIT Press.
// File name: projects/04/Fill.asm

// Runs an infinite loop that listens to the keyboard input.
// When a key is pressed (any key), the program blackens the screen,
// i.e. writes "black" in every pixel. When no key is pressed, the
// program clears the screen, i.e. writes "white" in every pixel.

(KLISTEN) // listens to keyboard and dictates screen fill
    @8191
    D=A
    @i
    M=D // set i to 8191 (last screen register)

    @KBD
    D=M // record key press

    @FILLSCREEN
    D;JGT // goto FILLSCREEN if key is pressed

    @RESETSCREEN
    0;JMP // goto RESETSCREEN if key is not pressed

(FILLSCREEN) // fills all pixels (black screen)
    @i
    D=M
    @KLISTEN
    D;JLT // exit loop if i < 0

    @SCREEN
    D=A
    @i
    A=D+M // find address of next register
    M=-1 // fill in full register

    @i
    M=M-1

    @FILLSCREEN
    0;JMP

(RESETSCREEN) // resets all pixels (white screen)
    @i
    D=M
    @KLISTEN
    D;JLT // exit loop if i < 0

    @SCREEN
    D=A
    @i
    A=D+M // find address of next register
    M=0 // reset full register

    @i
    M=M-1

    @RESETSCREEN
    0;JMP
