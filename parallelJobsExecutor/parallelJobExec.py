import sys
import os
from subprocess import call, check_call
from subprocess import CalledProcessError
from multiprocessing import Pool
import multiprocessing, logging


""" will execute command passed to it as executing on terminal """
def callShellCmd(commandString):
    retcode = -99
    
    try:
        print 'executing command: ', commandString
        retcode = check_call(commandString, shell=True)
        if retcode == 0:
            #just to follow convention i.e 1 => correctly executed
            return 1

    except OSError, e:
        print >>sys.stderr, "Execution failed: ", e
    except CalledProcessError, e:
        #retcode is not 0
        print >>sys.stderr, "Execution failed: ", e
        print >>sys.stderr, "child returned", e.returncode
        retcode = e.returncode
    sys.stderr.flush()
    sys.stdout.flush()
    return retcode

""" execute the jobs concurrently"""
def callWorkers(jobsFileName, numProcs = 0):
    workersArgs = []
    
    with open(jobsFileName, 'w') as jobsFile:
        for line in jobsFile:
            workersArgs.append(line)

    jobCount = len(workersArgs)

    if numProcs == 0:
        numProcs = jobCount 

    #initialize pool with number of possible jobs
    pool = Pool(processes=numProcs)
    
    results = pool.map(callShellCmd, workersArgs)
    pool.close()
    pool.join()
    return results

                    
def main():

    logger = multiprocessing.log_to_stderr()
    logger.setLevel(multiprocessing.SUBDEBUG)

    if len(sys.argv) >= 1:
        #file containing jobs
        jobsFileName = sys.argv[1]

        #get number of processors
        numProcs = int(sys.argv[2])
        
        #call workers to execute jobs
        results = callWorkers(jobsFileName, numProcs)

        print results
        
    else:
        print 'err: files missing'

if __name__ == '__main__':
    main()
