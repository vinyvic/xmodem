import os
import re
import serial
import time

# Config Port FOR /dev/pts/
port = '/dev/pts/2'
ser = serial.Serial(port)

# DEFAULTS INTS VALUES FOR TRANSMISSION
SOH = 0x01     #SOH -> Start of Header
ACK = 0x06     #ACK -> OK (Acknowledge)
NAK = 0x15     #NAK -> NOT OK (not Acknowledge)
CAN = 0x18     #CAN -> Cancel
EOT = 0x04     #EOT -> End of Transmission

# ASCII VALUES FOR TRANSMISSION
asc_SOH  =   chr(SOH)
asc_ACK  =   chr(ACK)
asc_NAK  =   chr(NAK)
asc_EOT  =   chr(EOT)
asc_CAN  =   chr(CAN)

# OTHER VARS
SUB = chr(0x1A) #SUB -> Character for fill DATA, when this is lower than 128 bytes.

## Functions ##

# Slipt string in peaces of 128 bits
def splitString(string):
    return [string[i:i+128] for i in range(0, len(string), 128)]
    
# Get Text of File
def getFileText(filename):
	with open(filename, 'r') as file:
		text = file.read()
	return splitString(text)

# Calculate FCS
def calc_FCS(data):
    s = 0
    for c in data:
        s = s + ord(c)
    FCS = s % 256
    print "FCS -> " + str(FCS)
    return chr(FCS)

# Menu of TX
def menu(ser):
    while True:
        print "Welcome to program TX (XMODEM) port:" + port
        print "Choose:"
        print "1 - Send File"
        print "2 - Exit\n"
        options = int(input("Opt: "))
        if (int(options) == 1):
            break
        elif (int(options) == 2):
            quit()
        else:
            os.system('cls||clear')
            print 'Invalid Option. TRY AGAIN.\n'

# SEND PACKAGE
def sendpackages(DATAFULL):
    # Count for packages of 128 bytes
    SEQ = 0x01                      # SEQ -> one byte sequence number which starts at 1, and increments by one until it reaches 255 and then wraps around to zero.
    NAKS_count = 0                  # NAKS COUNT
    
    # send one package for each 128 bytes of data
    for DATA in DATAFULL:
        CSEQ = 255 - SEQ            # ~SEQ
        asc_SEQ  =   chr(SEQ)       # transform SEQ in ASCII
        asc_CSEQ =   chr(CSEQ)      # transform ~SEQ in ASCII
        RESP = asc_NAK              # Set RESP (Response) with NAK, to enter in while

        # Wait receiver send FIRST NAK
        if SEQ == 1:
            os.system('cls||clear')
            while True:
                print "blocks to send: " + str(len(DATAFULL))
                print "Waiting First NAK..."
                RESP = ser.read(1)
                if RESP == asc_NAK:
                    break
                os.system('cls||clear')

        while (RESP == asc_NAK):
            # ---- #
            # Send SOH
            ser.write(chr(SOH))   
            print "SOH sent!"
            ser.reset_input_buffer()        # Reset Buffer, to avoid FIRST NACKS

            # Send SEQ and -SEQ
            ser.write(chr(SEQ))
            print "SEQ sent! package: " + str(hex(SEQ))
            ser.write(chr(CSEQ))
            print "-SEQ sent! value: " + str(hex(CSEQ))

            # ---- #
            #DATA -> 128, 8 bit bytes of data.
            if len(DATA) < 128:
                for i in range (len(DATA),  128):
                    DATA += SUB
            
            print "DATA: '" + DATA + "' -> Size: " + str(len(DATA))
            ser.write (DATA)  # SEND DATA

            # ---- #
            #FCS -> one byte sum of all of the data bytes
            asc_FCS = calc_FCS(DATA)

            ser.write(asc_FCS)  # SEND FCS 
            total = len(asc_SOH) + len(asc_SEQ) + len(asc_CSEQ) + len(DATA) + len(asc_FCS)
            print "TOTAL: " + str(total) + " bytes sent"

            # Get Status
            print "\nWaiting for Response"
            RESP = ser.read(1)
            if RESP == asc_ACK:
                print "Package sent sucessfully\n"
            elif RESP == asc_NAK:
                print "Failed to send package\n"
                NAKS_count += 1
                if NAKS_count >= 30:
                    print 'Alot of erros in response, try again.'
                    exit()
            elif RESP == asc_CAN:
                print "Canceled\n"
                quit()

                
            print "\n--------------------------"
            print "--------------------------\n"
        SEQ += 1

# XMODEM TX
while True:
    os.system('cls||clear')
    menu(ser)

    # Open file
    os.system('cls||clear')
    filename = str(raw_input('Enter the file name and extension: '))
    DATAFULL = getFileText(filename)

    # Send Packages
    sendpackages(DATAFULL)

    # SEND EOT
    RESP = asc_NAK
    print "Sending EOT, waiting for Last ACK!\n"

    while (RESP == asc_NAK):
        ser.write(asc_EOT)
        RESP = ser.read(1)
        if RESP == asc_ACK:
            print "File uploaded successfully!\n"
        elif RESP == asc_NAK:
            print "Failed to send the EOT, trying again.\n"
        elif RESP == asc_CAN:
            print "Canceled\n"
            quit()


    # Wait for continue
    raw_input("Press Enter to continue...")
    os.system('cls||clear')