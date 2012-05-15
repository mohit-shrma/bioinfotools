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

""" for intervals after each step size plot snps count in mid of interval """
def genSNPsHitFreqMid(snpSIndx, intervalLength, totLength, stepSize):
    #create an array of zeros of passed length
    snpSIndxSet = set(snpSIndx)
    xSeq = []
    ySeq = []
    for snpInd in snpSIndx:
       
       low = snpInd - intervalLength + 1
       hi = snpInd + intervalLength - 1
       if low < 0:
           low = 0
       if hi > totLength - 1:
           hi = totLength - 1

       #in interval low to high move and count
       #find a valid start point, its modulo step size
       if low == 0 or low % stepSize == 0:
           vStart = low
       else:
           vStart = (low + stepSize) - ((low + stepSize)%stepSize)

       #assign freq in intervals from valid start point
       for start in range(vStart, hi+1, stepSize):
           #intervals are from start -> + intervLen - 1
           tempList = range(start, (start + intervalLength - 1) + 1)
           intersection = list(set(tempList) & snpSIndxSet)
           if len(intersection) > 0:
               pointX = float(intersection[0] + intersection[-1]) / 2
               pointY = len(intersection)
               if pointX not in xSeq:
                   xSeq.append(pointX)
                   ySeq.append(pointY)
    return xSeq, ySeq


def genSNPsHitFreqStep(snpSIndx, intervalLength, totLength, stepSize):
    #create an array of zeros of passed length
    intvHits = zeros(totLength)
    snpSIndxSet = set(snpSIndx)
    for snpInd in snpSIndx:
       
       low = snpInd - intervalLength + 1
       hi = snpInd + intervalLength - 1
       if low < 0:
           low = 0
       if hi > totLength - 1:
           hi = totLength - 1
       print snpInd, low, hi

       #in interval low to high move and count
       #find a valid start point, its modulo step size
       if low == 0 or low % stepSize == 0:
           vStart = low
       else:
           vStart = (low + stepSize) - ((low + stepSize)%stepSize)
       #assign freq in intervals from valid start point
       for start in range(vStart, hi+1, stepSize):
           #intervals are from start -> + intervLen - 1
           print start, (start + intervalLength - 1)
           tempList = range(start, (start + intervalLength - 1) + 1)
           intersection = set(tempList) & snpSIndxSet
           if len(intersection) > 0:
               for i in tempList:
                   if intvHits[i] < len(intersection):
                       intvHits[i] = len(intersection)
    return intvHits
           
def doPlot(intvHits, totalLength):
    x = arange(totalLength)
    y = intvHits
    p.ylim((0, 5))
    p.plot(x, y)
    p.show()

def doPlotXY(x, y):
    p.ylim((0, 5))
    p.plot(x, y)
    p.show()


def main():
    #test plot sample
    snpsIndx = [2, 4, 5, 10, 15,18,19, 25]
    print snpsIndx
    x, y = genSNPsHitFreqMid(snpsIndx, 4, 50, 3)
    print x, y
    doPlotXY(x, y)
    
    """
    if len(sys.argv) >= 1:
        #input data file

    else:
        print 'err: files missing'
    """
if __name__ == '__main__':
    main()
