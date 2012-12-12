import sys
import os
import parallelSNPsFinder
from multiprocessing import Pool
import multiprocessing, logging

import workerForBam

def getAbsPath(dir):
    absDir = os.path.abspath(dir)
    if not absDir.endswith('/'):
        absDir += '/'
    return absDir


def writeCombineFastqJobs(outDir, fastqDir, fastaPath, lockDirPath):
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
        dirContents = os.listdir(fastqDir)
        for fileName in dirContents:
            fastqPath = os.path.join(fastqDir, fileName)
            if os.path.isfile(fastqPath) and\
                    fileName.endswith('fastq'):
                for fastaFilePath in fastaFilePaths:
                    workerForBam.writeJob(combinedBAMJobsFile, fastaFilePath,\
                                              fastqPath, lockDirPath, tools)
    return combinedBAMJobsPath


                    
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
        #combineJobPath = writeCombineFastqJobs(outDir, fastqsDir, fastaDir,\
        #    lockDirPath)


        tools = workerForBam.getToolsDict()
        """retcode = workerForBam.callParallelDrone(combineJobPath,\
                                                     tools['PARALLEL_DRONE'])

        if retcode != 0:
            #error occured while calling parallel drone
            print "parallel drone erred, in executing combined jobs"
            return -1
        """
        #now for all scaffolds combined bams and look for SNPs
        parallelSNPsFinder.snpsFinder(fastaDir, outDir, lockDirPath)
        
    else:
        print 'err: files missing'

if __name__ == '__main__':
    main()

