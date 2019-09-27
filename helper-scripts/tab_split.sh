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
    echo "tab_split.sh -f <A bgzipped pileup or ANGSD output file> -r <1> -h"
    echo
    echo "Options:"
    echo "-i: (required) A bgzipped, tab delimited file with scaffold in column 1 and position in column 2. Both pileup and ANGSD output files fit these criteria."
    echo "-r: The number of processors to use. If > 1, GNU Parallel (https://www.gnu.org/software/parallel/) is required. Default: 1."
    echo "-h: Display this help message."
    echo
    echo "Dependencies:"
    echo "01: tabix (required; https://sourceforge.net/projects/samtools/files/tabix/)"
    echo "02: GNU parallel (required for multiprocessing; https://www.gnu.org/software/parallel/)"
    echo
    echo "This script will create the following directories and files:"
    echo "01: tabsplit-scaffold-list.txt -> A list of scaffolds in the input file."
    echo "02: tabsplit/ -> A directory to which the split files will be written."
    echo "03: referee-input.txt -> This file file will have the paths to the split files for Referee's -i flag."
    echo "==========================================================================="
    exit 0
}

##########
# Invalid input option message
invalid_opt() {
    echo "Error 1: Invalid option: $1"
    echo "==========================================================================="
    exit 1
}

##########
# Invalid run mode message
invalid_file(){
    echo "Error 2: A pileup or ANGSD output file must be provided (-i)"
    echo "==========================================================================="
    exit 1   
}

############################################################

echo
echo "==========================================================================="
echo " Workflow script to split a tabbed pileup or ANGSD output file for Referee"
echo

input=false
scafffile="tabsplit-scaffold-list.txt"
procs=1
# Defaults

while getopts ":i:r:h" arg; do
    case $arg in
        h) display_usage;;
        i) input=$OPTARG;;
        r) procs=$OPTARG;;
        \?) invalid_opt $OPTARG ;;
    esac
done
# Parse input options

 if [ "$input" == false ]; then
     invalid_file
 fi
# Check to make sure a file has been provided.

echo
echo "STEP 01: INDEXING INPUT FILE"
tabix -s 1 -b 2 -e 2 $input
# Index the input file

echo "STEP 02: GETTING LIST OF ALL SCAFFOLDS IN INPUT TAB FILE: tabsplit-scaffold-list.txt"
tabix -l $input | grep -v "*" > $scafffile
# Get a list of all scaffolds in the BAM file

echo "STEP 03: SPLITTING INPUT FILE"
mkdir "tabsplit"
if [ $procs == 1 ]; then
    while read scaff; do
        echo "SPLIT: " $scaff
        tabix -s 1 -b 2 -e 2 $input $scaff > tabsplit/$scaff.tab
    done < "$scafffile"   
# Serial
else
    echo
    echo "SPLITTING INPUT FILE WITH GNU PARALLEL"
    echo
    cat $scafffile | parallel --progress --eta -j $procs "tabix -s 1 -b 2 -e 2 $input {.} > tabsplit/{.}.tab"
fi
# Parallel
# Split the input file

echo "-> GENERATING referee-input.txt"
ls -d -1 "$PWD/tabsplit/"*.tab > referee-input.txt
# Create the referee input file.

echo
echo "DONE! Please confirm that all your output files were created successfully."
echo "You can now use referee-input.txt as your -i input to Referee."
echo "==========================================================================="
echo