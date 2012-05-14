import sys
from numpy import *
import pylab as p

def convSamToSNPsIndx():
    pass

"""for the given hits return an array with interval hits"""
def genSNPsHitFreq(snpSIndx, intervalLength, totLength):
    #create an array of zeros of passed length
    intvHits = zeros(totLength)
    for snpInd in snpSIndx:

        start = snpInd - intervalLength + 1
        if start  < 0:
            start = 0
            
        end = snpInd + intervalLength - 1
        if end > totLength - 1:
            end = totLength - 1

        for i in range(start, end+1):
            intvHits[i] += 1

    return intvHits

def getSNPsHitFreqStep(snpSIndx, intervalLength, totLength):
    #create an array of zeros of passed length
    intvHits = zeros(totLength)
    for snpInd in snpSIndx:
       pass 


def doPlot(intvHits, totalLength):
    x = arange(totalLength)
    y = intvHits
    p.ylim((0, 5))
    p.plot(x, y)
    p.show()


def main():
    #test plot sample
    snpsIndx = [2, 4, 5, 10, 15,18,19, 25]
    intvHits = genSNPsHitFreq(snpsIndx, 4, 50)
    print snpsIndx
    print intvHits
    doPlot(intvHits, 50)
    
    """
    if len(sys.argv) >= 1:
        #input data file

    else:
        print 'err: files missing'
    """
if __name__ == '__main__':
    main()
