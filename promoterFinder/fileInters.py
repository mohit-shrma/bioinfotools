import sys
from bisect import *


#asuuming sorted unique data in file
def findIntersection(file1, file2):
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

            intersect = []
            
            for word in file1Data:
                #search word in another sorted file
                i = bisect_left(file2Data, word)
                if i != len(file2Data) and file2Data[i] == word:
                    #word found in another file
                    intersect.append(word)
            print '\n'.join(intersect)
                    
                    

def main():
    if len(sys.argv) >= 2:
        file1 = sys.argv[1]
        file2 = sys.argv[2]
        findIntersection(file1, file2)
    else:
        print 'err: files missing'

if __name__ == '__main__':
    main()

