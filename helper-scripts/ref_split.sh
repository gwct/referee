#!/bin/bash

############################################################
# For Referee, 09.19
# Takes a sorted BAM file and runs through the steps to 
# split and run mpileup on the file.
############################################################

display_usage() {
# Usage message for -h
	echo "Usage:"
    echo
    echo "ref_split.sh -b <BAM file> -f <reference FASTA file> -r <1> -a -p -h"
    echo
    echo "Options:"
    echo "-b: (required) The full, sorted and indexed BAM file with reads mapped back to the assembly."
    echo "-f: (required) The FASTA file containing the reference sequence that the reads the BAM file have been mapped to."
    echo "-r: The number of processors to use. If > 1, GNU Parallel (https://www.gnu.org/software/parallel/) is required. Default: 1."
    echo "-a: Run ANGSD on the split BAM files."
    echo "-p: Run samtools mpileup on the split BAM files."
    echo "-h: Display this help message."
    echo
    echo "Dependencies:"
    echo "01: samtools (required; https://www.htslib.org/download/)"
    echo "02: GNU parallel (required for multiprocessing; https://www.gnu.org/software/parallel/)"
    echo "03: ANGSD (required with -a; http://popgen.dk/angsd/index.php/Installation)"
    echo
    echo "This script will create the following directories and files:"
    echo "01: refsplit-scaffold-list.txt -> A list of scaffolds in the input BAM file."
    echo "02: refsplit-bam/ -> A directory to which the split BAM files will be written."
    echo "03: refsplit-pileup/ -> If -p is specified, the split pileup files will be written here."
    echo "04: referee-pileup-input.txt -> If -p is specified, this file will have the paths to the split pileup files for Referee's -i flag."
    echo "05: refsplit-angsd/ -> If -a is specified, the ANGSD output files on the split BAMs will be written here."
    echo "06: referee-angsd-input.txt -> If -a is specified, this file will have the paths to the split ANGSD output files for Referee's -i flag."
    echo "================================================="
    exit 0
}

##########
# Invalid input option message
invalid_opt() {
    echo "Error 1: Invalid option: $1"
    echo "================================================="
    exit 1
}

##########
# Invalid input file message
invalid_file(){
    echo "Error 2: Both a sorted BAM file (-b) and a reference FASTA file (-f) must be provided."
    echo "================================================="
    exit 1   
}

##########
# Invalid run mode message
invalid_mode(){
    echo "Error 3: Only one of -a (ANGSD) or -p (pileup) may be specified."
    echo "================================================="
    exit 1   
}

############################################################

echo
echo "================================================="
echo " Workflow script to split a BAM file for Referee"
echo

bamfile=false
fasta=false
pileup=false
angsd=false
scafffile="refsplit-scaffold-list.txt"
procs=1
# Defaults

while getopts ":b:f:r:pah" arg; do
    case $arg in
        h) display_usage;;
        b) bamfile=$OPTARG;;
        f) fasta=$OPTARG;;
        a) angsd=true;;
        p) pileup=true;;
        r) procs=$OPTARG;;
        \?) invalid_opt $OPTARG ;;
    esac
done
# Parse input options

if [ "$bamfile" = false ] || [ "$fasta" = false ]; then
    invalid_file
fi
# Check to make sure a bam and fasta file has been provided.

# if [ "$angsd" = true ] && [ "$pileup" = true ]; then
#     invalid_mode
# fi
# Check to make sure only ANGSD or pileup has been specified as a run mode.

echo "STEP 01: GETTING LIST OF ALL SCAFFOLDS IN BAM FILE: refsplit-scaffold-list.txt"
samtools idxstats $bamfile | cut -f 1 | tail -n10 | grep -v "*" > $scafffile
# Get a list of all scaffolds in the BAM file

echo
echo "STEP 02: SPLITTING BAM FILE BY SCAFFOLD"
mkdir "refsplit-bam"
if [ $procs == 1 ]; then
    while read scaff; do
        echo "SPLIT BAM: " $scaff
        samtools view $bamfile -b -o refsplit-bam/$scaff.bam $scaff
    done < "$scafffile"
# Serial
else
    echo
    echo "SPLITTING BAM WITH GNU PARALLEL"
    echo
    cat $scafffile | parallel --progress --eta -j $procs "samtools view $bamfile -b -o refsplit-bam/{.}.bam {.}"
# Parallel
fi
# Split the BAM file by scaffold


if [ "$pileup" = true ]; then
    echo
    echo "STEP 3A: RUNNING PILEUP ON SPLIT BAMS"
    mkdir "refsplit-pileup"
    if [ $procs == 1 ]; then
        while read scaff; do
            echo "PILEUP: " $scaff
            samtools mpileup -d 999999999 -f $fasta -Q 0 -s -B -o refsplit-pileup/$scaff.pileup refsplit-bam/$scaff.bam
        done < "$scafffile"   
    # Serial
    else
        echo
        echo "RUNNING PILEUP WITH GNU PARALLEL"
        echo
        cat $scafffile | parallel --progress --eta -j $procs "samtools mpileup -d 999999999 -f $fasta -Q 0 -s -B -o refsplit-pileup/{.}.pileup refsplit-bam/{.}.bam"
    fi
    # Parallel
    # Run pileup on the split BAMs

    echo "-> GENERATIONG referee-pileup-input.txt"
    ls -d -1 "$PWD/refsplit-pileup/"*.pileup > referee-pileup-input.txt
    # Create the referee input file.
fi
# If pileup is specified to run


if [ "$angsd" = true ]; then
    echo
    echo "STEP 3B: RUNNING ANGSD ON SPLIT PILEUPS"
    mkdir "refsplit-angsd"
    if [ $procs == 1 ]; then
        while read scaff; do
            echo "ANGSD " $scaff
            angsd -GL 2 -i refsplit-bam/$scaff.bam -ref $fasta -minQ 0 -doGlf 4 -out refsplit-angsd/$scaff-angsd
        done < "$scafffile"   
    # Serial
    else
        echo
        echo "RUNNING ANGSD WITH GNU PARALLEL"
        echo
        cat $scafffile | parallel --progress --eta -j $procs "angsd -GL 2 -i refsplit-bam/{.}.bam -ref $fasta -minQ 0 -doGlf 4 -out refsplit-angsd/{.}-angsd"
    fi
    # Parallel
    # Run ANGSD on the split BAM files

    echo "-> GENERATING referee-angsd-input.txt"
    ls -d -1 "$PWD/refsplit-angsd/"*-angsd.glf.gz > referee-angsd-input.txt
    # Get the list of ANGSD output files with full paths
fi
# If ANGSD is specified to run

echo
echo "DONE! Please confirm that all your output files were created successfully."
echo "If you ran with -p, you can now use referee-pileup-input.txt as your -i input to Referee."
echo "If you ran with -a, you can now use referee-angsd-input.txt as your -i input to Referee."
echo "================================================="
echo