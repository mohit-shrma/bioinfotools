import sys
from bisect import *


#asuuming sorted unique data in file
def findIntersection(file1, file2, intersFileName = None, nonIntersFileName = None):
    with open(file1, 'r') as file1:
        with open(file2, 'r') as file2:
            file1Data = []
            for line in file1:
                line = line.rstrip('\n')
                file1Data.append(line)
            
            file2Data = []
            for line in file2:
                line = line.rstrip('\n')
                file2Data.append(line)

            file1Data.sort()
            file2Data.sort()

            print 'length of file1: ', len(file1Data)
            print 'length of file2: ', len(file2Data)

            file1Set = set(file1Data)
            file2Set = set(file2Data)
            
            print 'unique File1: ', len(file1Set)
            print 'unique File2: ', len(file2Set)

            intersectSet = file1Set & file2Set
            unionSet = file1Set | file2Set
            
            print 'intersection count: ', len(intersectSet)
            print 'union count: ', len(unionSet)
            
            
            intersect = list(intersectSet)

            #in file1 but not in file2
            nonIntersectSet = file1Set - file2Set
            print 'non intersection count i.e. in 1 but not in 2: ',\
                len(nonIntersectSet)
            nonIntersect = list(nonIntersectSet)
                        
            if intersFileName != None:
                with open(intersFileName, 'w') as intersFile:
                    intersFile.write('\n'.join(intersect))

            if nonIntersFileName != None:
                with open(nonIntersFileName, 'w') as nonIntersFile:
                    nonIntersFile.write('\n'.join(nonIntersect))

            
                    
                    

def main():
    if len(sys.argv) >= 2:
        file1 = sys.argv[1]
        file2 = sys.argv[2]
        intersFileName = None
        nonIntersFileName = None
        if len(sys.argv) >= 4:
            intersFileName = sys.argv[3]
            nonIntersFileName = sys.argv[4]
        findIntersection(file1, file2, intersFileName, nonIntersFileName)
    else:
        print 'err: files missing'

if __name__ == '__main__':
    main()

