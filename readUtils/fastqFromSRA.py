import sys
import os

from multiprocessing import Pool
import multiprocessing, logging

from subprocess import call, check_call
from subprocess import CalledProcessError



""" get all reads ending with .lite.sra"""
def getReads(readsDir):
    readsExt = ".lite.sra" 
    dirContents = os.listdir(readsDir)
    reads = []
    for name in dirContents:
        if os.path.isfile(os.path.join(readsDir, name)) and\
                name.endswith(readsExt):
            reads.append(name)
    return reads



#get the read name from the read path
def getLibraryName(readLibraryPath):
    return ((readLibraryPath.split('/')[-1]).split('.'))[0]


#check the existence if exists of fastq file in outDir
def checkIfFileExists(fileNamePrefix, fileExt, outDir):
    try:
        dirContents=os.listdir(outDir)
        for name in dirContents:
            if os.path.isfile(os.path.join(outDir, name))\
                    and name.startswith(fileNamePrefix)\
                    and name.endswith(fileExt):
                return True
        return False
    except IOError as (errno, strerror):
        print "I/O error({0}): {1}".format(errno, strerror)
    return False



#genearate fastq files using fastw dump from read
def generateFastQ(readLibraryPath, outDir, fastQDumpCmd):
    #extract library name
    libName = getLibraryName(readLibraryPath)
    retcode = -99
    try:
        retcode = call(fastQDumpCmd + " -A " + libName
                       + " -O " + outDir + " " +  readLibraryPath,
                       shell=True)
        #retcode = 0               
        if retcode < 0:
            print >>sys.stderr, "child terminated by signal", retcode
        else:
            print >>sys.stderr, "child returned", retcode
            #check if retcode is 0 then check for existence of fataq file
            if retcode == 0 and checkIfFileExists(libName, ".fastq", outDir):
                return 1
            else:
                return 0
    except OSError, e:
        print >>sys.stderr, "Execution failed: ", e
    return retcode


""" convert passed sra into fastq"""
def callFastQConverter((sraDir, sraRead)):
    
    fastqDumpCmd = "/home/koronis/mohit/programs/sratoolkit.2.1.0-ubuntu32/fastq-dump" 
    libraryPath = os.path.join(sraDir, sraRead)
    return generateFastQ(libraryPath, sraDir, fastqDumpCmd)


""" convert sra in dir to fastq  """
def callFastqConverterWorkers(sraDir):
    #contain all sra reads which needs to convert
    sraReads = getReads(sraDir)
    print sraReads
    
    #get number of processors
    numProcs = multiprocessing.cpu_count()
    print 'number of cpus: ', numProcs

    #compute number of jobs
    numJobs = len(sraReads)

    #initialize pool with number of possible jobs
    pool = Pool(processes=min(numJobs, numProcs))
    workersArgs = []

    #for each read create a job
    for sraRead in sraReads:
        workersArgs.append((sraDir, sraRead))
    
    results = pool.map(callFastQConverter, workersArgs)
    pool.close()
    pool.join()
    return results
    
    
                    
def main():

    logger = multiprocessing.log_to_stderr()
    logger.setLevel(multiprocessing.SUBDEBUG)

    if len(sys.argv) >= 1:
        #directory containing sra library
        sraDir = sys.argv[1]
        
        #call workers to generate fastq's
        results = callFastqConverterWorkers(sraDir)

        print results
        
    else:
        print 'err: files missing'

if __name__ == '__main__':
    main()

