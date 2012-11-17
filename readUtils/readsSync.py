""" read reads from two fastq files and try to keep them in sync and ignores reads not in pairs"""

import sys
import os
from multiprocessing import Pool



class ReadConsts:
    #read num suffix
    READ_ONE_SUFF = '/1'
    READ_TWO_SUFF = '/2'


#read the reads and put headers in a separate list, returns the sorted list
def getHeadersList(readFileName):
    headerList = []
    with open(readFileName, 'r') as readFile:
        for line in readFile:
            if line.startswith('@'):
                #found header
                # -1 for read suffix number like '\1' and '\2' at end of header 
                headerList.append(line.rstrip('\n')[0:-1])
    headerList.sort()
    #TODO: check for uniqueness of items in this list
    return headerList



#return intersection of two headerlist
def getHeadersIntersection(headers1, headers2):
    return list(set(headers1).intersection(set(headers2)))
    

#parallely search for given headers in both the read file
def parallelReadSearcher(headers, ipRead1Name, opRead1Name, ipRead2Name,\
                             opRead2Name):
    pool = Pool(processes=2)
    workersArgs = []
    #add workers arguments for read1
    workersArgs.append((headers, ipRead1Name, opRead1Name))
    #add workers arguments for read2
    workersArgs.append((headers, ipRead2Name, opRead2Name))
    #pass the list of tasks to concurrent workers
    pool.map(writeSortedReads, workersArgs)
    
    pool.close()
    pool.join()

    

#search for reads in header list in input reads and write it out to output reads
def writeSortedReads((headerList, ipReadName, opReadName)):
    with open(ipReadName, 'r') as ipRead, open(opReadName, 'w') as opRead:

        for header in headerList:
            
            line = ipRead.readline()
            headerFound = False
            
            while line:
                if line.startswith(header):
                    #found read
                    #write header
                    opRead.write(line)
                    #write base
                    opRead.write(ipRead.readline())
                    #write optional line
                    opRead.write(ipRead.readline())
                    #write quality
                    opRead.write(ipRead.readline())
                    #found header
                    headerFound = True
                    break
                else:
                    #skip next 3 lines to go for next header
                    #skip bases
                    ipRead.readline()
                    #skip optinal line
                    ipRead.readline()
                    #skip quality
                    ipRead.readline()
                    
                    #read next header
                    line = ipRead.readline()
                    
            #reset input read file pointer to start of file
            ipRead.seek(0)

            if not headerFound:
                #write out header to conflict file
                print 'Not found: ', header

                
                
#write the list of headers to the given file
def printHeaders(headers, opFileName):
    with open(opFileName, 'w') as opFile:
        for header in headers:
            opFile.write(header+'\n')

            

def main():
    argLen = len(sys.argv)
    if argLen >= 4:

        ipRead1Name = sys.argv[1]
        ipRead2Name = sys.argv[2]
        opRead1Name = sys.argv[3]
        opRead2Name = sys.argv[4]
        confRead1Name = sys.argv[5]
        confRead2Name = sys.argv[6]

        #get the headers of first read
        headers1 = getHeadersList(ipRead1Name)

        #get the headers of second read
        headers2 = getHeadersList(ipRead2Name)

        #get the common headers in between two headers
        commonHeaders = getHeadersIntersection(headers1, headers2)        
        commonHeaders.sort()

        #print out the headers of absent reads in read1,\
        #i.e reads present in read2 but not in read1
        notRead1ButRead2 = list(set(headers2) - set(headers1))
        printHeaders(notRead1ButRead2, confRead1Name)
        
        #print out the headers of absent reads in read2,\
        #i.e reads present in read2 but not in read2
        notRead2ButRead1 = list(set(headers2) - set(headers2))
        printHeaders(notRead2ButRead1, confRead2Name)
        
        #use common headers to filter out the reads
        parallelReadSearcher(commonHeaders, ipRead1Name, opRead1Name,\
                                 ipRead2Name, opRead2Name)
        
        
    else:
        print 'err: less num of args passed'

if __name__ == '__main__':
    main()
