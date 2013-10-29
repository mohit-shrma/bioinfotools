""" split reads for each dir, ending with '/1' in other and '/2' in other"""
import sys
import os
from multiprocessing import Pool
import multiprocessing, logging


class FASTQ_CONSTS:
    #FASTQ file extension
    FASTQ_EXT = '.fasta'

    #First dir prefix
    READ1_PRE = '/1'

    #First dir prefix
    READ2_PRE = '/2'


        
#get all fastqs inside a dir
def getFastqFilePaths(fastqDir):
    #contained all fastqs
    fastqFilePaths = []
    for fileName in os.listdir(fastqDir):
            fastqPath = os.path.join(fastqDir, fileName)
            if os.path.isfile(fastqPath) and\
                    fileName.endswith(FASTQ_CONSTS.FASTQ_EXT):
                fastqFilePaths.append(fastqPath)
    return fastqFilePaths


    

def readSplitter((ipReadName, read1OpName, read2OpName)):
    with open(ipReadName, 'r') as ipFile, open(read1OpName, 'w') as opRead1,\
            open(read2OpName, 'w') as opRead2:
        isCurrRead1 = False
        isCurrRead2 = False
        for line in ipFile:
            if isCurrRead1:
                opRead1.write(line)
                isCurrRead1 = False
            elif isCurrRead2:
                opRead2.write(line)
                isCurrRead2 = False
            elif line.endswith(FASTQ_CONSTS.READ1_PRE + '\n'):
                opRead1.write(line)
                isCurrRead1 = True
            elif line.endswith(FASTQ_CONSTS.READ2_PRE + '\n'):
                opRead2.write(line)
                isCurrRead2 = True
            else:
                print 'Err: none of the conditions satisfied in split reads',\
                    ipReadName
                return -1
        return 1

    
def callReadSplitters(ipReadsDir):

    #get all reads
    #dirContents = os.listdir(ipReadsDir)

    reads = getFastqFilePaths(ipReadsDir)

    #initialize pool with number of possible jobs
    pool = Pool(processes=len(reads))
    workersArgs = []

    for read in reads:
        readName = read.rstrip(FASTQ_CONSTS.FASTQ_EXT)
        opRead1 = os.path.join(ipReadsDir, readName + '_1' + FASTQ_CONSTS.FASTQ_EXT)
        opRead2 = os.path.join(ipReadsDir, readName + '_2' + FASTQ_CONSTS.FASTQ_EXT)
        workersArgs.append((read, opRead1, opRead2))
        
    #for each read and fasta create a job
    """for read in dirContents:
        ipRead = os.path.join(ipReadsDir, read)
        opRead1 = os.path.join(ipReadsDir, read+'_1.fasta')
        opRead2 = os.path.join(ipReadsDir, read+'_2.fasta')
        workersArgs.append((ipRead, opRead1, opRead2))"""
        
    results = pool.map(readSplitter, workersArgs)
    pool.close()
    pool.join()
    return results



def main():

    logger = multiprocessing.log_to_stderr()
    logger.setLevel(multiprocessing.SUBDEBUG)

    if len(sys.argv) >= 1:
        #directory containing "ONLY" reads
        readsDir = sys.argv[1]
        
        #split the reads inside dir
        results = callReadSplitters(readsDir)

        print results
    else:
        print 'err: files missing'


if __name__ == '__main__':
    main()

