#to split multiple fasta file into multiple files containing a
#fasta each

ipFileName = ""
inFile = open(ipFileName, "r")

opDirName = ""

headerStart = '>'

tempOutfile = None

if infile:
    for line in inFile:
        if line[0] == headerStart:
            #got the header open a file named header.fasta
            header = line.rstrip('\n')
            header = header[1:]
            tempOutFile = open(opDirName + '/' + header
                               + '.fasta', w)
        else:
            tempOutFile.write(line)
            tempOutFile.close()
    infile.close()
                
                
            
    
