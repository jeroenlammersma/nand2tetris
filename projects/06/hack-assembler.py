#!usr/bin/python

import argparse
from platform import machine
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


class CInstruction():
  def __init__(self, instruction: str) -> None:
    self.instruction = instruction

  def __repr__(self) -> str:
    dest = DEST_TABLE[self.get_dest()]
    comp = COMP_TABLE[self.get_comp()]
    jump = JUMP_TABLE[self.get_jump()]
    return f'111{comp}{dest}{jump}'

  def get_dest(self) -> str:
    dest = self.instruction.split('=')[0] if self.has_dest() else 'null'
    return dest if dest == 'null' else ''.join(sorted(dest))

  def get_jump(self) -> str:
    return self.instruction.split(';')[1] if self.has_jump() else 'null'

  def has_dest(self) -> bool:
    return '=' in self.instruction

  def has_jump(self) -> bool:
    return ';' in self.instruction

  def get_comp(self) -> str:
    if self.has_dest() and self.has_jump():
      return self. instruction.split('=')[1].split(';')[0]
    if self.has_dest() and not self.has_jump():
      return self.instruction.split('=')[1]
    if not self.has_dest() and self.has_jump():
      return self.instruction.split(';')[0]
    return self.instruction


class InstructionTranslator():
  def translate_instruction(self, asm_instruction: str) -> str:
    if self._is_a_instruction(asm_instruction):
      return self._translate_a_instruction(asm_instruction)
    return self._translate_c_instruction(asm_instruction)

  def is_label_or_variable(self, instruction: str) -> bool:
    if not instruction.startswith('@'):
      return False
    value = instruction[1:]
    return value not in SYMBOL_TABLE and not value.isnumeric()

  def _is_a_instruction(self, instruction: str) -> bool:
    return instruction.startswith('@')

  def _translate_a_instruction(self, instruction: str) -> str:
    value = instruction[1:]
    if value in SYMBOL_TABLE:
      value = SYMBOL_TABLE[value]
    if value.isnumeric():
      return f'0{dec_to_bin(int(value))}'
    return value

  def _translate_c_instruction(self, instruction: str) -> str:
    return str(CInstruction(instruction))


class InstructionsTranslator():
  def __init__(self) -> None:
    self.translator = InstructionTranslator()

  def translate_instructions(self, asm_instructions: List[str]) -> List[str]:
    self._reset_variables()
    self._process_lines(asm_instructions)
    self._add_line_numbers_from_labels()
    self._assign_addresses_to_variables()
    return self.machine_instructions
  
  def _reset_variables(self) -> None:
    self.machine_instructions = []
    self.label_table = {}
    self.label_variable_set = set()
    self.line_number = 0

  def _process_lines(self, asm_instructions: List[str]) -> None:
    for line in asm_instructions:
      if not line or line.startswith('//'):  # skip empty lines and comments
        continue
      line = self._remove_comment(line)  # remove comment from line if present
      if line.startswith('('):
        self._add_label_to_table(line)
        continue
      machine_instruction = self.translator.translate_instruction(line)
      self.machine_instructions.append(machine_instruction)
      if self.translator.is_label_or_variable(line):
        self.label_variable_set.add(line[1:])
      self.line_number += 1

  def _remove_comment(self, line: str) -> str:
    if (where_comment := line.find('//')) != -1:
      return line[:where_comment].strip()
    return line

  def _add_label_to_table(self, line: str) -> None:
    label = line[1:-1]  # remove parentheses
    self.label_table[label] = self.line_number
  
  def _add_line_numbers_from_labels(self) -> None:
    for label, value in self.label_table.items():
      self._replace_label_or_variable_with_instruction(label, value)

  def _assign_addresses_to_variables(self) -> None:
    address = ADDRESS_SPACE_START
    for variable in self.label_variable_set:
      if variable in self.label_table.keys():
        continue
      if address > ADDRESS_SPACE_END:
        memory_limit_exceeded_exit()
      self._replace_label_or_variable_with_instruction(variable, address)
      address += 1
  
  def _replace_label_or_variable_with_instruction(self, name: str, value: int) -> None:
    machine_instruction = self.translator.translate_instruction(f'@{value}')
    indices = [i for i, line in enumerate(self.machine_instructions) if line == name]
    for i in indices:
      self.machine_instructions[i] = machine_instruction


def memory_limit_exceeded_exit() -> None:
  sys.exit("Program memory limit exceeded, aborting...")

def dec_to_bin(value: int) -> str:
  return format(value, '015b')

def get_file_path() -> str:
  parser = argparse.ArgumentParser()
  parser.add_argument('-f', '--File', help='Provide path to an Hack asm file')
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
  asm_instructions = read_file(file_path)
  machine_instructions = InstructionsTranslator().translate_instructions(asm_instructions)
  create_hack_file(file_path, machine_instructions)


if __name__ == '__main__':
  main()
