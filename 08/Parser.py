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
    mem_segment = {'local': 'LCL', 'argument': 'ARG', 'this': 'THIS', 'that': 'THAT', 'pointer': 3, 'temp': 5}
    operations = {'add': '+', 'sub': '-', 'and': '&', 'or': '|', 'neg': '-',
                  'not': '!', 'eq': 'JEQ', 'lt': 'JLT', 'gt': 'JGT'}
    nums = []
    labelnum = 0
    labelsDelivered = 0

    def __init__(self, directory, filename):
        self.outfile = open(os.path.join(directory, filename), 'w')
        self.lineCount = 0
        self.startFile()

    def setFileName(self, filename):
        self.fileName = os.path.basename(filename)[:-3]

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
        # self.writeCall('Sys.init', 0)

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
            'M=M-1',
            'A=M'
        ])

    def DtoSP(self):
        """ puts contents of D register where SP is pointing """
        self.write([
            '@SP',
            'A=M',
            'M=D'
        ])

    def writeLabel(self, label):
        """  just makes a label marker  """
        self.write([
            '(%s)' %label
        ])

    def writeGoTo(self, label):
        """  unconditional jumping to a specified label  """
        self.write([
            '@%s' %label,
            '0;JMP'
        ])
        self.labelsDelivered += 1

    def writeIf(self, label):
        """  if the statement isn't 0 it will jump to a label  """
        self.decrementSP()
        self.write([
            'D=M',
            '@%s' %label,
            'D;JNE'
        ])
        self.labelsDelivered += 1

    def writeCall(self, funcName, numArgs):
        """  Calling a function  """
        offset = int(numArgs) + 5    # how many args will it be taking? (needs at least 5)
        returnLabel = 'return%s%d' %(funcName, self.labelnum)    #creates unique return label
        self.labelnum += 1
        # sets up return label
        self.write([
            '@%s' %returnLabel,
            'D=A',
            '@SP',
            'A=M',
            'D=M'
        ])
        self.incrementSP()
        # sets up the base addresses of the segments
        for segment in ('LCL', 'ARG', 'THIS', 'THAT'):
            self.write([
                '@%s' %segment,
                'D=M',
                '@SP',
                'A=M',
                'M=D'
            ])
        self.write([   #moves ARG and LCL to accomidate the offset
            '@SP',
            'D=M',
            '@%d' %offset,
            'D=D-A',
            '@ARG',
            'M=D',
            '@SP',
            'D=M',
            '@LCL',
            'M=D'
        ])
        self.writeGoTo(funcName)
        self.writeLabel(returnLabel)

    def writeReturn(self): # super long....
        pass

    def writeFunction(self, funcName, nums):
        self.writeLabel(funcName)
        # set initial variables to 0
        for _ in range(int(nums)):
            self.write([
                '@SP',
                'A=M',
                'M=0'
            ])
            self.incrementSP()
            self.labelsDelivered += 1

    def writeArithmetic(self, command):
        if command in ('add', 'sub', 'and', 'or'):
            self.decrementSP()
            self.write([
                'D=M'
            ])
            self.decrementSP()
            self.write([
                'D=M%sD' %self.operations[command],
                'M=D'
            ])
        elif command in ('neg', 'not'):
            self.decrementSP()
            self.write([
                'D=M',
                'D=%sD' %self.operations[command],
                'M=D'
            ])
        # we need to create unique labels for each label.
        # if true execute to one label
        # if false execute to another label
        elif command in ('eq', 'gt', 'lt'):
            true = 'TruthLabel%s' %self.labelnum
            false = 'FalseLabel%s' %self.labelnum
            self.labelnum += 1
            self.decrementSP()
            self.write([
                'D=M'
            ])
            self.decrementSP()
            # A > D => D > 0
            # A < D => D < 0
            # A = D => D = 0
            self.write([
                'D=M-D',
                '@%s' %true,
                'D;%s' %self.operations[command],
                '@SP',
                'A=M',
                'M=0',
            ])
            # stores 0 for false
            self.write([
                '@%s' %false,
                '0;JMP'
            ])
            # create the command for the truth value (-1) to be stored
            self.write([
                '(%s)'%true,
                '@SP',
                'A=M',
                'M=-1',
            ])
            # skips the saving the truth value being stored
            # continues reading the vm
            self.write([
                '(%s)' %false
            ])
            self.labelsDelivered += 2
        self.incrementSP()

    def writePushPop(self, command, segment, index):
        if command == 'push':
            if segment == 'constant':
                self.write([
                    '@%s' %index,
                    'D=A'
                ])
                self.nums.append(int(index))
            elif segment in ('temp','pointer'):
                self.write([
                    '@%d' %(self.mem_segment[segment] + int(index)),
                    'D=M'
                ])
            elif segment == 'static':
                self.write([
                    '@%s' %(self.fileName + '.' + index),
                    'D=M'
                ])
            else:
                self.write([
                    '@%s' %self.mem_segment[segment],
                    'D=M',
                    '@%s' %index,
                    'A=D+A',
                    'D=M'
                ])
            self.DtoSP()
            self.incrementSP()
        else:
            if segment in ('temp','pointer','static'):
                write_index = ''
                if segment == 'static':
                    write_index = self.fileName + '.' + index
                else:
                    write_index = self.mem_segment[segment] + int(index)
                self.write([
                    '@%s' %write_index,
                    'D=A',
                    '@13',
                    'M=D'
                ])
            else:
                self.write([
                    '@%s' %self.mem_segment[segment],
                    'D=M',
                    '@%s' %index,
                    'D=D+A',
                    '@13',
                    'M=D'
                ])
            self.decrementSP()
            self.write([
                'D=M',
                '@13',
                'A=M',
                'M=D'
            ])

    def close(self):
        self.write(['@%s' %(self.lineCount-self.labelsDelivered), '0;JMP']) # infinite loop
        self.outfile.close()

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='VM Translator')
    parser.add_argument('vm', help='vm file or directory')
    args = parser.parse_args()

    files = []
    directory = ""
    if os.path.isdir(args.vm):    # if directory, get all .vm files
        directory = args.vm
        outfile = os.path.realpath(directory).split('/')[-1] + '.asm'
        files = [os.path.join(directory, f) for f in os.listdir(args.vm) if f.endswith('.vm')]
    else:    # if not directory, append file name
        directory = os.path.dirname(args.vm)
        outfile = args.vm.split('/')[-1][:-3] + '.asm'
        files.append(args.vm)

    cw = CodeWriter(directory, outfile)
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
            elif p.commandType() == 'C_LABEL':
                cw.writeLabel(p.arg1())
            elif p.commandType() == 'C_GOTO':
                cw.writeGoTo(p.arg1())
            elif p.commandType() == 'C_IF':
                cw.writeIf(p.arg1())
            elif p.commandType() == 'C_FUNCTION':
                cw.writeFunction(p.arg1(),p.arg2())
            elif p.commandType() == 'C_RETURN':
                cw.writeReturn()
            elif p.commandType() == 'C_CALL':
                cw.writeCall(p.arg1(), p.arg2())
    cw.close()
