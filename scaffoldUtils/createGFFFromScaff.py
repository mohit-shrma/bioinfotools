""" creates gff file for the scaffolds passed or present in a directory  """

import sys
import os


class LastzConsts:

    #reference start col.
    REF_START_COL = 4

    #reference end col.
    REF_END_COL = 5

    #query name col
    QUERY_NAME_COL = 6

    #query strand
    QUERY_STRAND_DIR_COL = 7
    
    #query start col
    QUERY_START_COL = 9
    
    #query end col
    QUERY_END_COL = 10
    
    #scaff name col
    SCAFF_NAME_COL = 1

    #identity pc col
    SCAFF_ID_PC_COL = 12

    #strand dir col
    STRAND_DIR_COL = 2

    #other strand dir col
    STRAND_OTHER_DIR_COL = 7
    
    #Lastz score
    SCORE_COL = 0
    
    #output extension
    OUT_EXT = '.fasta.out'


    
class GFFConsts:
    
    #gff output file extension
    GFF_EXT = '.gff'

    

""" for the given scaffold writes or generate GFF text"""
def genGFFForScaff(lastzScaffPath, opFile):
    with open(lastzScaffPath, 'r') as lastzScaffFile:
        header = lastzScaffFile.readline()

        #write GFF header for the file
        #NAME  SOURCE  TYPE  START  END  SCORE  STRAND  FRAME  GROUP
        header = 'NAME' + '\t' + 'SOURCE' + '\t' + 'TYPE' + '\t' \
            + 'START' + '\t' + 'END' + '\t' + 'SCORE' + '\t' \
            + 'STRAND' + '\t' + 'FRAME' + '\t' + 'GROUP' + '\n'
        opFile.write('# '+header)

        
        for line in lastzScaffFile:
            cols = line.strip().split()

            idy = cols[LastzConsts.SCAFF_ID_PC_COL]
            #ignore if identity is less than 97%
            if float(idy.strip('%')) < 97:
                continue

            start = cols[LastzConsts.REF_START_COL]
            end = cols[LastzConsts.REF_END_COL]
            scaffName = cols[LastzConsts.SCAFF_NAME_COL]
            strandDir = cols[LastzConsts.STRAND_DIR_COL]
            matchedLen = int(end) - int(start) + 1

            queryName = cols[LastzConsts.QUERY_NAME_COL]
            queryStart = cols[LastzConsts.QUERY_START_COL]
            queryEnd = cols[LastzConsts.QUERY_END_COL]
            queryStrandDir = cols[LastzConsts.QUERY_STRAND_DIR_COL]
            
            #write details in output file
            #write this info in gff format
            #NAME  SOURCE  TYPE  START  END  SCORE  STRAND  FRAME  GROUP
            opFile.write(scaffName + '\t' + 'LASTZ' + '\t' \
                             + queryName+':'+queryStart+':'+queryEnd + '\t' \
                             + start + '\t' + end + '\t' + '.' + '\t' \
                             + strandDir + '\t' + '.' + '\t'\
                             + 'Target=' + queryName + ' ' + queryStart + ' ' + queryEnd + ' ' + queryStrandDir
                             + ';ID=' + idy.strip('%') + ';Note=matchedLen -> ' \
                             + str(matchedLen) + '|matchedTier -> ' \
                             + str(getLevel(matchedLen)) + ';Name=' \
                             + queryName  + '\n')



""" parse all the scaffolds in scaffDirPath and generate corresponding gff """
def generateGFFForScaffolds(scaffDirPath, opFilePath):
    files = os.listdir(scaffDirPath)
    for fileName in files:
        if fileName.endswith(LastzConsts.OUT_EXT):
            name = fileName.rstrip(LastzConsts.OUT_EXT)
            lastzScaffPath = os.path.join(scaffDirPath, fileName)
            opFileWPath = os.path.join(opFilePath, name+GFFConsts.GFF_EXT)
            with open(opFileWPath, 'w') as opFile:
                genGFFForScaff(lastzScaffPath, opFile)


""" decide the tier/level/group to put it in  
    Tier Num : matched length
        1    :  >= 50000
        2    :  >= 25000
        3    :  >= 15000
        4    :  >= 10000
        5    :  <  10000
"""
def getLevel(matchedLen):
    if matchedLen >= 50000:
        return 1
    elif matchedLen >= 25000:
        return 2
    elif matchedLen >= 15000:
        return 3
    elif matchedLen >= 10000:
        return 4
    else:
        return 5


            
def main():
    argLen =  len(sys.argv)
    if argLen >= 3:
        scaffPath = sys.argv[1]
        opFilePath = sys.argv[2]
               
        #check if passed scaffPath is dir or not
        if os.path.isdir(scaffPath) and os.path.isdir(opFilePath):
            #for all lastz outs  make gff
            generateGFFForScaffolds(scaffPath, opFilePath)
        elif os.path.isfile(scaffPath) and \
                scaffPath.endswith(LastzConsts.OUT_EXT):
            with open(opFilePath, 'w') as opFile:
                #for single scaffold lastz out 
                genGFFForScaff(scaffPath, opFile)
    else:
        print 'err: files missing'



if __name__ == '__main__':
    main()

