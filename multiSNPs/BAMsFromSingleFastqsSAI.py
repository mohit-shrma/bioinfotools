""" will find the bam file for paired reads, assuming already SAI are generated
using bwa   """
import sys
import os
from multiprocessing import Pool
import multiprocessing, logging

import workerForBam


""" write multiple jobs to convert single SAIs to BAMs """
def writeCombineBAMJobsFromSAI(outDir, fastqDir, fastaPath, lockDirPath):
    combinedBAMJobsName = 'combinedBAMFrmSingleSAIJob.jobs'
    combinedBAMJobsPath = os.path.join(outDir, combinedBAMJobsName)
    tools = workerForBam.getToolsDict()

    #contained all fastas against which to map the fastqs
    fastaFilePaths = workerForBam.getFastaFilePaths(fastaPath)   

    #contained all fastqs
    fastqFilePaths = workerForBam.getFastqFilePaths(fastqDir)
    
    print 'fastaFilePaths: ', fastaFilePaths
    with open(combinedBAMJobsPath, 'w') as combinedBAMJobsFile:
        for fastqPath in fastqFilePaths:
            for fastaFilePath in fastaFilePaths:
                workerForBam.writeSAIIToBAMJob(combinedBAMJobsFile,\
                                                   fastaFilePath,\
                                                   fastqPath,\
                                                   lockDirPath, tools)
    return combinedBAMJobsPath


def callSAIToBAMWorker((fastaFilePath, fastQFilePath)):
    print "PID: ", os.getpid()
    return workerForBam.execSAIIToBAMJob(fastaFilePath, fastQFilePath)


def callSAIToBAMWorkers(fastqDir, fastaPath):

    print 'callSAIToBAMWorkers'

    #contained all fastas against which to map the fastqs
    fastaFilePaths = workerForBam.getFastaFilePaths(fastaPath)   
    print 'fastaFilePaths: ', fastaFilePaths
    
    #contained all fastqs 
    fastqFilePaths = workerForBam.getFastqFilePaths(fastqDir)
    print fastqFilePaths
    print 'fastqFilePaths: ', fastqFilePaths
    
    #initialize pool with number of possible jobs
    pool = Pool(processes=len(fastqFilePaths)*len(fastaFilePaths))
    workersArgs = []

    #for each read and fasta create a job
    for fastaFilePath in fastaFilePaths:
        for fastqPath in fastqFilePaths:
            workersArgs.append((fastaFilePath, fastqPath))

    results = pool.map(callSAIToBAMWorker, workersArgs)
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

        #call workers to generate BAMs from SAIs
        results = callSAIToBAMWorkers(fastqsDir, fastaDir)
        print results
        
    else:
        print 'err: files missing'

if __name__ == '__main__':
    main()

