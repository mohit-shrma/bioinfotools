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


""" write multiple jobs to convert single SAIs to BAMs """
def writeCombineBAMJobsFromSAI(outDir, fastqDir, fastaPath, lockDirPath):
    combinedBAMJobsName = 'combinedBAMFrmSingleSAIJob.jobs'
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
                    workerForBam.writeSAIIToBAMJob(combinedBAMJobsFile,\
                                                       fastaFilePath,\
                                                       fastqPath,\
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

