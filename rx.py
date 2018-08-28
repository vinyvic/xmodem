import os
import re
import serial
import time

# Config Port FOR /dev/pts/
port = 2
ser = serial.Serial('/dev/pts/' + str(port), timeout=5)

# DEFAULTS INTS VALUES
SOH = 0x01     #SOH -> Start of header character (decimal 1).
ACK = 0x06
NAK = 0x15
CAN = 0x18
EOT = 0x04     #EOT

# DEFAULT ASCII VALUES
asc_SOH  =   chr(SOH)
asc_ACK  =   chr(ACK)
asc_NAK  =   chr(NAK)
asc_EOT  =   chr(EOT)
asc_CAN  =   chr(CAN)

rec_SOH = chr(0)
#rec_SEQ
#rec_CSEQ
#rec_EOT
#rec_CAN
SEQS = []
error = 0
full_data = ''

def calc_FCS(data):
    s = 0
    for c in data:
        s = s + ord(c)
    FCS = s % 256
    return chr(FCS)

os.system("cls||clear")
filename = str(raw_input('Enter with name of file and extension: '))

def savefiile():
    with open(filename, 'a') as file:
        file.write(full_data)
        print "File " + filename + " saved with sucess!"

first = 1
sair = 1
os.system('cls||clear')
print "Aguardando Arquivo"

while first == 1 and sair == 1:
    ser.write(asc_NAK)
    rec_SOH = ser.read(1)
    if rec_SOH == asc_SOH:
        sair = 0
    elif rec_SOH == asc_EOT:
        print '\nEOT'
        exit()

while rec_SOH != EOT:
    if first != 1:
        rec_SOH = ser.read(1)
    else:
        first = 0
    if rec_SOH == asc_EOT:
        print '\nEOT'
        ser.write(asc_ACK)
        savefiile()
        exit()
    elif rec_SOH != asc_SOH:
        print 'SOH Header Error'
        error = 1
    first = 0
    rec_SEQ = ser.read(1)

    if rec_SEQ in SEQS:
        error = 2

    rec_CSEQ = ser.read(1)
    asc_CSEQ = chr(255 - ord(rec_SEQ))

    if rec_CSEQ != asc_CSEQ:
        error = 3

    rec_data = ser.read(128)
    rec_FCS = ser.read(1)
    asc_FCS = calc_FCS(rec_data)

    if rec_FCS != asc_FCS:
        error = 4
    
    if error == 0:
        full_data = full_data + rec_data
        ser.write(asc_ACK)
        print 'Package ' + str(ord(rec_SEQ)) + ' recevied'
        SEQS.append(rec_SEQ)
    else:
        ser.write(asc_NAK)
        if error == 1:
            print 'Header invalid (SOH)'
        if error == 2:
            print 'SEQ duplicate'
        if error == 3:
            print '-SEQ invalid'
        if error == 4:
            print 'Checksum fail'
