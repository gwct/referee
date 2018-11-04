# Referee
### Quality scoring for reference genomes

## Authors
#### Gregg Thomas and Matthew Hahn

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
| -i | A file containing paths to multiple pileup files or multiple genotype log likelihood files. One file path per line. Note: Only one of `-gl` or `-i` can be specified.|
| -ref | A FASTA formatted file containing the genome you wish to score. Can be gzip compressed or not. FASTA headers must match the sequence IDs in column one of the pileup or genotype log likelihood file. |
| -o | Referee will create at least 2 output files: a tab delimited score file and a log file. Use this option to specify a prefix for these file names. Otherwise, they will default to `referee-out-[date]-[time]-[random string]`. If `-i` is specified, this will be the name of the output directory. |
| --pileup | If this option is set, Referee will read the input file(s) in pileup format and use this info to calculate genotype likelihoods prior to the reference quality score (see below) |
| --mapq | If pileup file(s) are given as input, set this to incorporate mapping quality into Referee's quality score calculation. Mapping quality can be output by samtools mpileup with the `-s` option, and will appear in the 7th column of the file. If `--mapq` is not set, mapping qualities will be ignored even if they are present. |
| --fastq | Referee outputs quality scores for every position in tab delimited format (see below), but with this option scores can also be output in FASTQ format. Scores will be converted to [ASCII](https://en.wikipedia.org/wiki/ASCII) characters: score + 35 = ASCII char. Note 1: If `--correct` is set, corrected bases will appear as lower case. Note 2: This option cannot be set with `--mapped`. |
| --bed | Referee can output scores in binned BED format for visualizing tracks of scores in most genome browsers. One .bed file will be created for each scaffold scored and these will be placed in a directory ending with -bed-files. Note: This option cannot be set with `--mapped`. |
| --correct | With this option, sites where reads do not support the called reference base will have a higher scoring base suggested. In the tab delimited output, the corrected base and score is reported in additional columns. In FASTQ output, the corrected positions are indicated by lower case bases. |
| --mapped | Only report scores for sites with reads mapped to them. Note: This option cannot be set with `--fastq` or `--bed`. |
| --quiet | Set this option to prevent Referee from printing out runtime statistics for each step. |
| -p |The number of processes Referee can use. |

### Calculating genotype likelihoods from a pileup file (`--pileup`)

Referee can take as input a pileup file and calculate genotype likelihoods for each site prior to reference quality scores. This will have a detrimental effect on runtime. To generate a pileup file, use samtools:

`samtools mpileup -d 999999999 -f <reference.fasta> -Q 0 -s -o <output.pileup> <input.bam>`

The option `-d 999999999` sets the minimum depth to report a site to a high enough number that all sites will be reported. `-Q 0` sets the maximum base quality required to report a site to 0, again ensuring that all sites will be reported. `-s` tells mpileup to output mapping quality in an additional column. If mpileup is run with this option and `--mapq` is set in Referee, Referee will incorporate mapping quality into the genotype likelihood calculation.

### The pre-calculated genotype log likelihoods file format

If `--pileup` is not set, a file with precalculated **log** genotype likelihoods may be provided. We recommend [ANGSD](https://github.com/ANGSD/angsd) for this as it provides output in a format ready for use by Referee. This file should be a tab delimited file with columns in exactly this order:

| Sequence ID | Position | AA | AC | AG | AT | CC | CG | CT | GG | GT | TT |
|-------------|----------|----|----|----|----|----|----|----|----|----|----|

**This file should not have headers.**

#### Important! The sequence IDs in the pileup or genotype likelihood file must match those in the reference FASTA file.

The headers in the FASTA file can have additional information, but the sequence IDs must be first, followed immediately by a space (if this is too non-standard, contact me and I can change it).

Example log likelihood format:

```
scaffold_0	5	0.000000	-0.693147	-0.693147	-0.693147	-15.374639	-15.374639	-15.374639	-15.374639	-15.374639	-15.374639
scaffold_0	6	0.000000	-1.386294	-1.386294	-1.386294	-30.519020	-30.519020	-30.519020	-30.519020	-30.519020	-30.519020
scaffold_0	7	-30.288761	-30.288761	-1.386294	-30.288761	-30.288761	-1.386294	-30.288761	0.000000	-1.386294	-30.288761
scaffold_0	8	-27.986172	-1.386293	-27.986172	-27.986172	0.000000	-1.386293	-1.386293	-27.986172	-27.986172	-27.986172
scaffold_0	9	-27.755912	-1.386292	-27.755912	-27.755912	0.000000	-1.386292	-1.386292	-27.755912	-27.755912	-27.755912
scaffold_0	10	-8.689986	0.000000	-10.076280	-10.076280	-29.821151	-30.514277	-30.514277	-40.590558	-40.590558	-40.590558
```

Note that ANGSD also scales the log likelihoods by subtracting the highest likelihood from each likelihood. This has no effect on Referee's scoring.

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

If the `--correct` option is specified, corrected bases will be lower case. All others should be upper case.

#### Special case scores

There are several scenarios where the scoring calculation is impossible. We have reserved some scores for these situations.

| Scenario | Score |
|----------|-------|
| The sum of the genotype likelihoods that do not contain the reference base is 0 | 91 |
| The reference base is called as N | -1 |
| No reads mapped to this site | -2 |

For the case of the reference base being called as N, Referee can calculate the highest scoring base and report it with the `--correct` option.

#### Other notes

By default, Referee prints out the runtime for each step. If the [psutil](https://pypi.org/project/psutil/) module is installed, it will also print out memory usage. However, if you have many input files or use many processes then this can be distracting. Use `--quiet` to disable.

