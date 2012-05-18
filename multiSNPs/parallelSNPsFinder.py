import os
import sys
from subprocess import call

import workerForBam

#write a job for given scaffold to a jobFile
def writeJob(jobsFile, fastaFilePath, lockDirPath, tools):

    extensions = getExtDict()

    #fasta file name
    fastaFileName = (fastaFilePath.split('/')[-1]).split('.')[0]

    #fasta dir
    fastaDir = '/'.join(fastaFilePath.split('/')[:-1]) + '/'

    #job lock file path for current job
    currentJobLockFile = lockDirPath + "SNPS" + fastaFileName 

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

    #built fasta sequence dictionary
    jobsFile.write("java -Xms2048m -jar " + tools['PICARD_TOOLS']\
                       + "/CreateSequenceDictionary.jar R=" + fastaFilePath\
                       + "O=" + fastaDir + fastaFileName +".dict; ")

    #merge all bams for this scaffold into single bama
    jobsFile.write(tools['SAMTOOLS'] + " merge "\
                       + fastaDir + fastaFileName + extensions[SORT_BAM_EXT]\
                       + fastaDir + fastaFileName + "*_Unique.bam; ")

    #add or replace read groups
    jobsFile.write("java -Xms2048m -jar " + tools['PICARD_TOOLS']\
                       + "/AddOrReplaceReadGroups.jar I="\
                       + fastaDir + "/" + fastaFileName\
                       + extensions['SORT_BAM_EXT'] + " O="\
                       + fastaDir + "/" + fastaFileName + "_picard2.sorted.bam"\
                       + " SORT_ORDER=coordinate RGLB=1 RGPL=illumina RGPU=bar" \
                       + " RGSM=BMGC VALIDATION_STRINGENCY=LENIENT"\
                       + " CREATE_INDEX=TRUE; ")

    #reorder SAM
    jobsFile.write("java -Xms2048m -jar " + tools['PICARD_TOOLS']\
                       + "/ReorderSam.jar I="\
                       + fastaDir + "/" + fastaFileName + "_picard2.sorted.bam"\
                       + " O="+fastaDir + "/" + fastaFileName\
                       + "_picard3.sorted.bam " + "REFERENCE="+fastaFilePath\
                       + " VALIDATION_STRINGENCY=LENIENT CREATE_INDEX=TRUE; ")

    #genome analysis tK realigner target creator
    jobsFile.write("java -Xms2048m -jar " + tools['GENOME_ANALYSIS_TK_JAR']\
                       + " -T RealignerTargetCreator -R " + fastaFilePath\
                       + " -I " + fastaDir + "/" + fastaFileName
                       + "_picard3.sorted.bam -o " + fastaDir + fastaFileName +\
                       + ".intervals; ")

    #genome analysis tK indel realigner
    jobsFile.write("java -Xms2048m -jar " + tools['GENOME_ANALYSIS_TK_JAR']\
                       + " -T IndelRealigner -R " + fastaFilePath\
                       + " -I " + fastaDir + "/" + fastaFileName\
                       + "_picard3.sorted.bam -targetIntervals "\
                       +  fastaDir + fastaFileName\
                       + ".intervals -o " + fastaDir + fastaFileName\
                       + "_gatkrealigned.sorted.bam; ")
    
    #sangerq sorted bam
    #TODO: where is sangerq used
    jobsFile.write(tools['SAMTOOLS'] + " view -h " + fastaDir + fastaFileName\
                       + "_gatkrealigned.sorted.bam | perl -lane '$\"=\"\\t\";"\
                       + " if (/^@/) {print;} else {$F[10]=~ tr/\\x40-\\xff"\
                       + "\\x00-\\x3f/\\x21-\\xe0\\x21/;print \"@F\"}' | )"\
                       + tools['SAMTOOLS'] + " view -Sbh - > " + fastaDir\
                       + fastaFileName + "_gatkrealigned_sangerQ.sorted.bam; ")

    #mpileup generation
    jobsFile.write(tools['SAMTOOLS'] + " mpileup -BQ0 -d10000000 -f "\
                       + fastaFilePath + " " + fastaDir + fastaFileName\
                       + "_gatkrealigned.sorted.bam > " + fastaDir\
                       + fastaFileName +"_gatkrealigned.mpileup; ")

    #use varscan to make realigned cns
    jobsFile.write("java -jar " + tools['VARSCAN_JAR'] +" mpileup2cns "\
                       + fastaDir + fastaFileName +"_gatkrealigned.mpileup"\
                       + " --min-coverage 8 --min-reads2 3 --min-avg-qual 20"\
                       + " --min-var-freq 0.01 --p-value 0.99 --strand-filter"\
                       + " 0 --variants 1 > " + fastaDir + fastaFileName\
                       + "_realigned.cns; ")

    #generate indels
    jobsFile.write("java -jar " + tools['VARSCAN_JAR'] + " mpileup2indel "\
                       + fastaDir + fastaFileName + "_gatkrealigned.mpileup"\
                       + " --min-coverage 8 --min-reads2 3 --min-avg-qual 20"\
                       + " --min-var-freq 0.01 --p-value 0.99 --strand-filter 0"\
                       + " --variants 1 > " + fastaDir + fastaFileName\
                       + "_realigned2.indel; ")

    #rename mpileup to pileup
    jobsFile.write("mv " + fastaDir + fastaFileName + "_gatkrealigned.mpileup "\
                       + fastaDir + fastaFileName + "_gatkrealigned.pileup; ")

    #pileup to SNP
    jobsFile.write("java -jar " + tools['VARSCAN_JAR'] + " pileup2snp "\
                       + fastaDir + fastaFileName + "_gatkrealigned.pileup"\
                       + "  --min-coverage 8 --min-reads2 3 --min-avg-qual 20"\
                       + " --min-var-freq 0.01 --p-value 0.99 > "\
                       + fastaDir + fastaFileName + "_realigned3.snp; ")
                   
                   
    #create lock.out file indicating completion
    jobsFile.write("; touch " + currentJobLockFile  + ".out ")
    jobsFile.write("; fi")
    jobsFile.write("\n")




""" find snps for the pre processesd scaffold folder containing sorted BAMs
fastaDir - folder containing scafoold folders
outDir - place where jobs file will be written for execution by drone
"""
def snpsFinder(fastaPath, outDir, lockDirPath):

    #get all tools
    tools = getToolsDict()

    #get all scaffold folder names inside fasta dir
    fastaDirs = workerForBam.getAllFastas(fastaPath)

    #file containing snpfinder job for each scaffold
    snpsFinderJobFileName = fastaPath.split('/')[-1]+"Jobs.jobs"

    try:
        #open the snpsFinderJob file
        snpsFinderJobFile = open(snpsFinderJobFileName, 'w')

        for fastaDir in fastaDirs:
            #get fasta file path
            fastaFilePath = fastaPath + fastaDir + "/" + fastaDir + ".fasta"
            writeJob(snpsFinderJobFile, fastaFilePath, lockDirPath, tools):
        snpsFinderJobFile.close()    
        
    except IOError as (errno, strerror):
        print "I/O error({0}): {1}".format(errno, strerror)        
        return -1

    #execute the wrote jobs through DRONE parallely
    retCode = workerForBam.callParallelDrone( outDir+'/'+snpsFinderJobFileName,\
                                                  tools['PARALLEL_DRONE'])
    if retCode != 1:
        #error occured while calling parallel drone
        print "parallel drone erred"
        return -1
    return 1


        
        

