<p align="center"><img align="center" width="217" height="175" src="https://gwct.github.io/referee/img/ref-logo.png"></p>

# Referee

## Quality scoring for reference genomes

[![OS](https://gwct.github.io/referee/img/badges/osbadge.svg)](#Installation)
[![Language](https://gwct.github.io/referee/img/badges/pybadge.svg)](https://www.python.org/)
[![Build Status](https://travis-ci.org/gwct/referee.svg?branch=master)](https://travis-ci.org/gwct/referee)
[![codecov](https://codecov.io/gh/gwct/referee/branch/master/graph/badge.svg?token=3U2K65R611)](https://codecov.io/gh/gwct/referee)
![GitHub last commit](https://img.shields.io/github/last-commit/gwct/referee)
[![License](https://img.shields.io/github/license/gwct/referee)](https://github.com/gwct/referee/LICENSE)

## Authors
#### Gregg Thomas and Matthew Hahn

## About

### Referee is a program to calculate a quality score for every position in a genome assembly. This allows for easy filtering of low quality sites for any downstream analysis.

#### What follows is a brief explanation of the options. Please see the project website for much more in depth info about the algorithm and examples of the program's usage.

#### https://gwct.github.io/referee/

## Citation

#### Thomas GWC and Hahn MW. 2019. Referee: reference assembly quality scores. Genome Biology and Evolution. https://doi.org/10.1093/gbe/evz088. 

## Version History
#### This is version 1.2, released August 25, 2020

Change log:
* Restructured multiprocessing scheme; removed `-i` option.

###### Version 1.1 (August 19,2019): Added the `--haploid` option to score genome assemblies from haploid species.
###### Version 1.0 (April 19, 2019): Release coincides with publication. No major changes.
###### Version Beta 1.2 (November 04, 2018): Added bed output option with `--bed` and redesigned the website.
###### Version Beta 1.1 (October 14, 2018): Implemented in-house genotype likelihood calculations with `--pileup` input.
###### Version Beta 1.0 (October 6, 2018): First release and implementation of reference quality algorithm

## Installation

Simply download the program and run it. You may want to add the Referee folder to your $PATH variable for ease of use.
### The only dependency is Python 3+

## Usage

These are the general steps for scoring your genome:

1. Using any applicable software, map the reads from which you constructed your genome back to the finished assembly. (A BAM file is usable by samtools mpileup or ANGSD pileup for calculating genotype likelihoods in the next step)

2. Compile a pileup file for Referee to calculate genotype likelihoods OR pre-calculate genotype log likelihoods for all 10 genotypes at every position in the genome (we recommend [ANGSD](https://github.com/ANGSD/angsd) for this).

3. Score your genome with one of the following Referee commands:

`python referee.py -gl [genotype likelihood file] -ref [reference genome FASTA file] --pileup`

Alternatively, if you have multiple pileup or genotype likelihood files you wish to score with the same reference genome, you could put the paths to each file in a text file with one file path per line for Referee to score them all:

`python referee.py -i [text file with paths to genotype likelihood files] -ref [reference genome FASTA file] --pileup`

If you have pre-calculated genotype log likelihoods as input, exclude the `--pileup` flag.

### Options

| Option | Description | 
| ------ | ----------- |
| -gl | A single pileup file or a single file containing log genotype likelihoods for every site in your genome with reads mapped to it. Can be gzip compressed or not. If using pre-calculated log likelihoods, see the important information below regarding the order of the columns in the file. Note: Only one of `-gl` or `-i` can be specified.|
| --pileup | If this option is set, Referee will read the input file(s) in pileup format and use this info to calculate genotype likelihoods prior to the reference quality score. |
| -ref | A FASTA formatted file containing the genome you wish to score. Can be gzip compressed or not. FASTA headers must match the sequence IDs in column one of the pileup or genotype log likelihood file. |
| -o | The desired output directory. Default: `referee-[date]-[time]` |
| -prefix | Referee will create at least 2 output files: a tab delimited score file and a log file. Use this option to specify a prefix for these file names. Otherwise, they will default to `referee-[date]-[time]`. |
| --overwrite | By default, if the specified output directory already exists, Referee will exit with a warning. Set this option to bypass this warning and allow Referee to overwrite the files in this directory. |
| --mapq | If pileup file(s) are given as input, set this to incorporate mapping quality into Referee's quality score calculation. Mapping quality can be output by samtools mpileup with the `-s` option, and will appear in the 7th column of the file. If `--mapq` is not set, mapping qualities will be ignored even if they are present. |
| --fastq | Referee outputs quality scores for every position in tab delimited format (see below), but with this option scores can also be output in FASTQ format. Scores will be converted to [ASCII](https://en.wikipedia.org/wiki/ASCII) characters: score + 35 = ASCII char. Note 1: If `--correct` is set, corrected bases will appear as lower case. Note 2: This option cannot be set with `--mapped`. |
| --bed | Referee can output scores in binned BED format for visualizing tracks of scores in most genome browsers. One .bed file will be created for each scaffold scored and these will be placed in a directory ending with -bed-files. Note: This option cannot be set with `--mapped`. |
| --haploid | Set this option if your input sequencing data comes from a haploid species. Referee will limit it's likelihood calculations to single base states. Note: This option can only be used with an input `--pileup` file. |
| --correct | With this option, sites where reads do not support the called reference base will have a higher scoring base suggested. In the tab delimited output, the corrected base and score is reported in additional columns. In FASTQ output, the corrected positions are indicated by lower case bases. |
| --mapped | Only report scores for sites with reads mapped to them. Note: This option cannot be set with `--fastq` or `--bed`. |
| --quiet | Set this option to prevent Referee from printing out runtime statistics for each step. |
| -p | The number of processes Referee can use. |
| -l | The number of input lines read per process. Default: 100000. Decreasing this number may improve memory usage at the cost of slightly higher run times. |
