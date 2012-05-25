import sys
import os
import scaffCoordsConv
import scaffMapPlotter


def main():
    if len(sys.argv) >= 6:

        #scaffolds dir
        scaffsDir = os.path.abspath(sys.argv[1])

        #ordering qury/ref below shouldn't matter
        #file path of stats on reference
        scaffs1FilePath = os.path.abspath(sys.argv[2])

        #file path of stats on query
        scaffs2FilePath = os.path.abspath(sys.argv[3])

        #min match length
        minMatchLen = int(sys.argv[4])

        #plot outputfile
        plotOutFilePath = os.path.abspath(sys.argv[5])
                
        #get scaff map for the passed sequences
        (scaffMap, refListRange, coordScaffDict) = scaffCoordsConv.parseScaffDirNGetMapInfo(scaffsDir,\
                                                            scaffs1FilePath,\
                                                            scaffs2FilePath)
        #do iteration of plot and flip
        scaffCoordsConv.iteratePlotFlip(scaffMap, refListRange, coordScaffDict, minMatchLen)
        
        #generate plot for scaff map
        #scaffMapPlotter.generatePlot(scaffMap, minMatchLen, plotOutFilePath)
        
    else:
        print 'err: files missin'

if __name__ == '__main__':
    main()
