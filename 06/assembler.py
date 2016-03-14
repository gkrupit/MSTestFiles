#!/usr/bin/env python
import argparse
import re

symbols = {
    'R0': '0', 'R1': '1', 'R2': '2',
    'R3': '3', 'R4': '4', 'R5': '5',
    'R6': '6', 'R7': '7', 'R8': '8',
    'R9': '9', 'R10': '10', 'R11': '11',
    'R12': '12', 'R13': '13', 'R14': '14',
    'R15': '15', 'SCREEN': '16384', 'KBD': '24576',
    'SP': '0', 'LCL': '1', 'ARG': '2', 'THIS': '3', 'THAT': '4',
}

comp_a0 = {
    '0'   : '101010',
    '1'   : '111111',
    '-1'  : '111010',
    'D'   : '001100',
    'A'   : '110000',
    '!D'  : '001101',
    '!A'  : '110001',
    '-D'  : '001111',
    '-A'  : '110011',
    'D+1' : '011111',
    'A+1' : '110111',
    'D-1' : '001110',
    'A-1' : '110010',
    'D+A' : '000010',
    'D-A' :'010011',
    'A-D' :'000111',
    'D&A' : '000000',
    'D|A' : '010101',
}

comp_a1 = {
    'M'   : '110000',
    '!M'  : '110001',
    '-M'  : '110011',
    'M+1' : '110111',
    'M-1' : '110010',
    'D+M' : '000010',
    'D-M' :'010011',
    'M-D' :'000111',
    'D&M' : '000000',
    'D|M' : '010101',
}

jump = {
    'JGT': '001', 'JEQ': '010', 'JGE': '011',
    'JLT': '100', 'JNE': '101', 'JLE': '110', 'JMP': '111',
}

dest = {
    'M': '001', 'D': '010', 'MD': '011',
    'A': '100', 'AM': '101', 'AD': '110', 'AMD': '111',
}

def first_pass(lines):
    """ converts all symbols to numbers """

    for i, line in enumerate(lines):
        patterns = re.compile(r'(?<=\@)([a-zA-Z]+)|(?<=\()([a-zA-Z]+)').search(line) # @Word or (WORD)
        if patterns:
            if patterns.group() in symbols:         # convert symbol if it already exists
                lines[i] = "@%s" % symbols[patterns.group()]
            else:
                symbols[patterns.group()] = str(i)  # else, add to dictionary and conver
                lines[i] = "@%s" % symbols[patterns.group()]

    return lines

def translate(lines):
    """ translates each line to binary """

    for i, line in enumerate(lines):
        if line.startswith("@"):    # handles A instructions
            lines[i] = '0' + '{0:015b}'.format(int(line.strip("@")))

    # if no @, it is a C instruction
    # if C instruction, parse according to predefined dictionaries
    return lines

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Hack Assembler')
    parser.add_argument('asm', help='asm file')
    args = parser.parse_args()

    lines = []
    with open(args.asm) as handle:
        """ strips whitespace, ignores comments """
        lines = [line.split("//")[0].strip() for line in handle if line.split("//")[0].strip()]

    binary = translate(lines)
