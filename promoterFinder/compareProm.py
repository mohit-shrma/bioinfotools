import sys
import os
import csv

class PROM_TAB:
    START_COL = 3
    END_COL = 4
    GENE_ID = 7
    PROM_TYPE = 2


class PROM_DB_TAB:
    START_COL = 1
    END_COL = 2
    GENE_ID = 5
    PROM_TYPE = 4


class BLAST_TAB:
    REF_START_COL = 1
    REF_END_COL = 2
    QUERY_START_COL = 4
    QUERY_END_COL = 5


def getRangeGeneDic(promTabFileName, PROM_COL_INFO):
    with open(prom1TabFileName, 'r') as promTabFile:
        rangeGeneDic = {}
        promTabReader = csv.reader(prom1TabFile)
        for row in promTabReader:
            start = row[PROM_COL_INFO.START_COL]
            end = row[PROM_COL_INFO.END_COL]
            gene = row[PROM_COL_INFO.GENE_ID]
            rangeGeneDic[start + ':' + end] = gene
    return rangeGeneDic


def filterMummerOpFile(alignOpFileName, filteredOpFileName, qryRangeGeneDic,\
                           refRangeGenDic):
    with open(alignOpFileName, 'r') as mummerOpFile:
        mummerOpReader = csv.reader(mummerOpFile)
        #skip header
        mummerOpReader.next()
        for row in mummerOpReader:
            qryStart = row[BLAST_TAB.QUERY_START_COL]
            qryEnd = row[BLAST_TAB.QUERY_END_COL]
            refStart = row[BLAST_TAB.REF_START_COL]
            refEnd = row[BLAST_TAB.REF_END_COL]
            if qryRangeGeneDic[qryStart + ':' + qryEnd] ==\
                    refRangeGenDic[refStart + ':' + refEnd]:
                filteredOpFileName('\t'.join(row) + '\n')


def main():
    if len(sys.argv) > 3:
        alignOpFileName = sys.argv[1]
        qryTabFileName = sys.argv[2]
        refTabFileName = sys.argv[3]
        filteredOpFileName = sys.argv[4]
        #extracted promoters first
        qryRangeGeneDic = getRangeGeneDic(qryTabFileName, PROM_TAB)
        #downloaded promoters
        refRangeGenDic = getRangeGeneDic(refTabFileName, PROM_DB_TAB)
        filterMummerOpFile(alignOpFileName, filteredOpFileName, qryRangeGeneDic,\
                           refRangeGenDic)


    else:
        print 'err:invalid args'


if __name__ == '__main__':
    main()
