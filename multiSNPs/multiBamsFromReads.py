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
        bamWorkResults = callBamWorkers(readsDir, outDir, locksDir, fastaDir)

        print "bam work results: " + str(bamWorkResults)
        
        if not isValidResults(bamWorkResults):
            print "a worker on strike"
            return

        #now for all scaffolds combined bams and look for SNPs
        parallelSNPsFinder.snpsFinder(fastaDir, outDir, locksDir)
        
    else:
        print 'err: files missing'

if __name__ == '__main__':
    main()

