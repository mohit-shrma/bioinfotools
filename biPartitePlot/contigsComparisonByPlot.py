import sys
import os
import contigsCoordsConv
import scaffMapPlotter


def main():
    if len(sys.argv) >= 4:
        
        #contigMapFile
        contigMapFilePath = os.path.abspath(sys.argv[1])
        
        #min match length
        minMatchLen = int(sys.argv[2])

        #plot outputfile
        plotOutFilePath = os.path.abspath(sys.argv[3])
        
        #get scaff map for the passed sequences
        contigMap = contigsCoordsConv.parseContigFileNGetMapInfo(contigMapFilePath)
        #generate plot for scaff map
        scaffMapPlotter.generatePlot(contigMap, minMatchLen, plotOutFilePath)
        
    else:
        print 'err: files missin'

if __name__ == '__main__':
    main()
