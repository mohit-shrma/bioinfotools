import sys
import os
import scaffCoordsConv
import contigsCoordsConv
from multiprocessing import Pool
import multiprocessing, logging
import scaffMapPlotter
import mummerOutputConv

def contigWorker((contigsFilePath, minMatchLen)):
    #get contig map for the passed contigs
    refContigsNameLen, queryContigsNameLen, refAdjList, queryAdjList\
        = contigsCoordsConv.parseContigFileNGetMapInfo(contigsFilePath,\
                                                           minMatchLen)
    #try to plot cross minimize ordering     
    contigsCoordsConv.plotCrossMinimizedOrdering(refAdjList, queryAdjList,\
                                                     minMatchLen)
    return True

def callContigWorkers(contigsFilePath, minMatchLenSeq):
    pool = Pool(processes=len(minMatchLenSeq))
    workersArgs = []
    for minMatchLen in minMatchLenSeq:
        workersArgs.append((contigsFilePath, minMatchLen))
    results = pool.map(contigWorker, workersArgs)
    pool.close()
    pool.join()
    return results

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
        scaffMap, scaffsLenDict  = scaffCoordsConv.parseScaffDirNGetMapInfo(scaffsDir,\
                                                                scaffs1FilePath,\
                                                                scaffs2FilePath,\
                                                                minMatchLen)
        #print 'scaffMap: ', scaffMap
        #scaffCoordsConv.plotCrossMinimizedOrdering(scaffMap)

        #get hit counts which are parallel but separated by huge gap
        """conflictedCount, parallelCount, sepParallelCount =\
            scaffCoordsConv.getMultiHitsCountsNDisp(scaffMap, scaffsLenDict)

        print 'conflictedCount: ', conflictedCount
        print 'parallelCount: ', parallelCount
        print 'sepParallelCount: ', sepParallelCount
        """
        #print scaffMap['CGS00426']
        scaffMapPlotter.generateScaffPlot('CGS00144', scaffMap, scaffsLenDict)
        
    elif argLen >= 4:

        #contigs map file path
        mummerFilePath = os.path.abspath(sys.argv[1])

        minMatchLenSeq = int(sys.argv[2])
        minIdentity = int(sys.argv[3])
        
        scaffMap, scaffsLenDict =  mummerOutputConv.getMapAndLen(mummerFilePath,\
                                                                minMatchLenSeq,
                                                                 minIdentity)
        #get hit counts which are parallel but separated by huge gap
        """conflictedCount, parallelCount, sepParallelCount =\
            scaffCoordsConv.getMultiHitsCountsNDisp(scaffMap, scaffsLenDict)

        print 'conflictedCount: ', conflictedCount
        print 'parallelCount: ', parallelCount
        print 'sepParallelCount: ', sepParallelCount
        """
        #print scaffMap['CGS00426']
        #scaffMapPlotter.generateScaffPlot('CGS00426', scaffMap, scaffsLenDict)
        #scaffMapPlotter.generateScaffPlot('CGS00021', scaffMap, scaffsLenDict)
        #scaffMapPlotter.generateScaffPlot('CGS00110', scaffMap, scaffsLenDict)
    else:
        print 'err: files missin'
    



if __name__ == '__main__':
    main()
