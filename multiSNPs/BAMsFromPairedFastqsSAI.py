""" will find the bam file for paired reads, assuming already SAI are generated
using bwa   """
import sys
import os
from multiprocessing import Pool
import multiprocessing, logging

import workerForBam


""" returns the mismatch count b/w two string  """
def getMismatchCount(string1, string2):
    mismatchCount = 0
    if len(string1) != len(string2):
        #strings are not definitely same,
        #return an arbitrary large number to indicate this
        mismatchCount = 99
    else:
        for i in range(len(string1)):
            if string1[i] != string2[i]:
                mismatchCount += 1
    return mismatchCount

            
""" identify read pairs with in a directory, assuming name of these pair differ
only by one character,
e.g read_1.fastq, read_2.fastq or read.1.fastq, read.2.fastq, returns a list of
names of  read-pair tuple """
def getPairedReads(fastqDir):
    pairedReadTuples = []
    dirContents = os.listdir(fastqDir)
    readFileNames = []
    for fileName in dirContents:
        if os.path.isfile(os.path.join(fastqDir, fileName)) and \
                    fileName.endswith('fastq'):
            readFileNames.append(fileName)
    readFileNames.sort()
    #parse the sorted list with two reads at a time,
    #as reads with only one change in character of reads suffix will occur
    #together
    for i in range(0, len(readFileNames), 2):
        #compare i and i+1 filename
        misMatchCount = getMismatchCount(readFileNames[i], readFileNames[i+1])
        if misMatchCount == 1:
            #add the pair to read tuples
            pairedReadTuples.append((os.path.join(fastqDir,readFileNames[i]),\
                                         os.path.join(fastqDir,readFileNames[i+1])))
    return pairedReadTuples



""" write multiple jobs to convert paired SAIs to BAMs """
def writeCombineBAMJobsFromSAI(outDir, fastqDir, fastaPath, lockDirPath):
    combinedBAMJobsName = 'combinedBAMFrmPairedSAIsJob.jobs'
    combinedBAMJobsPath = os.path.join(outDir, combinedBAMJobsName)
    tools = workerForBam.getToolsDict()
    
    #contained all fastas against which to map the fastqs
    fastaFilePaths = workerForBam.getFastaFilePaths(fastaPath)

    print 'fastaFilePaths: ', fastaFilePaths
    with open(combinedBAMJobsPath, 'w') as combinedBAMJobsFile:
        pairedReads = getPairedReads(fastqDir)
        print 'pairedReads: ', pairedReads
        for pairedReadTuple in pairedReads:
            for fastaFilePath in fastaFilePaths:
                workerForBam.writePairedSAIToBAMJob(combinedBAMJobsFile, \
                                                        fastaFilePath,\
                                                        pairedReadTuple,\
                                                        lockDirPath, tools)
    return combinedBAMJobsPath



def callPairedSAIToBAMWorker((fastaFilePath, pairedReadTuple)):
    print "PID: ", os.getpid()
    #TODO: write paired sai to bam job
    return workerForBam.execPairedSAIIToBAMJob(fastaFilePath, pairedReadTuple)



def callPairedSAIToBAMWorkers(fastqDir, fastaPath):
    #contained all fastas against which to map the fastqs
    fastaFilePaths = workerForBam.getFastaFilePaths(fastaPath)
    print 'fastaFilePaths: ', fastaFilePaths

    pairedReads = getPairedReads(fastqDir)
    print 'pairedReads: ', pairedReads


    #initialize pool with number of possible jobs
    pool = Pool(processes=len(pairedReads)*len(fastaFilePaths))
    workersArgs = []

    #for each paired read and fasta create a job
    for pairedReadTuple in pairedReads:
        for fastaFilePath in fastaFilePaths:
            workersArgs.append((fastaFilePath, pairedReadTuple))

    results = pool.map(callPairedSAIToBAMWorker, workersArgs)
    pool.close()
    pool.join()
    return results

                    
def main():

    logger = multiprocessing.log_to_stderr()
    logger.setLevel(multiprocessing.SUBDEBUG)

    if len(sys.argv) >= 4:
        #directory containing fastq library
        fastqsDir = workerForBam.getAbsPath(sys.argv[1])
        
        #directory containing other directories with fasta names
        fastaDir = workerForBam.getAbsPath(sys.argv[2])

        #directory containing file locks
        lockDirPath = workerForBam.getAbsPath(sys.argv[3])
        
        #directory containing temp output -> fastQ's, jobsFile 
        outDir = workerForBam.getAbsPath(sys.argv[4])

        #write all fastq's processing in job file
        combineJobPath = writeCombineBAMJobsFromSAI(outDir, fastqsDir,\
                                                        fastaDir,\
                                                        lockDirPath)


        tools = workerForBam.getToolsDict()
        """retcode = workerForBam.callParallelDrone(combineJobPath,\
                                                     tools['PARALLEL_DRONE'])

        if retcode != 0:
            #error occured while calling parallel drone
            print "parallel drone erred, in executing combined jobs"
            return -1
        """
    else:
        print 'err: files missing'

if __name__ == '__main__':
    main()

