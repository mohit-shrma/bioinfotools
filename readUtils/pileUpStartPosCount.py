import sys
import os

class SAMConsts:

    #number of reads col
    NUM_READS_COL = 3

    


def countReadsAtEachPosition(pileUpFileName):
    with open(pileUpFileName, 'r') as pileUpFile:
        for pileUp in pileUpFile:
            

def main():
    argLen = len(sys.argv)
    if argLen >= 1:
        #passed pile up file
        pass
    else:
        print 'err: less num of args passed'

if __name__ == '__main__':
    main()
