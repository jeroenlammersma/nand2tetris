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
  // color = 0
  @color
  M=0
(WHITE)
  // if (KBD == 0) goto WHITE
  @KBD
  D=M
  @WHITE
  D;JEQ
  // color = -1
  @color
  M=-1
  // goto FILL
  @FILL
  0;JMP
(BLACK)
  // if (KBD > 0) goto BLACK
  @KBD
  D=M
  @BLACK
  D;JGT
  // color = 0
  @color
  M=0
(FILL)
  // address = SCREEN
  @SCREEN
  D=A
  @address
  M=D
(FILL_LOOP)
  // RAM[address] = color
  @color
  D=M
  @address
  A=M
  M=D
  // address = address + 1
  @address
  M=M+1
  // if (address <= last) goto FILL
  D=M
  @last
  D=D-M
  @FILL_LOOP
  D;JLE
  // if (color == 0) goto WHITE
  @color
  D=M
  @WHITE
  D;JEQ
  // else goto BLACK
  @BLACK
  0;JMP
