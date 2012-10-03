import sys
import os


class ScaffConsts:
    #fasta extension
    FASTA_EXT = 'fasta'

    #lock extension
    FASTA_LOCK = 'lock'

    #out extension
    FASTA_OUT = 'out'
    
    
def findPendingLocks(lockDir, outDir = None):
    dirContents = os.listdir(lockDir)
    completedJobs = {}
    for fileName in dirContents:
        if fileName.endswith('.' + ScaffConsts.FASTA_OUT):
            completedJobs[fileName.rstrip('.' + ScaffConsts.FASTA_OUT)] = 1

    #remove ".lock" files not in completed jobs
    for fileName in dirContents:
        if fileName.endswith('.' + ScaffConsts.FASTA_LOCK) and\
                fileName.rstrip('.' + ScaffConsts.FASTA_LOCK) not in completedJobs:
            #found a pending job and remove it
            os.remove(os.path.join(lockDir, fileName))

    #remove contents in outDir
    dirContents = os.listdir(outDir)
    for fileName in dirContents:
        if fileName.endswith('.' + ScaffConsts.FASTA_OUT):
            filePrefix = fileName.rstrip('.' + ScaffConsts.FASTA_OUT)
            if filePrefix not in completedJobs:
                #found a partial output remove it
                os.remove(os.path.join(outDir, fileName))
            
    return completedJobs.keys()
            
            

def findIntSuffix(scaffName):
    scaffName = scaffName.rstrip('.' + ScaffConsts.FASTA_EXT)
    digitFound = False
    for i in range(len(scaffName)):
        if scaffName[i].isdigit():
            digitFound = True
            break
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
    #prevNum = numSuffs[0]
    prevNum = 0
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
        print 'Missing jobs as follow: '
        for missingJob in missingJobs:
            print missingJob
    else:
        print 'err: files missing'



if __name__ == '__main__':
    main()
