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


#concatenate all the fastQ's inside a sample dir
def combineFastQs(sampleDir):

    #get the sample dir name
    dirName = sampleDir.split('/')[-1]

    #combined output file path
    combinedFilePath = getAbsPath(sampleDir) + dirName\
        + '.fastq'

    #concatenate all fastq's inside to fastqpath
    retcode = -1
    try:
        allFastQsPath = os.path.join(sampleDir, "*.fastq")
        print allFastQsPath, combinedFilePath
        retcode = call("cat " + allFastQsPath\
                            + " > " + combinedFilePath, shell=True)
        if retcode == 0:
            #successfully concatenated fastq
            retcode = 1
        else:
            #error found in concatenation
            print "fastqCombine error: ", sampleDir, retcode
            retcode = -1
    except OSError, e:
        print >>sys.stderr, "Execution failed: ", e
        print "fastqCombine error: ", sampleDir
        retcode = -1
    return retcode


#return all sample dir paths in a list
def allSampleDirsPath(sampleDirsParent):

    #get all contents inside saple directory
    samplesDirContents = os.listdir(sampleDirsParent)
    allSamplesDir = []
    
    #get list of samples directory inside the passed dir
    for name in samplesDirContents:
        contentPath = os.path.join(sampleDirsParent, name)
        if os.path.isdir(contentPath):
            allSamplesDir.append(contentPath)
    return allSamplesDir


""" identify all the fastq's inside a folder,
parentDir/samplesDir{1,2,3...16}/<xyz.{fastq|fastq.gz}>"""

def getAllFastqsPath(samplesDir):
    fastQsFilePaths = []
    #get list of samples directory inside the passed dir
    allSamplesDir = allSampleDirsPath(samplesDir)
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
    retcode = computeQScore(qScorePerlScript, fastQPath, qScoreFilePath,\
                            seqAvgsFilePath, seqAvgScorePath)
    return retcode

#worker that combine fastQ's inside samples and compute Qscore on combined fastq result
def workerToCombineAndCompute((sampleDir, qScoreFilePath, qScorePerlScript)):

    print sampleDir + 'worker'
    
    #combine all fastq's inside sample directory
    retcode = combineFastQs(sampleDir)

    if retcode == -1:
        return False

    sampleDirName = os.path.basename(sampleDir.rstrip('/'))
    combinedFastQPath = os.path.join(sampleDir, sampleDirName + '.fastq')

    #output file paths to be passed to perl script
    seqAvgsFilePath = os.path.join(sampleDir, sampleDirName +  '_seqavgs.txt')
    seqAvgScorePath = os.path.join(sampleDir, sampleDirName +  '_avgscore.txt')

    #compute q score for combinedFastQ file
    retcode = computeQScore(qScorePerlScript, combinedFastQPath, qScoreFilePath,\
                                seqAvgsFilePath, seqAvgScorePath)
    if retcode == 1:
        return True
    else:
        return False

#compute the q score by calling the perl script with passed arguments
def computeQScore(qScorePerlScript, fastQPath, qScoreFilePath,\
                       seqAvgsFilePath, seqAvgScorePath):
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
            retcode =  1
        else:
            #failed
            print fastQPath + " evaluation failed", retcode
            retcode = -1
    except OSError, e:
        print >>sys.stderr, "Execution failed: ", e, fastQPath
        retcode = -1
    return retcode
        

#prepare child workers to work for each directory
def prepAndRunWorkers(allSamplesDir, qScoreFilePath, qScorePerlScript):

    pool = Pool(processes=min(len(allSamplesDir), 32))
    workersArgs = []
    
    #prepare argument for each worker
    for sampleDir in allSamplesDir:
        workersArgs.append((sampleDir, qScoreFilePath, qScorePerlScript))
    print "calling pool.map"
    results = pool.map(workerToCombineAndCompute, workersArgs)
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
        
        #get all sample directory inside samplesDir
        allSamplesDir = allSampleDirsPath(samplesDir)
        
        #call child workers to do the job
        results = prepAndRunWorkers(allSamplesDir, qScoreFile, qScorePerlScript)

        #print final results
        print "avgQScoreComputation success: ", all(results)
    else:
        print 'err: files missing'

if __name__ == '__main__':
    main()

