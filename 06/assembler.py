#!/usr/bin/env python
import argparse
import re

"""
    *** HOW TO RUN ***
    To run, type: python assembler.py name_of_asm.asm

    The program will output a .hack file in the current directory
    with the same name as the name of the .asm file given as an argument
"""

symbols = {
    'R0': '0', 'SP': '0', 'R1': '1', 'LCL': '1',
    'R2': '2', 'ARG':'2', 'R3': '3', 'THIS': '3',
    'R4': '4', 'THAT': '4', 'R5': '5',
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
    'D-M' : '010011',
    'M-D' : '000111',
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

def remove_labels(lines):
    """ removes all label symbols """

    labels_removed = []
    line_num = 0    # keep track of instruction number. ignore if a label symbol
    for i, line in enumerate(lines):
        patterns = re.search(r'\((\S+)\)', line)    # (WORD)
        if patterns:
            if patterns.group(1) not in symbols:
                symbols[patterns.group(1)] = str(line_num)
        else:
            labels_removed.append(line)
            line_num += 1

    return labels_removed

def define_variables(lines):
    """ defines all variables by converting to addresses """

    var_address = 16    # start defining variables at address 16
    for i, line in enumerate(lines):
        if line.startswith("@") and not line.strip("@").isdigit():
            if line.strip('@') not in symbols:
                symbols[line.strip('@')] = str(var_address)
                lines[i] = "@%s" % symbols[line.strip('@')]
                var_address += 1
            else:
                lines[i] = "@%s" % symbols[line.strip('@')]

    return lines

def c_instruction(line):
    """ builds C instruction based on predefined dictionaries """

    a = ''
    comp = ''
    dst = '000'
    jmp = '000'

    if ';' in line:
        spl = line.split(';')
        jmp = jump[spl[1]]
        line = spl[0]

    if '=' in line:
        comp_dest = line.split('=')
        dst = dest[comp_dest[0]]
        line = comp_dest[1]

    if line in comp_a0:
        comp = comp_a0[line]
        a = '0'
    else:
        comp = comp_a1[line]
        a = '1'

    return '111' + a + comp + dst + jmp    # C instructions always start with 111

def translate(lines):
    """ translates each line to 16-bit binary string """

    instructions = []
    for i, line in enumerate(lines):
        if line.startswith("@"):    # handles A instructions
            instructions.append('0{0:015b}'.format(int(line.strip("@"))))
        else:                       # handles C instructions
            instructions.append(c_instruction(line))

    return instructions

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Hack Assembler')
    parser.add_argument('asm', help='asm file')
    args = parser.parse_args()

    outfile = args.asm[:-3] + 'hack'
    lines = []
    with open(args.asm) as handle:
        """ strips whitespace, ignores comments """
        lines = [line.split("//")[0].strip() for line in handle if line.split("//")[0].strip()]

    lines = remove_labels(lines)
    lines = define_variables(lines)
    lines = translate(lines)

    with open(outfile, 'w') as out:
        for line in lines:
            out.write(line + '\n')
