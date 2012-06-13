"""jobWriterMain.py usage
python jobWriterMain.py --rdotplot --format=<general/maf+> --exact=<40> \
--query=<path to query scaffold> --strict \
--lockDir=<lock directory to keep lock files> \
--outDir=<directory to store output> <ipfile containing scaffolds path> \
<opfile to which combined job will be written>
"""
import sys
import getopt

import jobWriter

class Usage(Exception):
    def __init__(self, msg):
        self.msg = msg



""" main module \
it parse commandline args and pass them to other module to do the job\
some options are as follow :
-rdotplot : whether dotplot output shud be generated or not
--format=<genearal/maf+>
--exact=<40>
--query=<path to query scaffold>
--strict : penalise mismatch more, no gaps, no chain 
--lockDir=<lock directory to keep lock files> \
--outDir=<directory to store output>
arguments as follow:
first arg: i/p file containing reference scaffold paths
"""

def main(argv = None):
    if argv is None:
        argv = sys.argv
    try:
        try:
            opts, args = getopt.getopt(sys.argv[1:], "h", \
                                           ["help", "rdotplot", \
                                            "format=", "exact=",\
                                            "strict", "query=", \
                                            "lockDir=", "outDir="])
        except getopt.error, msg:
            raise Usage(msg)

        #use enum equivalent to store string constant
        allArgDict = {}
        
        #process options
        for o, a in opts:
            if o == "--rdotplot":
                #need to give dotplot output
                allArgDict['rdotplot'] = True 
            elif o in ("-s", "--strict"):
                #use strict group of options
                allArgDict['strict'] = True
            elif o in ("-e", "--exact"):
                #how much exact bp
                allArgDict['exact'] = a
            elif o in ("-f", "--format"):
                #output file format
                allArgDict['format'] = a
            elif o in ("-q", "--query"):
                #scaffold which will be queried
                allArgDict['query'] = a
            elif o in ("--lockDir"):
                #directory to keep lock files
                allArgDict['lockDir'] = a
            elif o in ("--outDir"):
                #directory where output will be kept
                allArgDict['outDir'] = a
            elif o in ("-h", "--help"):
                print __doc__
                return 0    
                
        #process arguments
        #for arg in args:
        #    ipFilePath = arg
        if len(args) > 1:
            allArgDict['ip'] = args[0]
            allArgDict['op'] = args[1]
        else:
            #handle else case
            raise(Usage("missed i/p o/p file"))
            
        #process formed dictionary if have all min. required arguments
        #else raise error
        requiredParams = set(['ip', 'op', 'lockDir', 'outDir', 'query'])
        keysSet = set(allArgDict.keys())
        diff = requiredParams - keysSet

        print 'DEBUG: passed: ', keysSet, 'required: ', requiredParams

        if len(diff) != 0:
            #missed out on a required param
            raise Usage("missed out a required parameter")
        
        #pass the dict to job writer module    
        jobWriter.jobWriter(allArgDict)
        
        return 0
        
    except Usage, err:
        print >>sys.stderr, err.msg
        print >>sys.stderr, "for help use --help"
        return 2

if __name__ == "__main__":
    sys.exit(main())
