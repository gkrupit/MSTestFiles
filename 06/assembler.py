#!/usr/bin/env python
import argparse
import re

symbols = {
    # 'R0': '0', 'R1': '1', 'R2': '2',
    # 'R3': '3', 'R4': '4', 'R5': '5',
    # 'R6': '6', 'R7': '7', 'R8': '8',
    # 'R9': '9', 'R10': '10', 'R11': '11',
    # 'R12': '12', 'R13': '13', 'R14': '14',
    # 'R15': '15', 'SCREEN': '16384', 'KBD': '24576',
    # 'SP': '0', 'LCL': '1', 'ARG': '2', 'THIS': '3', 'THAT': '4',
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
        # @Word or (WORD)
        patterns = re.compile(r'(?<=\@)([a-zA-Z]+)|(?<=\()([a-zA-Z]+)').search(line)

        # convert symbol if it already exists
        # else, add to dictionary and convert
        if patterns:
            if patterns.group() in symbols:
                lines[i] = "@%s" % symbols[patterns.group()]
            else:
                symbols[patterns.group()] = str(i)
                lines[i] = "@%s" % symbols[patterns.group()]

    return lines

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Hack Assembler')
    parser.add_argument('asm', help='asm file')
    args = parser.parse_args()

    with open(args.asm) as handle:
        # strip whitespace and ignore comments
        lines = [line.split("//")[0].strip() for line in handle if line.split("//")[0].strip()]
        first_pass(lines)
