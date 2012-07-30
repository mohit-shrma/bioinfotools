import sys
import os


def findPendingLocks(lockDir, outDir = None):
    dirContents = os.listdir(lockDir)
    completedJobs = {}
    for fileName in dirContents:
        if fileName.endswith('.out'):
            completedJobs[fileName.rstrip('.out')] = 1
    #remove ".lock" files not in completed jobs
    for fileName in dirContents:
        if fileName.endswith('.lock') and\
                fileName.rstrip('.lock') not in completedJobs:
            #found a pending job and remove it
            os.remove(os.path.join(lockDir, fileName))
            if outDir is not None:
                #remove partial output file too
                os.remove(os.path.join(outDir,\
                                       fileName.rstrip('.lock') + '.out'))
    return completedJobs.keys()
            
            

def findIntSuffix(scaffName):
    digitFound = False
    for i in range(len(scaffName)):
        if scaffName[i].isdigit():
            digitFound = True
    #return integer suffix starting at index 'i'
    if digitFound:
        return int(scaffName[i:])
    else:
        return -1
            


#takes the files list as input and sort it by numerical suffix
def findMissingSeqFiles(filesList):
    missingSeq = []
    numSuffs = map(findIntSuffix, filesList)
    numSuffs.sort()
    prevNum = numSuffs[0]
    for num in numSuffs[1:]:
        if num != prevNum + 1:
            #print all num in between prevNum and num
            missingSeq += range(prevNum+1, num)
        prevNum = num
    return missingSeq
    
            
            
def main():

    if len(sys.argv) >= 3:
        lockDir = os.path.abspath(sys.argv[1])
        outDir = os.path.abspath(sys.argv[2])
        completedJobs = findPendingLocks(lockDir, outDir)
        missingJobs = findMissingSeqFiles(completedJobs)
        print 'missing: ', missingJobs
    else:
        print 'err: files missing'



if __name__ == '__main__':
    main()
