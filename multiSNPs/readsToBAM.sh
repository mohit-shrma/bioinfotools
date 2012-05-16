#!/bin/bash

#reads directory
READS_DIR=""

#read libraries
READS_ARR=(some)
READS_EXT=".lite.sra"

#scaffolds directory, contains directory by name of scaffold inside
SCAFF_DIR=""

#scaffolds array, each present in above dir
#http://tldp.org/LDP/Bash-Beginners-Guide/html/sect_10_02.html
SCAFF_ARR=(some)
SCAFF_EXT=".fasta"

#out directory
OUT_DIR=""

#fastq extension
FASTQ_EXT=".fastq"

#sai extension
SAI_EXT=".sai"

#sam extension
SAM_EXT=".sam"


#unique sam extension
UNIQ_SAM_EXT="_Unique.sam"
SAM_INFO_EXT="_info.txt"

#unique bam extension
UNIQ_BAM_EXT="_Unique.bam"
SORT_BAM_EXT="_Unique.sorted"

#tools
BWA="/project/huws/huwsgroup/Nitya/Mapping/Mapping_quality/bwa-0.5.9rc1/bwa"
FASTQDUMP_CMD="/project/huws/huwsgroup/Andrew/CHIPseq/sratoolkit.2.1.0-ubuntu32/fastq-dump"
SAMTOOLS="/project/huws/huwsgroup/Nitya/SAMtools18/samtools-0.1.18/samtools"
UNIQUESAMPL="/project/huws/huwsgroup/mohit/bgicomp/readsBwa/pull_Unique_reads.pl"
PICARD_TOOLS="/project/huws/huwsgroup/mohit/picard-tools-1.68"
GENOME_ANALYSIS_TK_JAR="/project/huws/huwsgroup/mohit/GenomeAnalysisTK/GenomeAnalysisTK.jar"
SAMTOOLS="/project/huws/huwsgroup/mohit/samtools-0.1.18/samtools"
VARSCAN_JAR="/project/huws/huwsgroup/mohit/varscan/VarScan.v2.2.10.jar"

#for each read create fastq's and process
for sra in ${READS_ARR[@]} do
  #generate fastq for this sra in out dir
  $FASTQDUMP_CMD -A $sra -O $OUT_DIR $READS_DIR"/"$sra$READS_EXT
  FASTQ_ARR=($sra"_1" $sra"_2")
  #for each fastq above, asuuming it has no extension just prefix
  for fastq in ${FASTQ_ARR[@]} do
    #for each scaffold generate BAM
    for scaffold in ${SCAFF_ARR[@]} do

      #generate index using BWA
      cd $SCAFF_DIR"/"$scaffold
      
      #generate index
      $BWA  index -a bwtsw -p $scaffold$SCAFF_EXT $SCAFF_DIR"/"$scaffold"/"$scaffold$SCAFF_EXT

      #generate sai
      $BWA aln -n 3 -l 1000000 -o 1 -e 5 $scaffold$SCAFF_EXT $OUT_DIR"/"$fastq$FASTQ_EXT > $fastq$SAI_EXT

      #generate sam file for sai
      $BWA samse -n 15 $scaffold$SCAFF_EXT $fastq$SAI_EXT $OUT_DIR"/"$fastq$FASTQ_EXT > $fastq$SAM_EXT

      #convert to unique sam, with info
      perl $UNIQUESAMPL $SCAFF_DIR"/"$scaffold"/"$fastq$SAM_EXT $SCAFF_DIR"/"$scaffold"/"$fastq$UNIQ_SAM_EXT $SCAFF_DIR"/"$scaffold"/"$fastq$SAM_INFO_EXT

      #convert to bam
      $SAMTOOLS view -bS -q 30 xo$SCAFF_DIR"/"$scaffold"/"$fastq$UNIQ_SAM_EXT  > $SCAFF_DIR"/"$scaffold"/"$fastq$UNIQ_BAM_EXT

      #convert to sorted bam
      $SAMTOOLS sort  $SCAFF_DIR"/"$scaffold"/"$fastq$UNIQ_BAM_EXT $SCAFF_DIR"/"$scaffold"/"$fastq$SORT_BAM_EXT 
    done #end scaffold
  done #end fastq
  #delete completed fastq
  rm $OUT_DIR"/"$fastq$FASTQ_EXT
done #end sra

#for each scaffold
for scaffold in ${SCAFF_ARR[@]} do

  #built fasta sequence dictionary
  java -Xms2048m -jar $PICARD_TOOLS"/CreateSequenceDictionary.jar" R=$SCAFF_DIR"/"$scaffold"/"$scaffold$SCAFF_EXT O=$SCAFF_DIR"/"$scaffold"/"$scaffold".dict"
  
  #merge all bams for this scaffold into single bam
  $SAMTOOLS merge $SCAFF_DIR"/"$scaffold"/"$scaffold$SORT_BAM_EXT $SCAFF_DIR"/"$scaffold"/"$scaffold"*.bam"

  #add or replace read groups
  java -Xms2048m -jar $PICARD_TOOLS"/AddOrReplaceReadGroups.jar" I=$SCAFF_DIR"/"$scaffold"/"$scaffold$SORT_BAM_EXT O=$SCAFF_DIR"/"$scaffold"/"$scaffold"_picard2.sorted.bam" SORT_ORDER=coordinate RGLB=1 RGPL=illumina RGPU=bar RGSM=BMGC VALIDATION_STRINGENCY=LENIENT CREATE_INDEX=TRUE

  #reorder SAM
  java -Xms2048m -jar $PICARD_TOOLS"/ReorderSam.jar" I=$SCAFF_DIR"/"$scaffold"/"$scaffold"_picard2.sorted.bam" O=$SCAFF_DIR"/"$scaffold"/"$scaffold"_picard3.sorted.bam" REFERENCE=$SCAFF_DIR"/"$scaffold"/"$scaffold$SCAFF_EXT VALIDATION_STRINGENCY=LENIENT CREATE_INDEX=TRUE

  #genome analysis tK realigner target creator
  java -Xms2048m -jar $GENOME_ANALYSIS_TK_JAR -T RealignerTargetCreator -R $SCAFF_DIR"/"$scaffold"/"$scaffold$SCAFF_EXT -I $SCAFF_DIR"/"$scaffold"/"$scaffold"_picard3.sorted.bam" -o $SCAFF_DIR"/"$scaffold"/"$scaffold".intervals"

  #genome analysis tK indel realigner
  java -Xms2048m -jar $GENOME_ANALYSIS_TK_JAR -T IndelRealigner -R $SCAFF_DIR"/"$scaffold"/"$scaffold$SCAFF_EXT -I $SCAFF_DIR"/"$scaffold"/"$scaffold"_picard3.sorted.bam" -targetIntervals $SCAFF_DIR"/"$scaffold"/"$scaffold".intervals" -o $SCAFF_DIR"/"$scaffold"/"$scaffold"_gatkrealigned.sorted.bam"

  #sangerq sorted bam
  $SAMTOOLS view -h $SCAFF_DIR"/"$scaffold"/"$scaffold"_gatkrealigned.sorted.bam" | perl -lane '$"="\t"; if (/^@/) {print;} else {$F[10]=~ tr/\x40-\xff\x00-\x3f/\x21-\xe0\x21/;print "@F"}' | $SAMTOOLS view -Sbh - > $SCAFF_DIR"/"$scaffold"/"$scaffold"_gatkrealigned_sangerQ.sorted.bam"

  #mpileup generation
  $SAMTOOLS mpileup -BQ0 -d10000000 -f $SCAFF_DIR"/"$scaffold"/"$scaffold$SCAFF_EXT  $SCAFF_DIR"/"$scaffold"/"$scaffold"_gatkrealigned.sorted.bam" > $SCAFF_DIR"/"$scaffold"/"$scaffold"_gatkrealigned.mpileup"

  #use varscan to make realigned cns
  java -jar $VARSCAN_JAR mpileup2cns $SCAFF_DIR"/"$scaffold"/"$scaffold"_gatkrealigned.mpileup" --min-coverage 8 --min-reads2 3 --min-avg-qual 20 --min-var-freq 0.01 --p-value 0.99 --strand-filter 0 --variants 1 > $SCAFF_DIR"/"$scaffold"/"$scaffold"_realigned.cns"

  #generate indels
  java -jar $VARSCAN_JAR mpileup2indel $SCAFF_DIR"/"$scaffold"/"$scaffold"_gatkrealigned.mpileup" --min-coverage 8 --min-reads2 3 --min-avg-qual 20 --min-var-freq 0.01 --p-value 0.99 --strand-filter 0 --variants 1 > $SCAFF_DIR"/"$scaffold"/"$scaffold"_realigned2.indel"

  #rename mpileup to pileup
  mv $SCAFF_DIR"/"$scaffold"/"$scaffold"_gatkrealigned.mpileup" $SCAFF_DIR"/"$scaffold"/"$scaffold"_gatkrealigned.pileup"

  #pileup to SNP
  java -jar $VARSCAN_JAR pileup2snp $SCAFF_DIR"/"$scaffold"/"$scaffold"_gatkrealigned.pileup" --min-coverage 8 --min-reads2 3 --min-avg-qual 20 --min-var-freq 0.01 --p-value 0.99 > $SCAFF_DIR"/"$scaffold"/"$scaffold"_realigned3.snp"

done


