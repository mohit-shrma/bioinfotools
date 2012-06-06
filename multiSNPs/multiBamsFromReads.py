import sys
import os
import parallelSNPsFinder
from multiprocessing import Pool
import multiprocessing, logging

import workerForBam


def getReads(readsDir):
    readsExt = workerForBam.getExtDict()['READS_EXT']
    dirContents = os.listdir(readsDir)
    reads = []
    for name in dirContents:
        if os.path.isfile(os.path.join(readsDir, name)) and\
                name.endswith(readsExt):
            reads.append(name)
    return reads

def getAbsPath(dir):
    absDir = os.path.abspath(dir)
    if not absDir.endswith('/'):
        absDir += '/'
    return absDir

def callBamWorker((readPath, outDir, lockDirPath, fastaPath)):
    print "PID: ", os.getpid()
    return workerForBam.workerToGenBAM(readPath, outDir, lockDirPath, fastaPath)

def callBamWorkers(readsDir, outDir, locksDir, fastaDir):
    reads = getReads(readsDir)
    print reads
    pool = Pool(processes=len(reads))
    workersArgs = []
    for read in reads:
        readPath = readsDir + read
        workersArgs.append((readPath, outDir, locksDir, fastaDir))
    results = pool.map(callBamWorker, workersArgs)
    pool.close()
    pool.join()
    return results

def isValidResults(results):
    if sum(results) == len(results):
        return True
    else:
        return False

#concatenate all jobs in outDir to be executed by drone
def combineAllBamJobs(outDir):
    combinedBAMJobsName = 'combinedBAMJob.jobs'
    combinedBAMJobsPath = os.path.join(outDir, combinedBAMJobsName)
    try:
        combinedBAMJobsFile = open(combinedBAMJobsPath, 'w')
        dirContents = os.listdir(outDir)
        for fileName in dirContents:
            contentPath = os.path.join(outDir, fileName)
            if os.path.isfile(contentPath) and\
                    fileName.endswith('Jobs.jobs')\
                    and fileName.startswith('SRR'):
                #found a job file
                jobFile = open(contentPath, 'r')
                for line in jobFile:
                    combinedBAMJobsFile.write(line)
                jobFile.close()
        combinedBAMJobsFile.close()
    except IOError as (errno, strerror):
        print "I/O error({0}): {1}".format(errno, strerror)        
        return -1
    return combinedBAMJobsPath
                                  

    
def main():

    logger = multiprocessing.log_to_stderr()
    logger.setLevel(multiprocessing.SUBDEBUG)

    if len(sys.argv) >= 4:
        #directory containing reads library
        readsDir = getAbsPath(sys.argv[1])
        
        #directory containing other directories with fasta names
        fastaDir = getAbsPath(sys.argv[2])

        #directory containing file locks
        locksDir = getAbsPath(sys.argv[3])
        
        #directory containing temp output -> fastQ's, jobsFile 
        outDir = getAbsPath(sys.argv[4])

        #call child workers to do the job
        print "calling child workers"
        bamWorkResults = callBamWorkers(readsDir, outDir, locksDir, fastaDir)

        print "bam work results: " + str(bamWorkResults)
        
        if not isValidResults(bamWorkResults):
            print "a worker on strike"
            return

        #combined all jobs for a job file
        combineJobPath = combineAllBamJobs(outDir)
        if combineJobPath == -1:
            print 'job concat error'
            return

        tools = workerForBam.getToolsDict()
        retcode = workerForBam.callParallelDrone(combineJobPath, tools['PARALLEL_DRONE'])

        if retcode != 0:
            #error occured while calling parallel drone
            print "parallel drone erred, in executing combined jobs"
            return -1
        
        #now for all scaffolds combined bams and look for SNPs
        #parallelSNPsFinder.snpsFinder(fastaDir, outDir, locksDir)
        
    else:
        print 'err: files missing'

if __name__ == '__main__':
    main()

