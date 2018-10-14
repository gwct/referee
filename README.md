# Referee
### Quality scoring for reference genomes

## Author
#### Gregg Thomas

## About

### Referee is a program to calculate a quality score for every position in a genome assembly. This allows for easy filtering of low quality sites for any downstream analysis.

### See the project [website](https://gwct.github.io/referee/) for more info!

## Citation

#### Forthcoming

## Version History
#### This is version Beta 1.1, released October 14, 2018

Change log:
* Implemented in-house genotype likelihood calculations with `--pileup` input.

###### Version Beta 1.0 (October 6, 2018): First release and implementation of reference quality algorithm

## Installation

Simply download the program and run it. You may want to add the Referee folder to your $PATH variable for ease of use.
### The only dependency is Python 2.7 or higher

## Usage

These are the general steps for scoring your genome:

1. Using any applicable software, map the reads from which you constructed your genome back to the finished assembly. (A BAM file is usable by ANGSD for calculating genotype likelihoods in the next step)

2. Compile a pileup file for Referee to calculate genotype likelihoods OR pre-calculate log genotype likelihoods for all 10 genotypes at every position in the genome (we recommend [ANGSD](https://github.com/ANGSD/angsd) for this).

3. Score your genome with one of the following Referee commands:

`python referee.py -gl [genotype likelihood file] -ref [reference genome FASTA file] --pileup`

Alternatively, if you have multiple genotype likelihood files you wish to score with the same reference genome, you could put the paths to each file in a text file with one file path per line for Referee to score them all:

`python referee.py -i [text file with paths to genotype likelihood files] -ref [reference genome FASTA file] --pileup`

If you have pre-calculated genotype likelihoods as input, exclude the `--pileup` flag.

### Options

| Option | Description | 
| ------ | ----------- |
| -gl | A single pileup file or a single file containing log genotype likelihoods for every site in your genome with reads mapped to it. Can be gzip compressed or not. Note: Only one of `-gl` or `-i` can be specified.|
| -i | A file containing paths to multiple pileup files or multiple log genotype likelihood files. One file path per line. Note: Only one of `-gl` or `-i` can be specified.|
| -ref | A FASTA formatted file containing the genome you wish to score. Can be gzip compressed or not. FASTA headers must match the sequence IDs in column one of the genotype likelihood file. |
| -o | Referee will create at least 2 output files: a tab delimited score file and a log file. Use this option to specify a prefix for these file names. Otherwise, they will default to `referee-out-[date]-[time]-[random string]` |
| --pileup | If this option is set, Referee will read the input file(s) in pileup format and use this info to calculate genotype likelihoods prior to the reference quality score (see below) |
| --fastq | The scores can also be output in FASTQ format. This option cannot be set with `--mapped`. Scores will be converted to [ASCII](https://en.wikipedia.org/wiki/ASCII) characters: score + 35 = ASCII char |
| --correct | With this option, sites where reads do not support the called reference base will have a higher scoring base suggested. |
| --mapped | Only report scores for sites with reads mapped to them. This option cannot be set with `--fastq`. |
| -p |The number of processes Referee can use. |

### Calculating genotype likelihoods from a pileup file (`--pileup`)

Referee can take as input a pileup file and calculate genotype likelihoods for each site prior to reference quality scores. To generate a pileup file, use samtools:

`samtools mpileup -d 999999999 -f <reference.fasta> -Q 0 -s -o <output.pileup> <input.bam>`

The option `-d 999999999` sets the minimum depth to report a site to a high enough number that all sites will be reported. `-Q 0` sets the maximum base quality required to report a site to 0, again ensuring that all sites will e reported. `-s` tells mpileup to output mapping quality in an additional column. If this is set, Referee will incorporate mapping quality into the genotype likelihood calculation.

### The genotype likelihoods format

If `--pileup` is not set, a file with precalculated **log** genotype likelihoods may be provided. We recommend [ANGSD](https://github.com/ANGSD/angsd) for this as it provides output in a format ready for use by Referee. This file should be a tab delimited file with columns in exactly this order:

| Sequence ID | Position | AA | AC | AG | AT | CC | CG | CT | GG | GT | TT |
|-------------|----------|----|----|----|----|----|----|----|----|----|----|

This file should not have headers.

#### Important! The sequence IDs in the genotype likelihood file must match those in the reference FASTA file.

Example with log likelihoods:

```
scaffold_0	5	0.000000	-0.693147	-0.693147	-0.693147	-15.374639	-15.374639	-15.374639	-15.374639	-15.374639	-15.374639
scaffold_0	6	0.000000	-1.386294	-1.386294	-1.386294	-30.519020	-30.519020	-30.519020	-30.519020	-30.519020	-30.519020
scaffold_0	7	-30.288761	-30.288761	-1.386294	-30.288761	-30.288761	-1.386294	-30.288761	0.000000	-1.386294	-30.288761
scaffold_0	8	-27.986172	-1.386293	-27.986172	-27.986172	0.000000	-1.386293	-1.386293	-27.986172	-27.986172	-27.986172
scaffold_0	9	-27.755912	-1.386292	-27.755912	-27.755912	0.000000	-1.386292	-1.386292	-27.755912	-27.755912	-27.755912
scaffold_0	10	-8.689986	0.000000	-10.076280	-10.076280	-29.821151	-30.514277	-30.514277	-40.590558	-40.590558	-40.590558
```

If you have multiple genotype likelihood files from the same reference genome to score, use `-i` and provide a text file containing the paths to each file, one per line.

Example:

```
/path/to/gl/file1.txt
/path/to/gl/file2.txt
/path/to/gl/file3.txt
/path/to/gl/file4.txt
```

### Outputs

Referee creates a log file and a tab delimited output file by default. The tab delimited output file contains three columns with no headers:

| Sequence ID | Position | Quality score |
|-------------|----------|---------------|

Example:

```
scaffold_0	5	0
scaffold_0	6	13
scaffold_0	7	13
scaffold_0	8	12
scaffold_0	9	12
scaffold_0	10	13
```

If the `--correct` option is specified, this file will contain 2 additional columns for sites with reads that do not support the called reference base:

| Sequence ID | Position | Quality score | Highest scoring base | Score for highest scoring base |
|-------------|----------|---------------|----------------------|--------------------------------|

Example:

```
scaffold_0	5	0	A	6
scaffold_0	6	13		
scaffold_0	7	13		
scaffold_0	8	12		
scaffold_0	9	12		
scaffold_0	10	13	
```

Additionally, the `--fastq` option can be specified to output the sequence and scores in FASTQ format:

```
@scaffold_0 1:40 length=40
GGTGTAGCCAGAGAGTAAANAATATGGTGAAGCCAGAGAG
+
!!!!#00//0442.45=CK"CKKLLKLKLKSRRRSSRSSS
```

In this case, scores have been converted to [ASCII](https://en.wikipedia.org/wiki/ASCII) characters with the following method:

FASTQ score char = ascii(Score+35)

In other words, the [ASCII](https://en.wikipedia.org/wiki/ASCII) character `S` corresponds to the decimal 83. That means the score at this position was 83 - 35 = 48.

#### Special case scores

There are several scenarios where the scoring calculation is impossible. We have reserved some scores for these situations.

| Scenario | Score |
|----------|-------|
| The sum of the genotype likelihoods that do not contain the reference base is 0 | 92 |
| The reference base is called as N | -1 |
| No reads mapped to this site | -2 |

For the case of the reference base being called as N, Referee can calculate the highest scoring base and report it with the `--correct` option.