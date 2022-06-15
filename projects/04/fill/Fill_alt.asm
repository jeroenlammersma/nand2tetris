// This file is part of www.nand2tetris.org
// and the book "The Elements of Computing Systems"
// by Nisan and Schocken, MIT Press.
// File name: projects/04/Fill.asm

// Runs an infinite loop that listens to the keyboard input.
// When a key is pressed (any key), the program blackens the screen,
// i.e. writes "black" in every pixel;
// the screen should remain fully black as long as the key is pressed. 
// When no key is pressed, the program clears the screen, i.e. writes
// "white" in every pixel;
// the screen should remain fully clear as long as no key is pressed.

  // last = SCREEN + 8192
  @SCREEN
  D=A
  @8191
  D=D+A
  @last
  M=D
(WHITE)
  // if (KBD == 0) goto WHITE
  @KBD
  D=M
  @WHITE
  D;JEQ
  // address = SCREEN
  @SCREEN
  D=A
  @address
  M=D
(FILLBLACK)
  // RAM[address] = -1
  @address
  A=M
  M=-1
  // address = address + 1
  @address
  M=M+1
  // if (address <= last) goto FILLBLACK
  D=M
  @last
  D=D-M
  @FILLBLACK
  D;JLE
  // address = SCREEN
  @SCREEN
  D=A
  @address
  M=D
(BLACK)
  // if (KBD > 0) goto BLACK
  @KBD
  D=M
  @BLACK
  D;JGT
(FILLWHITE)
  // RAM[address] = 0
  @address
  A=M
  M=0
  // address = address + 1
  @address
  M=M+1
  // if (address <= last) goto FILLWHITE
  D=M
  @last
  D=D-M
  @FILLWHITE
  D;JLE
  // goto WHITE
  @WHITE
  0;JMP
