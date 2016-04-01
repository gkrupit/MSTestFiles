#!/usr/bin/env python
import argparse
import os

class Parser(object):

    commands = {'add':'C_ARITHMETIC', 'sub':'C_ARITHMETIC', 'neg':'C_ARITHMETIC',
                'eq' :'C_ARITHMETIC', 'gt' :'C_ARITHMETIC', 'lt' :'C_ARITHMETIC',
                'and':'C_ARITHMETIC', 'or' :'C_ARITHMETIC', 'not':'C_ARITHMETIC',
                'push':'C_PUSH', 'pop':'C_POP', 'label':'C_LABEL', 'goto':'C_GOTO',
                'if-goto':'C_IF', 'function':'C_FUNCTION', 'return':'C_RETURN', 'call':'C_CALL'}

    def __init__(self, filename):
        with open(filename) as handle:
            """ strips whitespace, ignores comments """
            self.lines = [line.split("//")[0].strip() for line in handle if line.split("//")[0].strip()]

    def hasMoreCommands(self):
        return self.lines != []

    def advance(self):
        """ advances to the next line """
        self.current_command = self.lines.pop(0)

    def commandType(self):
        """ defines command types according to instruction """
        return self.commands[self.current_command.split()[0]]

    def arg1(self):
        """ returns first argument of command """
        if self.commandType() == 'C_ARITHMETIC':
            return self.current_command
        else:
            return self.current_command.split()[0]

    def arg2(self):
        return self.current_command.split()[1]

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='VM Translator')
    parser.add_argument('vm', help='vm file or directory')
    args = parser.parse_args()

    files = []
    if args.vm.endswith('/'):    # get all .vm files if directory is specified
        files = [args.vm + f for f in os.listdir(args.vm) if f.endswith('.vm')]
    else:
        files.append(args.vm)

    for f in files:
        p = Parser(f)
        while p.hasMoreCommands():
            p.advance()
            print p.commandType()
