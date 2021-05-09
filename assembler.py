import sys

REGS = {
    'R0' : '00',
    'R1' : '01',
    'R2' : '10',
    'R3' : '11',
}

ALU_INS = {
    'ADD' : '1000',
    'SUB' : '1001', 
    'SHR' : '1010',
    'SHL' : '1011',
    'NOT' : '1100',
    'OR'  : '1101',
    'AND' : '1110',
    'XOR' : '1111', 
}

MOV_INS = {
    'LD' : '0000',
    'ST' : '0001',
}

DATA_INS = {
    'DATA' : '001000',
}

JUMP_INS = {
    'JMPR' : '001100',
    'JMP'  : '01000000',
}

JMPFLGPREFIX = 'J'
JMPIF = '0101'

LABELFLGPREFIX = '('
LABELFLGSUFFIX = ')'
LABEL_FLAG = '@'

MISC_INS = {
    'CLF' : '01100000',
    'END' : '11001111'
}

ASSEMBLER_FLAGS = {
    '--debug' : 'DEBUG',
    '-D' : 'DEBUG',
}

class Assembler:
    def sanitise(self, f):
        sanitised = []
        for command in f:
            command = command.strip()
            if command[:2] == '//' or len(command) < 1:
                continue
            if command.find('//') != -1:
                command = command[:command.find('//')]
            sanitised.append(command)
        return sanitised

    def __init__(self):
        self.flags = {
            'DEBUG' : False
        }
        self.symbolTable = {}
        self.symbolLocs = {}
        self.filename = ''
        self.savename = ''
        for i in range(1, len(sys.argv)):
            if sys.argv[i] in ASSEMBLER_FLAGS.keys():
                self.flags[ASSEMBLER_FLAGS[sys.argv[i]]] = True
            elif not self.filename:
                self.filename = sys.argv[i]
            elif not self.savename:
                self.savename = sys.argv[i]
        if self.filename:
            try:
                f = open(self.filename).readlines()
            except:
                print(self.filename + ' does not exist.')
                sys.exit()
            self.file = self.sanitise(f)
            self.mcl = ['v2.0 raw\n']
        else:
            print("No input file given.")
            sys.exit()
    
    def BinToHex(self, binary):
        return hex(int(binary, 2))[2:]
    
    def HexToBin(self, hexadec):
        return bin(int(hexadec, 16))[2:]
    
    def DecToBin(self, decimal):
        decimal = int(decimal) % 256
        ans = bin(decimal)[2:]
        while len(ans) < 8:
            ans = '0' + ans
        return ans
    
    def toMachineCode(self):
        for command in self.file:
            mc = ""
            if self.flags['DEBUG']:
                print(command)
            
            command = command.split(' ')
            
            if self.flags['DEBUG']:
                print(command)
            
            if len(command) == 3:
                if command[0] in ALU_INS.keys():
                    mc += ALU_INS[command[0]]
                elif command[0] in MOV_INS.keys():
                    mc += MOV_INS[command[0]]
                mc += REGS[command[1]]
                mc += REGS[command[2]]
            
            elif len(command) == 2:
                if command[0] in JUMP_INS.keys():
                    mc += JUMP_INS[command[0]]
                
                elif command[0] in DATA_INS.keys():
                    mc += DATA_INS[command[0]]
                
                if len(mc) == 6:
                    mc += REGS[command[1]]
                
            elif len(command) == 1:
                if command[0] in MISC_INS.keys():
                    mc += MISC_INS[command[0]]
                
                if command[0] in JUMP_INS.keys():
                    mc += JUMP_INS[command[0]]

                elif command[0].startswith(JMPFLGPREFIX):
                    gezc = list('0000')
                    jmpflags = command[0][1:]
                    for f in jmpflags:
                        if f == 'G' or f == 'A':
                            gezc[0] = '1'
                        elif f == 'E':
                            gezc[1] = '1'
                        elif f == 'Z':
                            gezc[2] = '1'
                        elif f == 'C':
                            gezc[3] = '1'
                    mc += JMPIF + ''.join(gezc)
                
                elif command[0].startswith(LABELFLGPREFIX) and command[0].endswith(LABELFLGSUFFIX):
                    if self.flags['DEBUG']:
                        print()
                    command = command[0][1:-1].strip()
                    self.symbolTable[command] = len(self.mcl) - 1
                    continue
                
                elif command[0].startswith(LABEL_FLAG):
                    if command[0][1:] not in self.symbolLocs.keys():
                        self.symbolLocs[command[0][1:]] = []
                    self.symbolLocs[command[0][1:]].append(len(self.mcl))
                    mc += LABEL_FLAG

                elif command[0].isdigit():
                    mc += self.DecToBin(command[0])
                elif command[0].startswith('0b'):
                    mc += command[0][2:]
                    while len(mc) < 8:
                        mc = '0' + mc
                elif command[0].startswith('0x'):
                    mc += self.HexToBin(command[0][2:])
                    while len(mc) < 8:
                        mc = '0' + mc

            if self.flags['DEBUG']:
                print(mc[:len(mc)//2], mc[len(mc)//2:])
                if mc != LABEL_FLAG:
                    print(self.BinToHex(mc))
                print()
            
            if mc == LABEL_FLAG:
                self.mcl.append(mc + '\n')
            else:
                self.mcl.append(self.BinToHex(mc) + '\n')
        
        if self.flags['DEBUG']:
            print('Symbols Used : ')
        for sym in self.symbolLocs.keys():
            if self.flags['DEBUG']:
                print(sym + ' = ' + str(self.symbolTable[sym]))
                print('Indices : ')
            for ind in self.symbolLocs[sym]:
                if self.flags['DEBUG']:
                    print(ind)
                self.mcl[ind] = self.BinToHex(self.DecToBin(str(self.symbolTable[sym]))) + '\n'
            if self.flags['DEBUG']:
                print()
    
    def saveToFile(self):
        if not self.savename:
            file = open(self.filename[0:-4] + '.prg', 'w')
        else:
            file = open(self.savename, 'w')
        for mc in self.mcl:
            file.write(mc)
        file.close()

asm = Assembler()
asm.toMachineCode()
asm.saveToFile()