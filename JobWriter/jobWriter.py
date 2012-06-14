import sys
import re
import os

"""TODO: divide this module into methods and accept as commandline \
argument which type of output needed i.e dotplot, output.txt or .maf.
Also commandline arg for --exact= parameter"""

def getFileName(filePath):
    pattern = re.compile('(\w+)\.?(\w+)?$')
    match = pattern.search(filePath)
    if match is not None:
        return match.group()
    else:
        #couldn't match, return the last part after '/'
        return match.group(1)

def jobWriter(allArgDict):
    
    #file path containing scaffolds list
    scaffoldsListFile = os.path.abspath(allArgDict['ip'])

    #file path to write the jobs into
    jobsOutFileName = os.path.abspath(allArgDict['op'])

    #directory to write the job output
    jobsOutDirPath = os.path.abspath(allArgDict['outDir'])
    if not jobsOutDirPath.endswith('/'):
        jobsOutDirPath += '/'

    #directory to write the job locks
    jobsLockDir = os.path.abspath(allArgDict['lockDir'])
    if not jobsLockDir.endswith('/'):
        jobsLockDir += '/'

    
    #second scaffolds or query File
    secondScaffoldFilePath = os.path.abspath(allArgDict['query'])

    try:
        #read the files list and add the file paths into a list
        inListFile = open(scaffoldsListFile, "r")

        #list containing scaffold file paths
        scaffoldFilePaths = []

        if inListFile:
            scaffoldFilePaths = [line.rstrip('\n') for line in inListFile]
            #print scaffoldFilePaths
            inListFile.close()
            
        jobsOutFile = open(jobsOutFileName, "w")
        
        if jobsOutFile:
            #write a job for each file in list
            for scaffoldFile in scaffoldFilePaths:

                scaffoldFileName = getFileName(scaffoldFile)
                
                #job lock file path(incl. name) for current job
                currentJobLockFile = jobsLockDir + scaffoldFileName

                #job out file path(incl. name) for current job
                currentJobOPFile = jobsOutDirPath + scaffoldFileName

                """check for  lock file in case current job is already being
                executed"""
                jobsOutFile.write("if [ -f " + currentJobLockFile  \
                                      + ".lock ]; then echo \"" \
                                      + currentJobLockFile  \
                                      +" done\"; exit 0; ")

                #check if job is already finished
                #TODO: find scenario when it will actually come to this point?
                jobsOutFile.write("elif [ -f " + currentJobLockFile \
                                      + ".out ]; then echo \"" \
                                      + currentJobLockFile \
                                      +" done\"; exit 0;  ")
                jobsOutFile.write("else ")
                #need to execute jobs

                #write lock file b4 executing job
                jobsOutFile.write("touch "+currentJobLockFile+".lock; ")

                #write job processing statements
                #jobsOutFile.write("cd /project/huws/huwsgroup/Nitya/Hyacinth/lastz-distrib-1.02.00/src/;")
                jobsOutFile.write("/home/koronis/mohit/programs/lastz/lastz-distrib/bin/lastz " \
                                      + scaffoldFile + " " + secondScaffoldFilePath + " ")

                jobsOutFile.write("--step=20 --seed=match12 --notransition "\
                                      + " --ambiguous=n  --ambiguous=iupac --gfextend ")
                
                if 'strict' in allArgDict:
                    jobsOutFile.write("--match=1,5  --nogapped --nochain ")
                else:
                    jobsOutFile.write("--identity=97 --gapped --chain ")

                #find equivalent of dictionary exists
                if 'exact' in allArgDict:
                    jobsOutFile.write("--exact="+allArgDict['exact']+" ")
                else:
                    jobsOutFile.write("--mismatch=30,1000 ")

                if 'rdotplot' in allArgDict:
                    jobsOutFile.write("--rdotplot=" + currentJobOPFile + ".dotplot ")
                    
                if 'format' in allArgDict:
                    jobsOutFile.write("--format=" + allArgDict['format'] + " ")
                else:
                    jobsOutFile.write("--format=general ")

                    
                jobsOutFile.write("--output=" + currentJobOPFile + ".out ")

                #create lock.out file indicating completion
                jobsOutFile.write("; touch " + currentJobLockFile  + ".out ")
                jobsOutFile.write("; fi")
                jobsOutFile.write("\n")

            jobsOutFile.close()
    except IOError as (errno, strerror):
        print "I/O error({0}): {1}".format(errno, strerror)
    except:
        print "unexpected error:", sys.exc_info()[0]
    

