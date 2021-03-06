import pybedtools
import sys
import os



def getGenomeCov(bamFileName, genomeFileName, geneCovFileName):
    print 'Creating bed... ', bamFileName
    bamBed = pybedtools.BedTool(bamFileName)
    
    print 'Getting genome coverage...'
    genomeCov = bamBed.genome_coverage(genome=genomeFileName, d=True)

    print 'Saving genome coverage...'
    genomeCov.saveas(geneCovFileName, trackline='track name= "bam and gene"')
    

def main():
    if len(sys.argv) > 3:
        bamFileName = os.path.abspath(sys.argv[1])
        genomeFileName = os.path.abspath(sys.argv[2])
        geneCovFileName = os.path.abspath(sys.argv[3])
        getGenomeCov(bamFileName, genomeFileName, geneCovFileName)
    else:
        print 'err: invalid arguments'


if __name__ == '__main__':
    main()
