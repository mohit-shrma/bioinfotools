import sys
import os
from scipy.stats import poisson

class FileExts:
    SORTED_BAM = 'sorted.bam'
    SNP = 'snp'
    VCF = 'vcf'
    BCF = 'bcf'
    INDEL = 'indel'
    FASTA = 'fa'
    LOCK = 'lock'
    OUT = 'out'
    PILEUP = 'pileup'
    
    
class Programs:
    #specify the path
    SAMTOOLS = '/project/huws/huwsgroup/Nitya/SAMtools18/samtools-0.1.18/samtools'
    BCFTOOLS = '/project/huws/huwsgroup/Nitya/SAMtools18/samtools-0.1.18/bcftools/bcftools'
    MAP_QUAL = 'perl /project/huws/huwsgroup/mohit/bgicomp/anrewPipe/add_mappingqual2.pl'
    INDEL_INFO = 'perl /project/huws/huwsgroup/mohit/bgicomp/anrewPipe/add_indelinfo.pl'
    ANDRE_FISHER = 'matlab -r /project/huws/huwsgroup/mohit/bgicomp/anrewPipe/Andrew_fisher'
    POISSON_VARREAD = 'python /project/huws/huwsgroup/mohit/bgicomp/anrewPipe/fourthSNP.py'
    NUC_CONV = 'perl /project/huws/huwsgroup/mohit/bgicomp/anrewPipe/nucleotideconvertion.pl'
    NUC_CONV_ACID = '/project/huws/huwsgroup/mohit/bgicomp/anrewPipe/Nucleicacid.txt'
    ADD_READPOS = 'perl /project/huws/huwsgroup/mohit/bgicomp/anrewPipe/add_readposition3.pl'
    SIXTH_SNP = 'python /project/huws/huwsgroup/mohit/bgicomp/anrewPipe/sixthSNP.py'

    
def getAbsPath(dir):
    absDir = os.path.abspath(dir)
    if not os.path.isfile(dir) and not absDir.endswith('/'):
        absDir += '/'
    return absDir

    
def findAllExtFiles(ipDir, fileExt):
    resultFiles = []
    for fileName in os.listdir(ipDir):
        filePath = os.path.join(ipDir, fileName)
        if os.path.isfile(filePath) and\
                (fileName.endswith(fileExt) or\
                     fileName.endswith(fileExt.upper())):
            resultFiles.append(filePath)
    return resultFiles


#get all pileups inside dir
def findAllPileups(ipDir):
    return findAllExtFiles(ipDir, FileExts.PILEUP)


#get all snps inside dir
def findAllSNPs(ipDir):
    return findAllExtFiles(ipDir, FileExts.SNP)


#get all sorted bams inside ipDir
def findAllSortedBAMs(ipDir):
    return findAllExtFiles(ipDir, FileExts.SORTED_BAM)


#get all indels
def findAllIndels(ipDir):
    return findAllExtFiles(ipDir, FileExts.INDEL)

#get all fastas
def findAllFastas(ipDir):
    return findAllExtFiles(ipDir, FileExts.FASTA)


def getCommonPrefix(name1, name2):
    i = -1
    for i in range(len(name1)):
        if name1[i] != name2[i]:
            break
    if i > 0:
        return name1[0:i]
    else:
        print 'err: getCommonPrefix'
    

        
def generateBCF(ipDir, prefix, sequenceName):
    cmdStr = ''
    #assumong only one fastas
    #TODO: check
    #fastas = findAllFastas(ipDir)
    sortedBAMs = findAllSortedBAMs(ipDir)

    #get the prefix
    #prefix = getCommonPrefix(sortedBAMs[0], sortedBAMs[1])
    
    #assuming there is only one fasta
    cmdStr += Programs.SAMTOOLS + ' mpileup -B -d 100000000 -u -f ' + sequenceName + ' '\
        + ' '.join(sortedBAMs) + ' > ' + os.path.join(ipDir, prefix + '.' +FileExts.BCF)
    return cmdStr



def generateVCF(ipDir, prefix):
    bcfPath = os.path.join(ipDir, prefix + '.' + FileExts.BCF)
    vcfPath = os.path.join(ipDir, prefix + '.' + FileExts.VCF)
    cmdStr = ''
    cmdStr += Programs.BCFTOOLS + ' view -cg ' + bcfPath + ' > ' + vcfPath
    return cmdStr



#get all dirs inside ipDir containing sorted BAMs 
def getAllBAMDirs(ipDir):
    resultDirs = []
    for fileName in os.listdir(ipDir):
        filePath = os.path.join(ipDir, fileName)
        if os.path.isdir(filePath):
            resultDirs.append(filePath)
    return resultDirs


def genFirstSNP(ipDir, prefix):
    snps = findAllSNPs(ipDir)
    #TODO: dont take _?.snp
    ipSnp = snps[0]
    cmdstr = ''
    cmdstr += Programs.MAP_QUAL + ' ' + ipSnp + ' '\
        + os.path.join(ipDir, prefix + '.' + FileExts.VCF) + ' '\
        + os.path.join(ipDir, prefix + '_1' + '.' + FileExts.SNP)
    return cmdstr


def genSecondSNP(ipDir, prefix):
    firstSNP = os.path.join(ipDir, prefix + '_1' + '.' + FileExts.SNP)
    secondSNP = os.path.join(ipDir, prefix + '_2' + '.' + FileExts.SNP)
    indels = findAllIndels(ipDir)
    #assuming only one indel
    #TODO: check
    indel = indels[0]
    cmdStr = ''
    cmdStr += Programs.INDEL_INFO + ' ' + firstSNP +  ' '\
        + indel + ' ' + secondSNP
    return cmdStr


def genThirdSNPByFisher(ipDir, prefix):
    secondSNP = os.path.join(ipDir, prefix + '_2' + '.' + FileExts.SNP)
    thirdSNP = os.path.join(ipDir, prefix + '_3' + '.' + FileExts.SNP)
    cmdStr = Programs.ANDRE_FISHER + '(' + secondSNP + ',' + thirdSNP + ')'
    return cmdStr


def getFourthSNPByPoisson(ipDir, prefix):
    thirdSNP = os.path.join(ipDir, prefix + '_3' + '.' + FileExts.SNP)
    fourthSNP = os.path.join(ipDir, prefix + '_4' + '.' + FileExts.SNP)
    cmdStr = Programs.POISSON_VARREAD + ' ' + ipDir + ' ' + prefix 
    return cmdStr


def getFifthSNP(ipDir, prefix):
    fourthSNP = os.path.join(ipDir, prefix + '_4' + '.' + FileExts.SNP)
    fifthSNP = os.path.join(ipDir, prefix + '_5' + '.' + FileExts.SNP)
    cmdStr = Programs.NUC_CONV + ' ' + fourthSNP + ' ' + Programs.NUC_CONV_ACID  + ' ' + fifthSNP
    return cmdStr



def getSixthSNP(ipDir, prefix):
    fifthSNP = os.path.join(ipDir, prefix + '_5' + '.' + FileExts.SNP)
    cmdStr = Programs.SIXTH_SNP + ' ' + ipDir + ' ' + prefix 
    return cmdStr
    

def getFinalSNP(ipDir, prefix):
    sixthSNP = os.path.join(ipDir, prefix + '_6.' + '.' + FileExts.SNP)
    seventhSNP = os.path.join(ipDir, prefix + '_7.' + '.' + FileExts.SNP)
    #assuming only one pileup inside
    pileUp = findAllPileups(ipDir)[0]
    cmdStr = Programs.ADD_READPOS + ' ' +  sixthSNP + ' ' + pileUp + ' ' + seventhSNP
    return cmdStr

def getSingleSNPJob(ipDir, lockDir, sequenceName):
    jobStr = ''
    sortedBAMs = findAllSortedBAMs(ipDir)
    prefix = (sortedBAMs[0].split('/')[-1]).rstrip('.' + FileExts.SORTED_BAM)
    if len(sortedBAMs) > 1:
        prefix = getCommonPrefix((sortedBAMs[0].split('/'))[-1], (sortedBAMs[1].split('/'))[-1])

    #job lock file path for current job
    currentJobLockFile = os.path.join(lockDir, prefix + '.' + FileExts.LOCK)

    #job out file path for current job
    currentJobOutFile = os.path.join(lockDir, prefix + '.' + FileExts.OUT) 

    
    #check for  lock file in case current job is already executed
    jobStr += "if [ -f " + currentJobLockFile + " ]; then echo \"" \
                       + currentJobLockFile  \
                       +" done\"; exit 0; "
 
    #check if job is already finished
    jobStr += "elif [ -f " + currentJobOutFile \
                       + "]; then echo \"" \
                       + currentJobOutFile \
                       +" done\"; exit 0;  "
    jobStr += "else "
    #need to execute job

    #write lock file b4 executing job
    jobStr += "touch " + currentJobLockFile + "; "

    #write statements for processing job

    #change directory to scaffold where we are working
    jobStr += "cd "+ ipDir +"; "

    #get script statements
    cmdStrs = []
    
    #generate bcf
    #cmdStrs.append(generateBCF(ipDir, prefix, sequenceName))

    #generate vcf
    #cmdStrs.append(generateVCF(ipDir, prefix))

    #generate first snp
    #cmdStrs.append(genFirstSNP(ipDir, prefix))

    #generate second snp
    #cmdStrs.append(genSecondSNP(ipDir, prefix))

    #generate third snp
    cmdStrs.append(genThirdSNPByFisher(ipDir, prefix))

    #generate fourth snp
    cmdStrs.append(getFourthSNPByPoisson(ipDir, prefix))

    #generate fifth snp
    cmdStrs.append(getFifthSNP(ipDir, prefix))

    #generate sixth snp
    cmdStrs.append(getSixthSNP(ipDir, prefix))

    #generate final snp
    cmdStrs.append(getFinalSNP(ipDir, prefix))
    
    #combine all coleected command strings
    jobStr += '; '.join(cmdStrs)

    #create lock.out file indicating completion
    jobStr += "; touch " + currentJobOutFile
    jobStr += "; fi"
    jobStr += "\n"

    return jobStr
 


def snpsJobWriter(ipDir, lockDir, jobsFileName, sequenceName):
    with open(jobsFileName, 'w') as jobsFile:
        bamDirs = getAllBAMDirs(ipDir)
        for bamDir in bamDirs:
            jobStr = getSingleSNPJob(bamDir, lockDir, sequenceName)
            jobsFile.write(jobStr)


    
def main():

    if len(sys.argv) > 4:
        ipDir = getAbsPath(sys.argv[1])
        lockDir = getAbsPath(sys.argv[2])
        sequenceName = getAbsPath(sys.argv[3])
        jobsFileName = sys.argv[4]
        #write the jobs file
        snpsJobWriter(ipDir, lockDir, jobsFileName, sequenceName)
        
    else:
        print 'err: invalid args'


if __name__=='__main__':
    main()
