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
            return self.current_command.split()[1]

    def arg2(self):
        """ returns second argument of command """
        return self.current_command.split()[2]

class CodeWriter(object):

    def __init__(self, directory):
        self.outfile = open(os.path.join(directory, 'out.asm'), 'w')
        self.lineCount = 0
        self.startFile()

    def setFileName(self, filename):
        self.filename = os.path.basename(filename)[:-3]

    def write(self, arr):
        self.lineCount += len(arr)
        self.outfile.write('\n'.join(arr) + '\n')

    def startFile(self):
        """ initializes stack pointer """
        self.write([
            '@256',
            'D=A',
            '@SP',
            'M=D'
        ])

    def incrementSP(self):
        """ increments SP """
        self.write([
            '@SP',
            'M=M+1'
        ])

    def decrementSP(self):
        """ decrements SP """
        self.write([
            '@SP',
            'M=M-1'
        ])

    def DtoSP(self):
        """ puts contents of D register where SP is pointing """
        self.write([
            '@SP',
            'A=M',
            'M=D'
        ])

    def writeArithmetic(self, command):
        pass

    def writePushPop(self, command, segment, index):
        if command == 'push':
            if segment == 'constant':
                self.write([
                    '@%s' %index,
                    'D=A'
                ])
                self.DtoSP()
                self.incrementSP()

        else:
            pass


    def close(self):
        self.write(['@%s' %(1+self.lineCount), '0;JMP']) # infinite loop
        self.outfile.close()

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='VM Translator')
    parser.add_argument('vm', help='vm file or directory')
    args = parser.parse_args()

    files = []
    directory = ""
    if os.path.isdir(args.vm):    # if directory, get all .vm files
        directory = args.vm
        files = [os.path.join(directory, f) for f in os.listdir(args.vm) if f.endswith('.vm')]
    else:    # if not directory, append file name
        directory = os.path.dirname(args.vm)
        files.append(args.vm)

    cw = CodeWriter(directory)
    for f in files:
        p = Parser(f)
        cw.setFileName(f)
        while p.hasMoreCommands():
            p.advance()
            if p.commandType() == 'C_ARITHMETIC':
                cw.writeArithmetic(p.arg1())
            elif p.commandType() == 'C_PUSH':
                cw.writePushPop('push', p.arg1(), p.arg2())
            elif p.commandType() == 'C_POP':
                cw.writePushPop('pop', p.arg1(), p.arg2())

    cw.close()
