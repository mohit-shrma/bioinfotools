import sys
import os

class SAMConsts:

    #position col
    POSITION_COL = 1
    
    #number of reads col
    NUM_READS_COL = 3

    #reads alignment pos style col
    ALIGN_POS_STYLE_COL = 4

    #reads start style
    START_STYLE = '^F'
    START_STYLE_FIRST = '^'
    START_STYLE_SECOND = 'F'

    #reads end style
    END_STYLE = '$'

    

def countReadsAtEachPosition(pileUpFileName):

    with open(pileUpFileName, 'r') as pileUpFile:

        print 'Position\tReadsCount\tStartCount\tEndCount\n' 

        for line in pileUpFile:

            cols = line.split()

            #position on reference
            position = cols[SAMConsts.POSITION_COL]

            #reads aligned style on this position
            alignReadsStyle = cols[SAMConsts.ALIGN_POS_STYLE_COL]

            #num reads
            numReads = cols[SAMConsts.NUM_READS_COL]
            
            #count of reads aligned with their start and end
            startCount = 0
            endCount = 0

            lastStart = False

            for readStyle in alignReadsStyle:
                if readStyle == SAMConsts.START_STYLE_FIRST:
                    #found beginning character of start
                    lastStart = True
                elif lastStart and \
                        readStyle == SAMConsts.START_STYLE_SECOND:
                    startCount += 1
                    lastStart = False
                elif readStyle == SAMConsts.END_STYLE:
                    endCount += 1
                    lastStart = False
                else:
                    lastStart = False
                    
            print position + '\t' + '\t' + numReads + '\t' +str(startCount) \
                + '\t' + str(endCount)
            

            
            
                    
                    
            

def main():
    argLen = len(sys.argv)
    if argLen >= 1:
        #passed pile up file
        pileupFileName = sys.argv[1]
        countReadsAtEachPosition(pileupFileName)
    else:
        print 'err: less num of args passed'

if __name__ == '__main__':
    main()
