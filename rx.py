import serial

# Config Port
ser = serial.Serial('/dev/pts/1')

# Get SOH
SOH = ser.read(1)
if (SOH != chr(0x01)):
    if (SOH == chr(0x04)):
        print "--EOT--"
    else:
        print "SOH not valid"
    quit()
print "SOH: " + hex(ord(SOH))

# Get SEQ
SEQ = ser.read(1)
print "SEQ: " + hex(ord(SEQ))

# Get -SEQ
CSEQ = ser.read(1)
print "CSEQ: " + hex(ord(CSEQ))

# Get DATA
DATA = ser.read(128)
print "DATA: " + DATA + " -> Size: " + str(len(DATA))

# Get FCS
FCS = ser.read(1)
print "FCS: " + FCS