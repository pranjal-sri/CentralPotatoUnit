DATA R0
5
DATA R1
5
XOR R2 R2
(loop)
CLF
SHR R0 R0
JC
@ifadd
JMP
@skipadd
(ifadd)
CLF
ADD R1 R2
AND R0 R0
JZ
@end
(skipadd)
CLF
SHL R1 R1
JMP
@loop
(end)
END