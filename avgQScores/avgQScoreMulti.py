import sys
import os
from multiprocessing import Pool
import multiprocessing, logging
from subprocess import call

#return the absolute path of a filepath
def getAbsPath(dir):
    absDir = os.path.abspath(dir)
    if not absDir.endswith('/'):
        absDir += '/'
    return absDir


""" identify all the fastq's inside a folder,
parentDir/samplesDir{1,2,3...16}/<xyz.{fastq|fastq.gz}>"""

def getAllFastqsPath(samplesDir):

    fastQsFilePaths = []
    
    samplsDirContents = os.listdir(samplesDir)
    allSamplesDir = []

    #get list of samples directory inside the passed dir
    for name in samplsDirContents:
        contentPath = os.path.join(samplesDir, name)
        if os.path.isdir(contentPath):
            allSamplesDir.append(contentPath)

    #find all fastq's after
    for sampleDir in allSamplesDir:

        sampleDirContents = os.listdir(sampleDir)

        for name in sampleDirContents:
            
            if name.endswith('.fastq'):
                if name+'.gz' not in sampleDirContents:
                    fastQsFilePaths.append(os.path.join(sampleDir, name))
            elif name.endswith('.fastq.gz'):
                #either fastq or fastq compressed file
                fastQsFilePaths.append(os.path.join(sampleDir, name))
                
    return fastQsFilePaths

#return directory containing file and file name without extension
def getDirNFileName(filePath):

    #fileName
    fileName = (filePath.split('/')[-1]).split('.')[0]

    #folder containing file
    fileDir = '/'.join(filePath.split('/')[:-1]) + '/'

    return (fileDir, fileName)

    
#worker to do qscore calculation o passed fastq, unzip if required
def qscoreWorker((fastQPath, qScoreFilePath, qScorePerlScript)):
    print "PID: ", os.getpid()
    
    #if fastq compressed, then unzip it
    #unzip compressed fastQ
    if fastQPath.endswith('.gz'):
        #unzip compressed fastQ
        try:
            retcode = call(["gunzip", "-f", fastQPath])
            if retcode != 0:
                #unzip command failed
                print >>sys.stderr, "unzip command fail"
                return -1
        except OSError, e:
            print >>sys.stderr, "Execution failed: ", e
            return -1
        
        fastQPath = fastQPath.rstrip('.gz')

    (fastQDir, fastQFileName) = getDirNFileName(fastQPath)

    #output file paths to be passed to perl script
    seqAvgsFilePath = fastQDir  + fastQFileName + '_seqavgs.txt'
    seqAvgScorePath = fastQDir  + fastQFileName + '_avgscore.txt'

    #print qScorePerlScript, fastQPath, seqAvgsFilePath, seqAvgScorePath

    print >>sys.stdout, qScorePerlScript, fastQPath, seqAvgsFilePath, seqAvgScorePath

    #flush the output stream
    sys.stdout.flush()
    
    #call perl script for calculation on passed fastq
    #retcode = call("perl" + qScorePerlScript
    #    + " fastQPath qScoreFilePath seqAvgsFilePath seqAvgScorePath ",
    #        shell=True)
    
    try: 
        retcode = call(["perl", qScorePerlScript, fastQPath, qScoreFilePath,\
                       seqAvgsFilePath, seqAvgScorePath])
        if retcode == 0:
            #passed
            print fastQPath + " evaluated"
            return 1
        else:
            #failed
            print fastQPath + " evaluation failed"
    except OSError, e:
        print >>sys.stderr, "Execution failed: ", e

    return  -1    

def prepAndRunWorkers(fastQPaths, qScoreFilePath, qScorePerlScript):

    pool = Pool(processes=min(len(fastQPaths), 32))
    workersArgs = []
    
    #prepare argument for each worker
    for fastQPath in fastQPaths:
        workersArgs.append((fastQPath, qScoreFilePath, qScorePerlScript))
    print "calling pool.map"
    results = pool.map(qscoreWorker, workersArgs)
    pool.close()
    pool.join()

    return results

def main():

    logger = multiprocessing.log_to_stderr()
    logger.setLevel(multiprocessing.SUBDEBUG)

    
    if len(sys.argv) >= 3:
        #directory containing samples which contains fastq
        samplesDir = getAbsPath(sys.argv[1])
        
        #quality scores file
        qScoreFile = getAbsPath(sys.argv[2]).rstrip('/')

        #perl script for qscore calculation
        qScorePerlScript = getAbsPath(sys.argv[3]).rstrip('/')
        
        #fastQs paths
        fastQFilePaths = getAllFastqsPath(samplesDir)

        #display fastQFilePaths contents
        print fastQFilePaths, len(fastQFilePaths)
        
        #call child workers to do the job
        prepAndRunWorkers(fastQFilePaths, qScoreFile, qScorePerlScript)
    else:
        print 'err: files missing'

if __name__ == '__main__':
    main()

