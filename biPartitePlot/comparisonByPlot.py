import sys
import os
import scaffCoordsConv
import contigsCoordsConv

def main():

    argLen = len(sys.argv)

    if argLen >= 5:
        #scaffold
        #scaffolds dir
        scaffsDir = os.path.abspath(sys.argv[1])

        #ordering qury/ref below shouldn't matter
        #file path of stats on reference
        scaffs1FilePath = os.path.abspath(sys.argv[2])

        #file path of stats on query
        scaffs2FilePath = os.path.abspath(sys.argv[3])

        #min match length
        minMatchLen = int(sys.argv[4])

        #get scaff map for the passed sequences
        scaffMap = scaffCoordsConv.parseScaffDirNGetMapInfo(scaffsDir,\
                                                                scaffs1FilePath,\
                                                                scaffs2FilePath,\
                                                                minMatchLen)
        
        scaffCoordsConv.plotCrossMinimizedOrdering(scaffMap)
        
    elif argLen >= 3:

        #contigs map file path
        contigsFilePath = os.path.abspath(sys.argv[1])

        #min match length
        minMatchLen = int(sys.argv[2])

        
        #get contig map for the passed contigs
        contigMap = contigsCoordsConv.parseContigFileNGetMapInfo(contigsFilePath,\
                                                                     minMatchLen)
                
        contigsCoordsConv.plotCrossMinimizedOrdering(contigMap)
        
    else:
        print 'err: files missin'
    



if __name__ == '__main__':
    main()
