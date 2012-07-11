import sys
import os

""" takes the scaffold file, prefix suffix length, output file name and\
generate a file with sequences containg header of form <[prefix][suffix]>"""

def genHeader(scaffsFileName, prefix, suffixLen, outFileName):
    with open(scaffsFileName, 'r') as scaffsFile:
        with open(outFileName, 'w') as outFile:
            counter = 1
            suffixBase = 10**suffixLen
            for line in scaffsFile:
                if line.startswith('>'):
                    #found header
                    newHeader = '>' + prefix\
                        + (str(suffixBase+counter)[1:])
                    outFile.write(newHeader + '\n')
                    counter += 1
                else:
                    #found sequence
                    outFile.write(line)

                    
def main():
    argLen = len(sys.argv)
    if argLen >= 5:
        scaffsFileName = sys.argv[1]
        prefix = sys.argv[2]
        suffixLen = int(sys.argv[3])
        outFileName = sys.argv[4]
        genHeader(scaffsFileName, prefix, suffixLen, outFileName)
    else:
        print 'err: less num of args passed'

if __name__ == '__main__':
    main()
