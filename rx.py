import os
import serial
import time

# Config Port
port = '/dev/pts/3'
ser = serial.Serial(port, timeout=3)

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

## Functions ##

# Calculate FCS
def calc_FCS(data):
    s = 0
    for c in data:
        s = s + ord(c)
    FCS = s % 256
    return chr(FCS)

# Save Data in File
def savefiile(full_data):
    with open(filename, 'a') as file:
        file.write(full_data)
        print "File " + filename + " saved with sucess!"

# Menu of RX
def menu(ser):
    while True:
        print "Welcome to program RX (XMODEM) port: " + port
        print "Choose:"
        print "1 - Recieve File"
        print "2 - Exit\n"
        options = int(input("Opt: "))
        if (int(options) == 1):
            break
        elif (int(options) == 2):
            quit()
        else:
            os.system('cls||clear')
            print 'Invalid Option. TRY AGAIN.\n'

def receivepackages(filename):
    # VARS
    full_data = ''      # String to save DATA 
    rec_SOH = chr(0)    # SET rec_SOH NULL
    SEQS = []           # SAVE SEQ in LIST
    count_naks = 0      # First NAK counter sent
    first = 1           # Used to treat the first SOH

    # Wait for the first SOH and send NAK
    while True:
        # NAK send
        os.system('cls||clear')
        print "Waiting for the file"
        ser.write(asc_NAK)
        ser.write(asc_NAK)
        # Counter of NAK Sent
        count_naks += 1
        print "NAK's sent: " + str(count_naks)

        # SOH read
        rec_SOH = ser.read(1)
        if rec_SOH == asc_SOH:
            break
        elif rec_SOH == asc_CAN:
            print 'Canceled.'
            quit()

    # Read the packages
    while rec_SOH != EOT:
        error = 0           # Var used to display errors

        # if it's the first time, don't read SOH again
        if first != 1:
            rec_SOH = ser.read(1)
        else:
            first = 0               # if first time, set first 0.

        # Check SOH
        if rec_SOH == asc_CAN:      # if read CAN, Cancel and quit.
            print 'Canceled.'
            quit()

        elif rec_SOH == asc_EOT:    # if is EOT, save file and quit.
            print '\nEOT received. Sending Last ACK'
            ser.write(asc_ACK)
            savefiile(full_data)
            break

        elif rec_SOH != asc_SOH:    # if received SOH isn't ASCII SOH, return error 1
            error = 1

        elif rec_SOH == asc_SOH:    # if received SOH is ASCII SOH, continue
            # Read SEQ
            rec_SEQ = ser.read(1)
            
            # Verify if package is duplicate, if it's duplicate, return error 2
            for SEQ in SEQS:
                if ord(rec_SEQ) == SEQ:
                    error = 2
            if error == 0:
                # Calculate ~SEQ with the SEQ received
                asc_CSEQ = chr(255 - ord(rec_SEQ))

                # Read ~SEQ
                rec_CSEQ = ser.read(1)

                # Compare received ~SEQ with calculated ~SEQ
                if rec_CSEQ != asc_CSEQ:
                    error = 3
                else:
                    # Read DATA
                    rec_data = ser.read(128)
                    
                    # Read FCS
                    rec_FCS = ser.read(1)

                    # Calculate FCS with DATA
                    asc_FCS = calc_FCS(rec_data)

                    # Compare received FCS with calculated FCS
                    if rec_FCS != asc_FCS:
                        error = 4

        # STATUS
        if error == 0:                          
            full_data = full_data + rec_data
            ser.write(asc_ACK)
            print 'Package ' + str(ord(rec_SEQ)) + ' recevied'
            SEQS.append(ord(rec_SEQ))
        elif error == 2:                        # SEQ DUPLICATE
            ser.read(130)
            ser.write(asc_ACK)
            print 'SEQ duplicate, sending ACK for the next package.'
        else:
            ser.write(asc_NAK)
            if error == 1:                      # SOH ERROR
                print 'Header invalid (SOH)'
                ser.read(131)
            if error == 3:                      # ~SEQ ERROR
                print '-SEQ invalid'
                ser.read(129)
            if error == 4:                      # FCS ERROR
                print 'Checksum fail'

#XMODEM RX
while True:
    os.system('cls||clear')
    menu(ser)

    os.system("cls||clear")
    filename = str(raw_input('Enter with name of file and extension: '))
    receivepackages(filename)

    # Wait for continue
    raw_input("Press Enter to continue...")