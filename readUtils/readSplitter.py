""" split input reads file after each iteration of certain number of reads """
import sys
import os


class FASTQ_CONSTS:
    #FASTQ file extension
    FASTQ_EXT = '.fastq'

    
#split the passed read into different reads each containing some reads
def splitReads(ipReadName, splitThreshold):
    readCount = 0
    splitCount = 0
    currRead = []
    dirName = os.path.dirname(ipReadName)
    readName = os.path.basename(ipReadName).rstrip(FASTQ_CONSTS.FASTQ_EXT)
    opFileName = readName + '_' + str(splitCount) + FASTQ_CONSTS.FASTQ_EXT
    opFile = open(os.path.join(dirName, opFileName), 'w')
    with open(ipReadName, 'r') as ipRead:
        for line in ipRead:
            line = line.rstrip('\n')
            if line.startswith('@'):
                #header/ found a new read, write previous reads
                if len(currRead) > 0:
                    opFile.write('\n'.join(currRead))
                    opFile.write('\n')
                    readCount += 1
                    currRead = []
                if readCount >= splitThreshold:
                    #close current output file
                    opFile.close()
                    #increase the split count
                    splitCount += 1
                    #rest the readCount
                    readCount = 0
                    #open new file
                    opFileName = readName + '_' + str(splitCount) + FASTQ_CONSTS.FASTQ_EXT
                    opFile = open(os.path.join(dirName, opFileName), 'w')
            #append to current read details    
            currRead.append(line)
        #write the last read
        if len(currRead) > 0:
            opFile.write('\n'.join(currRead))
            opFile.write('\n')
            currRead = []
        #close current output file
        opFile.close()
            



def main():
    argLen = len(sys.argv)
    if argLen >= 2:
        ipReadName = sys.argv[1]
        splitThreshold = int(sys.argv[2])
        splitReads(ipReadName, splitThreshold)
    else:
        print 'err: less num of args passed'



if __name__ == '__main__':
    main()
