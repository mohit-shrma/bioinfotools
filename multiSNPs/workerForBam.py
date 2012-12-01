import sys
import os
from subprocess import call

#get the read name from the read path
def getLibraryName(readLibraryPath):
    return ((readLibraryPath.split('/')[-1]).split('.'))[0]

#check the existence if exists of fastq file in outDir
def checkIfFastQExists(fileNamePrefix, fileExt, outDir):
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


#a dictionary of all tools being used
def getToolsDict():
    tools = {}
    tools['BWA'] = "/home/koronis/mohit/programs/bwa-0.6.1/bwa"
    tools['FASTQDUMP_CMD'] = "/home/koronis/mohit/programs/sratoolkit.2.1.0-ubuntu32/fastq-dump"
    tools['SAMTOOLS'] = "/home/koronis/mohit/programs/samtools-0.1.18/samtools"
    tools['UNIQUESAMPL'] = "/home/koronis/mohit/programs/pull_Unique_reads.pl"
    tools['PICARD_TOOLS'] ="/home/koronis/mohit/programs/picard-tools-1.68"
    tools['GENOME_ANALYSIS_TK_JAR'] = "/home/koronis/mohit/programs/GenomeAnalysisTK/GenomeAnalysisTK.jar"
    tools['VARSCAN_JAR'] = "/home/koronis/mohit/programs/varscan/VarScan.v2.2.10.jar"
    tools['PARALLEL_DRONE'] = "mpiexec_mpt -np 96 /home/koronis/mohit/programs/Drone/Drone "
    return tools

#a dictionary of all possible extensions
def getExtDict():
    extensions = {}
    extensions['READS_EXT'] = ".lite.sra"
    extensions['READS_PREFIX'] = "SRR"
    extensions['SCAFF_EXT'] = ".fasta"
    extensions['FASTQ_EXT'] = ".fastq"
    extensions['SAI_EXT'] = ".sai"
    extensions['SAM_EXT'] = ".sam"
    extensions['BAM_EXT'] = ".bam"
    extensions['SORT_BAM_EXT'] = ".sorted"
    extensions['UNIQ_SAM_EXT'] = "_Unique.sam"
    extensions['SAM_INFO_EXT'] = "_info.txt"
    extensions['UNIQ_BAM_EXT'] = "_Unique.bam"
    extensions['UNIQ_SORT_BAM_EXT'] = "_Unique.sorted"               
    return extensions

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
            if retcode == 0 and checkIfFastQExists(libName, getExtDict()['FASTQ_EXT'], outDir):
                return 1
            else:
                return 0
    except OSError, e:
        print >>sys.stderr, "Execution failed: ", e
    return retcode


#call the parallel drone program to process the multiple jobs file
def callParallelDrone(jobsFilePath, parallelDrone):
    #call parallel Drone program
    retcode = -99
    try:
        retcode = call(parallelDrone  + " " + jobsFilePath, shell=True)
        if retcode < 0:
            print >>sys.stderr, "child terminated by signal", -retcode
        else:
            print >>sys.stderr, "child returned", retcode
    except OSError, e:
        print >>sys.stderr, "Execution failed: ", e
    return retcode
        

def getScaffoldName(scaffName):
    return ''.join((scaffName.split('.'))[:-1])

#get all fastas from a given directory
def getAllFastas(scaffDir):
    dirContents = os.listdir(scaffDir)
    scaffDirs = [ name for name in dirContents if os.path.isdir(\
                                                 os.path.join(scaffDir, name)\
                                                     ) ]
    return scaffDirs

#get all fastQ files for a read from outDirectory
def getAllFastQs(outDir, libName):
    fastQExt = '.fastq'
    dirContents = os.listdir(outDir)
    fastQFiles = []
    for name in dirContents:
        if os.path.isfile(os.path.join(outDir, name)) and\
                name.startswith(libName) and name.endswith(fastQExt):
           fastQFiles.append(name)
    return fastQFiles


#write a job for a given scaffold and read to a unique sorted bam file
def writeJob(jobsFile, fastaFilePath, fastQFilePath, lockDirPath, tools):

    extensions = getExtDict()
    
    #fastq file name
    fastQFileName = (fastQFilePath.split('/')[-1]).rstrip(extensions['FASTQ_EXT'])

    #fasta file name
    fastaFileName = (fastaFilePath.split('/')[-1]).rstrip(extensions['SCAFF_EXT'])

    #fasta dir
    fastaDir = '/'.join(fastaFilePath.split('/')[:-1]) + '/'
    
    #job lock file path for current job
    currentJobLockFile = lockDirPath + fastQFileName + fastaFileName 

    #check for  lock file in case current job is already executed
    jobsFile.write("if [ -f " + currentJobLockFile  \
                       + ".lock ]; then echo \"" \
                       + currentJobLockFile  \
                       +" done\"; exit 0; ")
 
    #check if job is already finished
    jobsFile.write("elif [ -f " + currentJobLockFile \
                       + ".out ]; then echo \"" \
                       + currentJobLockFile \
                       +" done\"; exit 0;  ")
    jobsFile.write("else ")
    #need to execute job

    #write lock file b4 executing job
    jobsFile.write("touch "+currentJobLockFile+".lock; ")

    #write statements for processing job

    #change directory to scaffold where we are working
    jobsFile.write("cd "+ fastaDir+"; ")

    #Burrow wheel aligner processing
    
    #generate index, do following separately as this is for scaffold,
    #not for read
    #jobsFile.write(tools['BWA'] +" index -a bwtsw -p "\
    #                   + fastaFileName + extensions['SCAFF_EXT'] \
    #                   + " " + fastaFilePath + "; ")


    #generate SAI, 10 threads used for generation
    jobsFile.write(tools['BWA'] +" aln -t 24 -n 3 -l 1000000 -o 1 -e 5 "\
                       + fastaFileName + extensions['SCAFF_EXT'] \
                       + " " + fastQFilePath + " > "\
                       + fastQFileName+extensions['SAI_EXT'] +"; ")

    #generate SAM file for SAI
    jobsFile.write(tools['BWA'] + " samse -n 15 " \
                       + fastaFileName + extensions['SCAFF_EXT']\
                       + " " + fastQFileName + extensions['SAI_EXT']\
                       + " " + fastQFilePath + " >" \
                       + " " + fastQFileName + extensions['SAM_EXT'] + "; ")
    

    #convert to unique sam with info
    jobsFile.write("perl "+ tools['UNIQUESAMPL']\
                   + " " + fastaDir + fastQFileName + extensions['SAM_EXT']\
                   + " " + fastaDir + fastQFileName + extensions['UNIQ_SAM_EXT']\
                   + " " + fastaDir + fastQFileName + extensions['SAM_INFO_EXT']\
                   + "; ")

    #convert to BAM
    jobsFile.write(tools['SAMTOOLS'] +" view -bS -q 30 "\
                   + " " + fastaDir + fastQFileName + extensions['UNIQ_SAM_EXT']\
                   + " > " + fastaDir + fastQFileName + extensions['UNIQ_BAM_EXT']\
                   + "; ")

    #convert to sorted bam
    jobsFile.write(tools['SAMTOOLS'] +" sort "\
                   + " " + fastaDir + fastQFileName  + extensions['UNIQ_BAM_EXT']\
                   + " " + fastaDir + fastQFileName + extensions['UNIQ_SORT_BAM_EXT']\
                   + " ")

    
    #create lock.out file indicating completion
    jobsFile.write("; touch " + currentJobLockFile  + ".out ")
    jobsFile.write("; fi")
    jobsFile.write("\n")




#write a job for a given scaffold and single read "SAI"  to a bam file
def writeSAIIToBAMJob(jobsFile, fastaFilePath, fastQFilePath, lockDirPath, tools):

    extensions = getExtDict()
    
    #fastq file name
    fastQFileName = (fastQFilePath.split('/')[-1]).rstrip(extensions['FASTQ_EXT'])

    #fasta file name
    fastaFileName = (fastaFilePath.split('/')[-1]).rstrip(extensions['SCAFF_EXT'])

    #fasta dir
    fastaDir = '/'.join(fastaFilePath.split('/')[:-1]) + '/'
    
    #job lock file path for current job
    currentJobLockFile = lockDirPath + fastQFileName + fastaFileName 

    #check for  lock file in case current job is already executed
    jobsFile.write("if [ -f " + currentJobLockFile  \
                       + ".lock ]; then echo \"" \
                       + currentJobLockFile  \
                       +" done\"; exit 0; ")
 
    #check if job is already finished
    jobsFile.write("elif [ -f " + currentJobLockFile \
                       + ".out ]; then echo \"" \
                       + currentJobLockFile \
                       +" done\"; exit 0;  ")
    jobsFile.write("else ")
    #need to execute job

    #write lock file b4 executing job
    jobsFile.write("touch "+currentJobLockFile+".lock; ")

    #write statements for processing job

    #change directory to scaffold where we are working
    jobsFile.write("cd "+ fastaDir+"; ")

    #Burrow wheel aligner processing
    
    #generate index, do following separately as this is for scaffold,
    #not for read
    #jobsFile.write(tools['BWA'] +" index -a bwtsw -p "\
    #                   + fastaFileName + extensions['SCAFF_EXT'] \
    #                   + " " + fastaFilePath + "; ")


    #assuming SAI is already generated

    #generate SAM file for SAI
    jobsFile.write(tools['BWA'] + " samse -n 15 " \
                       + fastaFileName + extensions['SCAFF_EXT']\
                       + " " + fastQFileName + extensions['SAI_EXT']\
                       + " " + fastQFilePath + " >" \
                       + " " + fastQFileName + extensions['SAM_EXT'] + "; ")
    

    #convert to unique sam with info
    jobsFile.write("perl "+ tools['UNIQUESAMPL']\
                   + " " + fastaDir + fastQFileName + extensions['SAM_EXT']\
                   + " " + fastaDir + fastQFileName + extensions['UNIQ_SAM_EXT']\
                   + " " + fastaDir + fastQFileName + extensions['SAM_INFO_EXT']\
                   + "; ")

    #convert to BAM
    jobsFile.write(tools['SAMTOOLS'] +" view -bS -q 30 "\
                   + " " + fastaDir + fastQFileName + extensions['UNIQ_SAM_EXT']\
                   + " > " + fastaDir + fastQFileName + extensions['UNIQ_BAM_EXT']\
                   + "; ")

    #convert to sorted bam
    jobsFile.write(tools['SAMTOOLS'] +" sort "\
                   + " " + fastaDir + fastQFileName  + extensions['UNIQ_BAM_EXT']\
                   + " " + fastaDir + fastQFileName + extensions['UNIQ_SORT_BAM_EXT']\
                   + " ")

    
    #create lock.out file indicating completion
    jobsFile.write("; touch " + currentJobLockFile  + ".out ")
    jobsFile.write("; fi")
    jobsFile.write("\n")

    
#write a job to combine paired reads and corresponding sai to bam
def writePairedSAIToBAMJob(jobsFile, fastaFilePath, pairedReadTuple,\
                               lockDirPath, tools):
    extensions = getExtDict()

    #first read of pair
    read1FilePath = pairedReadTuple[0]

    #second read of pair
    read2FilePath = pairedReadTuple[1]

    #read1 file name
    read1Name = (read1FilePath.split('/')[-1]).rstrip(extensions['FASTQ_EXT'])

    #read2 file name
    read2Name = (read2FilePath.split('/')[-1]).rstrip(extensions['FASTQ_EXT'])

    #get the common prefix for both read
    pairName = getCommonPrefix(read1Name, read2Name) 
    
    #fasta file name
    fastaFileName = (fastaFilePath.split('/')[-1]).rstrip(extensions['SCAFF_EXT'])

    #fasta dir
    fastaDir = '/'.join(fastaFilePath.split('/')[:-1]) + '/'
    
    #job lock file path for current job
    currentJobLockFile = lockDirPath + pairName + fastaFileName 

    #check for  lock file in case current job is already executed
    jobsFile.write("if [ -f " + currentJobLockFile  \
                       + ".lock ]; then echo \"" \
                       + currentJobLockFile  \
                       +" done\"; exit 0; ")
 
    #check if job is already finished
    jobsFile.write("elif [ -f " + currentJobLockFile \
                       + ".out ]; then echo \"" \
                       + currentJobLockFile \
                       +" done\"; exit 0;  ")
    jobsFile.write("else ")
    #need to execute job

    #write lock file b4 executing job
    jobsFile.write("touch "+currentJobLockFile+".lock; ")

    #write statements for processing job

    #change directory to scaffold where we are working
    jobsFile.write("cd "+ fastaDir+"; ")

    #Burrow wheel aligner processing
    
    #generate index, do following separately as this is for scaffold,
    #not for read
    #jobsFile.write(tools['BWA'] +" index -a bwtsw -p "\
    #                   + fastaFileName + extensions['SCAFF_EXT'] \
    #                   + " " + fastaFilePath + "; ")


    #assuming SAI file is alredy generated for both the reads
    
    #generate SAM file for both SAI
    jobsFile.write(tools['BWA'] + " sampe -n 15 " \
                       + fastaFileName + extensions['SCAFF_EXT']\
                       + " " + read1Name + extensions['SAI_EXT']\
                       + " " + read2Name + extensions['SAI_EXT']\
                       + " " + read1FilePath + " >" \
                       + " " + read2FilePath + " >" \
                       + " " + pairName + extensions['SAM_EXT'] + "; ")
    
    #generate bam file for sam
    jobsFile.write(tools['SAMTOOLS'] +" view -bS -q 30 "\
                   + " " + fastaDir + pairName + extensions['SAM_EXT']\
                   + " > " + fastaDir + pairName + extensions['BAM_EXT']\
                   + "; ")

    #convert to sorted bam
    jobsFile.write(tools['SAMTOOLS'] +" sort "\
                   + " " + fastaDir + pairName  + extensions['BAM_EXT']\
                   + " " + fastaDir + pairName + extensions['SORT_BAM_EXT']\
                   + " ")
    
    #create lock.out file indicating completion
    jobsFile.write("; touch " + currentJobLockFile  + ".out ")
    jobsFile.write("; fi")
    jobsFile.write("\n")
    


#find common prefix string between two reads
def getCommonPrefix(name1, name2):
    commonPrefix = ''
    for i in range(len(name1)):
        if name1[i] == name2[i]:
            commonPrefix += name1[i]
        else:
            break
    return commonPrefix


    

#write a job for a given scaffold and read to a sai file
def writeSAIJob(jobsFile, fastaFilePath, fastQFilePath, lockDirPath, tools):

    extensions = getExtDict()
    
    #fastq file name
    fastQFileName = (fastQFilePath.split('/')[-1]).rstrip(extensions['FASTQ_EXT'])

    #fasta file name
    fastaFileName = (fastaFilePath.split('/')[-1]).rstrip(extensions['SCAFF_EXT'])

    #fasta dir
    fastaDir = '/'.join(fastaFilePath.split('/')[:-1]) + '/'
    
    #job lock file path for current job
    currentJobLockFile = lockDirPath + fastQFileName + fastaFileName 

    #check for  lock file in case current job is already executed
    jobsFile.write("if [ -f " + currentJobLockFile  \
                       + ".lock ]; then echo \"" \
                       + currentJobLockFile  \
                       +" done\"; exit 0; ")
 
    #check if job is already finished
    jobsFile.write("elif [ -f " + currentJobLockFile \
                       + ".out ]; then echo \"" \
                       + currentJobLockFile \
                       +" done\"; exit 0;  ")
    jobsFile.write("else ")
    #need to execute job

    #write lock file b4 executing job
    jobsFile.write("touch "+currentJobLockFile+".lock; ")

    #write statements for processing job

    #change directory to scaffold where we are working
    jobsFile.write("cd "+ fastaDir+"; ")

    #Burrow wheel aligner processing
    
    #generate index, do following separately as this is for scaffold,
    #not for read
    #jobsFile.write(tools['BWA'] +" index -a bwtsw -p "\
    #                   + fastaFileName + extensions['SCAFF_EXT'] \
    #                   + " " + fastaFilePath + "; ")


    #generate SAI, 10 threads used for generation
    jobsFile.write(tools['BWA'] +" aln -t 10 -n 3 -l 1000000 -o 1 -e 5 "\
                       + fastaFileName + extensions['SCAFF_EXT'] \
                       + " " + fastQFilePath + " > "\
                       + fastQFileName+extensions['SAI_EXT'] +"; ")


    
    #create lock.out file indicating completion
    jobsFile.write("; touch " + currentJobLockFile  + ".out ")
    jobsFile.write("; fi")
    jobsFile.write("\n")

    

""" defines the worker functionality for a particular read library and 
fasta files present in directory path fastapath, also specified are outDir
to which all fastq's are written and jobs too lockDir to keep track of locks """
def workerToGenBAM(readLibraryPath, outDir, lockDirPath, fastaPath):

    #extract library name
    libName = getLibraryName(readLibraryPath)

    #get all tools
    tools = getToolsDict()
    
    #generate fastQ's for this read library
    fastQStatus = generateFastQ(readLibraryPath, outDir, \
                                      tools['FASTQDUMP_CMD'])
    if fastQStatus != 1:
        #some error occured
        print "fastqstatus erred"
        return -1
    
    #write a file containing multiple jobs for each fasta
    fastQJobsFileName = libName + "Jobs.jobs"

    try:
        fastQJobFile = open(outDir+'/'+fastQJobsFileName, 'w')

        #get name of all fastq Files inside outDir
        fastQFiles = getAllFastQs(outDir, libName)
        
        #fastaPath contains all .fasta inside a dir with same name as fasta
        #get all fasta name without ext ".fasta" in a list
        fastaDirs = getAllFastas(fastaPath)

        for fastaDir in fastaDirs:
            #get fasta File Path        
            fastaFilePath = fastaPath + fastaDir + "/" + fastaDir + ".fasta"
            for fastQFile in fastQFiles:
                fastQFilePath = outDir + fastQFile
                writeJob(fastQJobFile, fastaFilePath, fastQFilePath,\
                             lockDirPath, tools)
        fastQJobFile.close()
    except IOError as (errno, strerror):
        print "I/O error({0}): {1}".format(errno, strerror)        
        return -1

    return 1
