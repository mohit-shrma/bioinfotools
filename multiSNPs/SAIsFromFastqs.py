import sys
import os
from multiprocessing import Pool
import multiprocessing, logging

import workerForBam


def writeCombineSAIJobs(outDir, fastqDir, fastaPath, lockDirPath, numThreads):
    combinedSAIJobsName = 'combinedSAIJob.jobs'
    combinedSAIJobsPath = os.path.join(outDir, combinedSAIJobsName)
    tools = workerForBam.getToolsDict()
    
    #contained all fastas against which to map the fastqs
    fastaFilePaths = workerForBam.getFastaFilePaths(fastaPath)   

    #contained all fastqs
    fastqFilePaths = workerForBam.getFastqFilePaths(fastqDir)
    
    print 'fastaFilePaths: ', fastaFilePaths
    with open(combinedSAIJobsPath, 'w') as combinedSAIJobsFile:
        for fastqPath in fastqFilePaths:
            for fastaFilePath in fastaFilePaths:
                workerForBam.writeSAIJob(combinedSAIJobsFile, fastaFilePath,\
                                             fastqPath, lockDirPath, tools,\
                                             numThreads)
    return combinedSAIJobsPath



def callSAIWorker((fastaFilePath, fastqPath, numThreads)):
    print 'callSAIWorker: ', fastaFilePath, fastqPath, numThreads
    print "PID: ", os.getpid()
    return workerForBam.workerToGenSAI(fastaFilePath, fastqPath, numThreads)


def callSAIWorkers(fastqDir, fastaPath, numThreads = 12):

    #contained all fastas against which to map the fastqs
    fastaFilePaths = workerForBam.getFastaFilePaths(fastaPath)   
    print fastaFilePaths
    
    #contained all fastqs 
    fastqFilePaths = workerForBam.getFastqFilePaths(fastqDir)
    print fastqFilePaths
    
    #get number of processors
    numProcs = multiprocessing.cpu_count()
    print 'number of cpus: ', numProcs

    #compute number of jobs
    numJobs = len(fastqFilePaths)*len(fastaFilePaths)

    #initialize pool with number of possible jobs
    pool = Pool(processes=min(numJobs, numProcs))
    workersArgs = []

    #for each read and fasta create a job
    for fastaFilePath in fastaFilePaths:
        for fastqPath in fastqFilePaths:
            workersArgs.append((fastaFilePath, fastqPath, numThreads))

    results = pool.map(callSAIWorker, workersArgs)
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

        #initialize deafult value of threads
        numThreads = 12
        #TODO: make the following design correct
        if len(sys.argv) >= 5:
            #TODO: exception handling for conversion to int
            numThreads = int(sys.argv[5])

        #write all fastq's processing in job file
        combineJobPath = writeCombineSAIJobs(outDir, fastqsDir, fastaDir,\
                                                   lockDirPath, numThreads)

        #call workers to generate SAIs
        #TODO: take number of threads as args
        results = callSAIWorkers(fastqsDir, fastaDir, numThreads)

        print results
        
    else:
        print 'err: files missing'

if __name__ == '__main__':
    main()

