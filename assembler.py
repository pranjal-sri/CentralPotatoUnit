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

MISC_INS = {
    'CLF' : '01100000',
    'END' : '11001111'
}

class Assembler:
    def sanitise(self, f):
        sanitised = []
        for command in f:
            # command = command.replace(' ', '')
            while command.startswith(' '):
                command = command[1:]
            command = command.replace('\t', '')
            command = command.replace('\n', '')
            command = command.replace('\r', '')
            if command[:2] == '//' or len(command) < 1:
                continue
            if command.find('//') != -1:
                command = command[:command.find('//')]
            sanitised.append(command)
        return sanitised

    def __init__(self):
        self.filename = sys.argv[1] 
        f = open(self.filename).readlines()
        self.file = self.sanitise(f)
        self.mcl = ['v2.0 raw\n']
    
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
            print(command)
            command = command.split(' ')
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

            print(mc[:4], mc[4:])
            print(self.BinToHex(mc))
            print()
            self.mcl.append(self.BinToHex(mc) + '\n')
    
    def saveToFile(self):
        file = open(self.filename[0:-4] + '.prg', 'w')
        for mc in self.mcl:
            file.write(mc)
        file.close()

asm = Assembler()
asm.toMachineCode()
asm.saveToFile()