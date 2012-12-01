""" will find the bam file for paired reads, assuming already SAI are generated
using bwa   """
import sys
import os
from multiprocessing import Pool
import multiprocessing, logging

import workerForBam


def getAbsPath(dir):
    absDir = os.path.abspath(dir)
    if not absDir.endswith('/'):
        absDir += '/'
    return absDir

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
        if os.path.isfile(fileName) and \
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
            pairedReadTuples.append((readFileNames[i], readFileNames[i+1]))
    return pairedReadTuples



""" write multiple jobs to convert paired SAIs to BAMs """
def writeCombineBAMJobsFromSAI(outDir, fastqDir, fastaPath, lockDirPath):
    combinedBAMJobsName = 'combinedBAMJob.jobs'
    combinedBAMJobsPath = os.path.join(outDir, combinedBAMJobsName)
    tools = workerForBam.getToolsDict()
    #contained all fastas against which to map the fastqs
    fastaFilePaths = []    
    #fastaPath contains all .fasta inside a dir with same name as fasta
    #get all fasta name without ext ".fasta" in a list
    fastaDirs = workerForBam.getAllFastas(fastaPath)
    for fastaDir in fastaDirs:
        #get fasta File Path        
        fastaFilePath = fastaPath + fastaDir + "/" + fastaDir + ".fasta"
        fastaFilePaths.append(fastaFilePath)
    print 'fastaFilePaths: ', fastaFilePaths
    with open(combinedBAMJobsPath, 'w') as combinedBAMJobsFile:
        pairedReads = getPairedReads(fastqDir)
        print 'pairedReads: ', pairedReads
        for pairedReadTuple in pairedReads:
            pairedReadTuple[0] = os.path.join(fastqDir, pairedReadTuple[0])
            pairedReadTuple[1] = os.path.join(fastqDir, pairedReadTuple[1])
            for fastaFilePath in fastaFilePaths:
                workerForBam.writePairedSAIToBAMJob(combinedBAMJobsFile, \
                                                        fastaFilePath,\
                                                        pairedReadTuple,\
                                                        lockDirPath, tools)
    return combinedBAMJobsPath


                    
def main():

    logger = multiprocessing.log_to_stderr()
    logger.setLevel(multiprocessing.SUBDEBUG)

    if len(sys.argv) >= 4:
        #directory containing fastq library
        fastqsDir = getAbsPath(sys.argv[1])
        
        #directory containing other directories with fasta names
        fastaDir = getAbsPath(sys.argv[2])

        #directory containing file locks
        lockDirPath = getAbsPath(sys.argv[3])
        
        #directory containing temp output -> fastQ's, jobsFile 
        outDir = getAbsPath(sys.argv[4])

        #write all fastq's processing in job file
        combineJobPath = writeCombineBAMJobsFromSAI(outDir, fastqsDir,\
                                                        fastaDir,\
                                                        lockDirPath)


        tools = workerForBam.getToolsDict()
        retcode = workerForBam.callParallelDrone(combineJobPath,\
                                                     tools['PARALLEL_DRONE'])

        if retcode != 0:
            #error occured while calling parallel drone
            print "parallel drone erred, in executing combined jobs"
            return -1
        
    else:
        print 'err: files missing'

if __name__ == '__main__':
    main()

