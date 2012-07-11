import sys
import os




""" takes input file and remove newline from sequences following a heeader  """

def trimScaffsFile(scaffsFileName, outFileName):
    with open(scaffsFileName, 'r') as scaffsFile:
            with open(outFileName, 'w') as outFile:
                firstHeader = scaffsFile.readline()
                outFile.write(firstHeader)
                for line in scaffsFile:
                    if line.startswith('>'):
                        outFile.write('\n')
                        outFile.write(line)
                    else:
                        line = line.rstrip('\n')
                        outFile.write(line)
                outFile.write('\n')


def main():
    argLen = len(sys.argv)
    if argLen >= 3:
        scaffsFileName = sys.argv[1]
        outFileName = sys.argv[2]
        trimScaffsFile(scaffsFileName, outFileName)
    else:
         print 'err: less num of args passed'



if __name__ == '__main__':
    main()
