import sys
import os

""" takes the completed output directory and the directory to output locks
 and out files for completed jobs  """

class JobConsts:

    #completed out extension
    JOB_COMP_EXT = 'out'

    #lock extension
    JOB_LOCK_EXT = 'lock'

    #job output extension
    JOB_OUT_EXT = 'out'
    

    
""" return lists of completed jobs in the dir with output suffix removed"""
def findCompletedJobsPrefix(compDir):
    compJobsList = []
    dirContents = os.listdir(compDir)
    for fileName in dirContents:
        if fileName.endswith('.' + JobConsts.JOB_COMP_EXT):
            compJobsList.append(fileName.rstrip('.' + JobConsts.JOB_COMP_EXT))
    return compJobsList



""" check existence of lock & out file for passed filename in lockdir """
def isLockNOutExists(fileNamePrefix, lockDir):
    lockFileName = fileNamePrefix + '.' + JobConsts.JOB_LOCK_EXT
    outFileName = fileNamePrefix + '.' + JobConsts.JOB_OUT_EXT
    return ( os.path.isfile(os.path.join(lockDir, lockFileName)) \
                 and os.path.isfile(os.path.join(lockDir, outFileName)) )



""" write lock N out file in lockdir """
def writeLockNOut(fileNamePrefix, lockDir):
    lockFileName = fileNamePrefix + '.' + JobConsts.JOB_LOCK_EXT
    outFileName = fileNamePrefix + '.' + JobConsts.JOB_OUT_EXT
    lockFile = open(os.path.join(lockDir, lockFileName), 'w')
    lockFile.close()
    outFile = open(os.path.join(lockDir, outFileName), 'w')
    outFile.close()

    

""" create empty lock and out file for files in list if dont exists """
def createLockNOut(compJobsList, lockDir):
    for compJobPrefix in compJobsList:
        if not isLockNOutExists(compJobPrefix, lockDir):
            writeLockNOut(compJobPrefix, lockDir)

            

def main():
    if len(sys.argv) >= 3:
        lockDir = os.path.abspath(sys.argv[1])
        compDir = os.path.abspath(sys.argv[2])
        completedJobs = findCompletedJobsPrefix(compDir)
        createLockNOut(completedJobs, lockDir)
    else:
        print 'err: files missing'

if __name__ == '__main__':
    main()
            
    


        
    
