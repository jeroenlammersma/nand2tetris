#!usr/bin/python

import argparse
import sys
from typing import List


COMP_TABLE = {
  '0':   '0101010',
  '1':   '0111111',
  '-1':  '0111010',
  'D':   '0001100',
  'A':   '0110000',
  'M':   '1110000',
  '!D':  '0001101',
  '!A':  '0110001',
  '!M':  '1110001',
  '-D':  '0001111',
  '-A':  '0110011',
  '-M':  '1110011',
  'D+1': '0011111',
  'A+1': '0110111',
  'M+1': '1110111',
  'D-1': '0001110',
  'A-1': '0110010',
  'M-1': '1110010',
  'D+A': '0000010',
  'D+M': '1000010',
  'D-A': '0010011',
  'D-M': '1010011',
  'A-D': '0000111',
  'M-D': '1000111',
  'D&A': '0000000',
  'D&M': '1000000',
  'D|A': '0010101',
  'D|M': '1010101',
}

DEST_TABLE = {
  'null': '000',
  'M':    '001',
  'D':    '010',
  'DM':   '011',
  'A':    '100',
  'AM':   '101',
  'AD':   '110',
  'ADM':  '111'
}

JUMP_TABLE = {
  'null': '000',
  'JGT':  '001',
  'JEQ':  '010',
  'JGE':  '011',
  'JLT':  '100',
  'JNE':  '101',
  'JLE':  '110',
  'JMP':  '111'
}

SYMBOL_TABLE = {
  'R0':     '0', 
  'R1':     '1',
  'R2':     '2',
  'R3':     '3',
  'R4':     '4',
  'R5':     '5',
  'R6':     '6',
  'R7':     '7',
  'R8':     '8',
  'R9':     '9', 
  'R10':    '10',
  'R11':    '11',
  'R12':    '12',
  'R13':    '13',
  'R14':    '14',
  'R15':    '15',
  'SCREEN': '16384',
  'KBD':    '24576',
  'SP':     '0',
  'LCL':    '1',
  'ARG':    '2',
  'THIS':   '3',
  'THAT':   '4',
}

# address space for variables
ADDRESS_SPACE_START = 16   # min
ADDRESS_SPACE_END = 16383  # max

UNDEFINED_VARIABLES_TABLE = {}  # key: variable name, value: list of line numbers


class CInstruction():
  def __init__(self, instruction: str) -> None:
    self.instruction = instruction
  
  def get_machine_code(self) -> str:
    return self.__repr__()

  def __repr__(self) -> str:
    dest = DEST_TABLE[self._get_dest()]
    comp = COMP_TABLE[self._get_comp()]
    jump = JUMP_TABLE[self._get_jump()]
    return f'111{comp}{dest}{jump}'

  def _get_dest(self) -> str:
    dest = self.instruction.split('=')[0] if self._has_dest() else 'null'
    return dest if dest == 'null' else ''.join(sorted(dest))

  def _get_jump(self) -> str:
    return self.instruction.split(';')[1] if self._has_jump() else 'null'

  def _has_dest(self) -> bool:
    return '=' in self.instruction

  def _has_jump(self) -> bool:
    return ';' in self.instruction

  def _get_comp(self) -> str:
    if self._has_dest() and self._has_jump():
      return self. instruction.split('=')[1].split(';')[0]
    if self._has_dest() and not self._has_jump():
      return self.instruction.split('=')[1]
    if not self._has_dest() and self._has_jump():
      return self.instruction.split(';')[0]
    return self.instruction


class InstructionsParser():
  def __init__(self) -> None:
    self._reset_variables()

  def _reset_variables(self) -> None:
    self._machine_instructions = []
    self._line_number = 0

  def parse_lines(self, lines: List[str]) -> List[str]:
    for line in lines:
      if not line or line.startswith('//'):  # skip empty lines and comments
        continue
      line = self._remove_comment(line)  # remove comment from line if present
      if line.startswith('('):
        self._handle_label(line, self._line_number)
        continue
      machine_instruction = parse_instruction(line, self._line_number)
      self._machine_instructions.append(machine_instruction)
      self._line_number += 1
    self._process_undefined_variables()
    return self._machine_instructions

  def _remove_comment(self, line: str) -> str:
    if (where_comment := line.find('//')) != -1:
      return line[:where_comment].strip()
    return line
    
  def _handle_label(self, line: str, line_number: int) -> None:
    label = line[1:-1]  # remove parentheses
    self._add_label_to_symbol_table(label, line_number)
    self._process_label_through_undefined(label)
  
  def _add_label_to_symbol_table(self, label: str, line_number: int) -> None:
    SYMBOL_TABLE[label] = str(line_number)
  
  def _process_label_through_undefined(self, label: str) -> None:
    if label not in UNDEFINED_VARIABLES_TABLE:
      return
    for line_number in UNDEFINED_VARIABLES_TABLE[label]:
      value = int(SYMBOL_TABLE[label])
      self._machine_instructions[line_number] = to_a_instruction(value)
    UNDEFINED_VARIABLES_TABLE.pop(label, None)  # remove label from table
  
  def _process_undefined_variables(self) -> None:
    address = ADDRESS_SPACE_START
    for variable in UNDEFINED_VARIABLES_TABLE.values():
      if address > ADDRESS_SPACE_END:
        memory_limit_exceeded_exit()
      for line_number in variable:
        self._machine_instructions[line_number] = to_a_instruction(address)
      address += 1


def parse_instruction(line: str, line_number: int) -> str:
  if line.startswith('@'):
    return parse_a_instruction(line, line_number)
  return parse_c_instruction(line)

def parse_a_instruction(line: str, line_number: int) -> str:
  value = line[1:]
  if value in SYMBOL_TABLE:
    value = SYMBOL_TABLE[value]
  if value.isnumeric():
    return to_a_instruction(int(value))
  UNDEFINED_VARIABLES_TABLE.setdefault(value,[]).append(line_number)
  return value

def to_a_instruction(value: int) -> str:
  return f'0{dec_to_bin(value)}'

def dec_to_bin(value: int) -> str:
  return format(value, '015b')

def parse_c_instruction(line: str) -> str:
  return CInstruction(line).get_machine_code()

def memory_limit_exceeded_exit() -> None:
  sys.exit("Program memory limit exceeded, aborting...")

def get_file_path() -> str:
  parser = argparse.ArgumentParser()
  parser.add_argument('-f', '--File', required=True, help='path to asm source file')
  args = parser.parse_args()
  return args.File

def create_hack_file(file_path: str, lines: List[str]) -> None:
  hack_file = file_path.replace('.asm', '.hack')
  with open(hack_file, 'w') as file:
    [file.write('%s\n' % line) for line in lines]
  print(f'ASM to HACK translation successful...\nFile created: {hack_file}')

def read_file(file_path: str) -> List[str]:
  with open(file_path, 'r') as file:
    lines = [line.strip() for line in file]
  return lines

def main():
  file_path = get_file_path()
  lines = read_file(file_path)
  machine_instructions = InstructionsParser().parse_lines(lines)
  create_hack_file(file_path, machine_instructions)


if __name__ == '__main__':
  main()
