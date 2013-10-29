import sys
import os
from multiprocessing import Pool
import multiprocessing, logging

from readSplitter import splitReads


#get all fastqs inside a dir
def getFastqFilePaths(fastqDir):
    #contained all fastqs
    fastqFilePaths = []
    for fileName in os.listdir(fastqDir):
            fastqPath = os.path.join(fastqDir, fileName)
            if os.path.isfile(fastqPath) and\
                    fileName.endswith('fastq'):
                fastqFilePaths.append(fastqPath)
    return fastqFilePaths



#split the read after each split threshold
def callReadSplitter((fastqPath, splitThreshold)):
    print 'calling reads splitter: ', fastqPath
    splitReads(fastqPath, splitThreshold)

    

#execute read splitting of reads in passed dir
def execReadSplittingTasks(ipReadsDir, splitThreshold):

    #get all fastqs
    fastqFilePaths = getFastqFilePaths(ipReadsDir)
    print 'fastqFilePaths: ', fastqFilePaths 
    
    #get number of processors
    numProcs = multiprocessing.cpu_count()
    print 'number of cpus: ', numProcs

    #compute number of jobs
    numJobs = len(fastqFilePaths)

    #initialize pool with number of possible jobs
    pool = Pool(processes=min(numJobs, numProcs))
    workersArgs = []

    #for each read create a task
    for fastqPath in fastqFilePaths:
        workersArgs.append((fastqPath, splitThreshold))

    #execute the concurrent tasks    
    pool.map(callReadSplitter, workersArgs)

    pool.close()
    pool.join()
    


def main():

    logger = multiprocessing.log_to_stderr()
    logger.setLevel(multiprocessing.SUBDEBUG)

    argLen = len(sys.argv)
    if argLen >= 2:
        ipReadsDir = sys.argv[1]
        splitThreshold = int(sys.argv[2]) #generally 25Million reads for 5Gb
        execReadSplittingTasks(ipReadsDir, splitThreshold)
    else:
        print 'err: less num of args passed'


if __name__ == '__main__':
    main()
