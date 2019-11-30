############################################################
# For Referee docs, 11.19
# This generates the file "readme.html"
############################################################

import sys, os
sys.path.append('..')
import lib.read_chunks as RC

######################
# HTML template
######################

html_template = """
<!doctype html>
    {head}

<body>
    {nav}

<div class="pure-g" id="main_row">
		<div class="pure-u-3-24" id="margin"></div>
		<div class="pure-u-18-24" id="main_col">
			<div id="main_content">
				<h1>Referee README</h1>
                <h3>This page contains all info about the Referee program including its inputs, options, and outputs.</h3>

                <div class="readme_divider"></div>
				<h2>Installation</h2>
                    <p>Clone or download the github repo: <a href="https://github.com/gwct/referee" target="_blank">Referee github</a></p>
                    <p>The only dependency is Python 2.7 or higher. You may want to add the Referee folder to your $PATH variable for ease of use!</p>
                
                <div class="readme_divider"></div>
                <h2>Usage</h2>
                    <p>These are the general steps for scoring your genome:</p>
                    <ol>
                        <li><p>Using any applicable software, map the reads from which you constructed your genome back to the finished 
                            assembly. (A BAM file is usable by ANGSD for calculating genotype likelihoods in the next step)</p></li>
                        <li><p>Compile a pileup file for Referee to calculate genotype likelihoods OR pre-calculate genotype 
                            log-likelihoods for all 10 genotypes at every position in the genome (we recommend <a href="https://github.com/ANGSD/angsd">ANGSD</a> 
                            for this).</p></li>
                        <li><p>Score your genome with one of the following Referee commands:</p>
                            <pre><code>python referee.py -gl [genotype likelihood file] -ref [reference genome FASTA file] --pileup</code></pre>
                            <p>Alternatively, if you have multiple genotype likelihood files you wish to score with the same reference genome, you 
                                could put the paths to each file in a text file with one file path per line for Referee to score them all:</p>
                            <pre><code>python referee.py -i [text file with paths to genotype likelihood files] -ref [reference genome FASTA file] --pileup</code></pre>
                            <p>If you have pre-calculated genotype likelihoods as input, exclude the <code>--pileup</code> flag.</p>
                        </li>
                    </ol>

                
                    <h3>Input</h3>
                        <p>There are two main inputs for the program:</p>
                        <ol>
                            <li><p>A genotype log-likelihood file (<code class="cb">-gl</code>) or files (<code class="cb">-i</code>). File(s) can be either 
                                pre-calculated genotype log-likelihoods in a certain format (see below), or a pileups from which Referee will calculate 
                                genotype likelihoods. See the <a href="walkthrough.html">walkthrough</a> for more info.</p>
                                
                                <p>If you use a pileup file as input, be sure to use the <code class="cb">--pileup</code> flag.</p>

                                <p>If you have pre-calculated genotype log-likelihoods, they must be formatted in a tab delimited file with the following columns
                                    and no column headers:

                                <pre><code>Scaffold ID  Position    AA  AC  AG  AT  CC  CG  CT  GG  GT  TT</code></pre>

                                <strong>If your input has a different column ordering, you will not get accurate scores!</strong></p>

                                <p>For example, the following output snippet from ANGSD is acceptable:

                                <pre><code>scaffold_0	5	0.000000	-0.693147	-0.693147	-0.693147	-15.374639	-15.374639	-15.374639	-15.374639	-15.374639	-15.374639
scaffold_0	6	0.000000	-1.386294	-1.386294	-1.386294	-30.519020	-30.519020	-30.519020	-30.519020	-30.519020	-30.519020
scaffold_0	7	-30.288761	-30.288761	-1.386294	-30.288761	-30.288761	-1.386294	-30.288761	0.000000	-1.386294	-30.288761
scaffold_0	8	-27.986172	-1.386293	-27.986172	-27.986172	0.000000	-1.386293	-1.386293	-27.986172	-27.986172	-27.986172
scaffold_0	9	-27.755912	-1.386292	-27.755912	-27.755912	0.000000	-1.386292	-1.386292	-27.755912	-27.755912	-27.755912
scaffold_0	10	-8.689986	0.000000	-10.076280	-10.076280	-29.821151	-30.514277	-30.514277	-40.590558	-40.590558	-40.590558</code></pre>

                                Note that ANGSD also scales the log likelihoods by subtracting the highest likelihood from each likelihood. 
                                This has no effect on Referee's scoring.</p>

                                <p>If you have multiple genotype log-likelihood files from the same genome, you can put the paths to those files in a text file and
                                        give that to Referee as input through <code class="cb">-i</code> <strong>instead of</strong> <code class="cb">-gl</code></p>
            
                                    <p>Example <code>-i</code> input:
                                        <pre><code>/path/to/gl/file1.txt
/path/to/gl/file2.txt
/path/to/gl/file3.txt
/path/to/gl/file4.txt</code></pre>
                                    </p>
                                
                            </li>

                            <li>A reference FASTA file containing the sequences used to calculate genotype log-likelihoods (<code class="cb">-ref</code>).
                                <strong>The FASTA headers in this file must match those in the first column of the ANGSD or pileup file(s) specified with 
                                <code class="cb">-i</code> or <code class="cb">-gl</code></strong>. By default, Referee will trim the FASTA headers at
                                the first occurrence of a space character, so be sure to account for this. I admit this is a shaky workaround, but given
                                the non-standard nature of FASTA files its what I came up with. Please contact me if you would like some other header
                                format implemented.</li>
                        </ol>

                    <h3>Output</h3>
                        <p>With no specification, Referee will create one output file and one log file. A FASTQ output file can be created with
                            the <code>--fastq</code> flag and a Bed file can be created with the <code>--bed</code> flag.</p>

                        <p>By default, all outputs created by Referee will be files beginning with 
                            <code>referee-out-[start date]-[start time]-[random 6 char string]</code>. To change this, use the <code>-o</code> option.
                            For the following examples we assume <code>-o ref-out</code> has beend specified.</p>


                        <ol>
                            <li><h4>ref-out.log</h4>
                                <p>This is a log file containing information about the Referee run, including the options used and specified
                                    inputs and outputs. It also contains runtime and memory usage (if the Python module <code>psutil</code> is 
                                    available) info for each step. If you have many inputs or use many processors these runtime statistics can
                                    be distracting, so you can disable with <code>--quiet</code></p>
                            </li>

                            <li><h4>ref-out.txt</h4>
                                <p>This is a tab delimited output file containing the Referee scores for every position in the input reference
                                    genome. This file has the following columns:

                                    <pre><code>Scaffold ID  Position    Referee score</code></pre></p>

                                <p>Example:
                                    <pre><code>scaffold_0	5	0
scaffold_0	6	13
scaffold_0	7	13
scaffold_0	8	12
scaffold_0	9	12
scaffold_0	10	13</code></pre></p>

                                <p>If you specify the <code>--correct</code> option, then Referee will also output higher scoring bases for
                                    positions that score 0. This file will have two extra columns:
                                    <pre><code>Scaffold ID  Position    Referee score   Corrected base    Referee score for corrected base</code></pre></p>

                                    <p>Example with <code>--correct</code> and one position with a better scoring base (position 5):
                                            <pre><code>scaffold_0	5	0	A	6
scaffold_0	6	13		
scaffold_0	7	13		
scaffold_0	8	12		
scaffold_0	9	12		
scaffold_0	10	13</code></pre></p>

                            </li>

                            <li><h4>ref-out.fq</h4>
                                <p>If <code>--fastq</code> is specified Referee will create a FASTQ file with the reference genome annotated with Referee's scores 
                                    Referee scores are encoded as <a href="https://en.wikipedia.org/wiki/ASCII">ASCII</a> characters with the following method:
                                    
                                    <center><code>FASTQ score = ascii(Integer score + 35)</code></center></p>

                                    <p>For example, the <a href="https://en.wikipedia.org/wiki/ASCII">ASCII</a>  character <code>S</code> corresponds 
                                        to the decimal 83. That means the score at this position was 83 - 35 = 48.</p>

                                    <p>Example FASTQ output:
                                        <pre><code>@scaffold_0 1:40 length=40
GGTGTAGCCAGAGAGTAAANAATATGGTGAAGCCAGAGAG
+
!!!!#00//0442.45=CK"CKKLLKLKLKSRRRSSRSSS</code></pre></p>

                                    <p>If the <code>--correct</code> option is specified, corrected bases will be lower case. All others should be upper case.</p>
                            </li>

                            <li><h4>ref-out-bed-files/[scaffold ID].bed</h4>
                                <p>If <code>--bed</code> is specified Referee will create Bed files to visualize Referee scores in genome browsers. Referee will
                                    create one Bed file for every scaffold present in the input genotype likelihood file(s) and place them in the directory
                                    <code>ref-out-bed-files/</code>.</p>
                            </li>
                        </ol>

                    <div class="readme_divider"></div>
                    <h2>Options Table</h2>
                        <table class="pure-table pure-table-bordered pure-table-striped">
                            <thead><tr><th>Option</th><th>Description</th></tr></thead>
                            <tbody>
                                <tr><td><code>-gl</code></td>
                                    <td>A single pileup file or a single file containing log genotype likelihoods for every site in your genome with reads 
                                        mapped to it. Can be gzip compressed or not. If using pre-calculated log likelihoods, see the important information 
                                        below regarding the order of the columns in the file. Note: Only one of <code>-gl</code> or <code>-i</code> can be 
                                        specified.</td></tr>

                                <tr><td><code>-i</code></td>
                                    <td>A file containing paths to multiple pileup files or multiple genotype log likelihood files. One file path per line. 
                                        Note: Only one of <code>-gl</code> or <code>-i</code> can be specified.</td></tr>

                                <tr><td><code>-ref</code></td>
                                    <td>A FASTA formatted file containing the genome you wish to score. Can be gzip compressed or not. FASTA headers must 
                                        match the sequence IDs in column one of the pileup or genotype log likelihood file.</td></tr>

                                <tr><td><code>-o</code></td>
                                    <td>Referee will create at least 2 output files: a tab delimited score file and a log file. Use this option to specify 
                                        a prefix for these file names. Otherwise, they will default to <code>referee-out-[date]-[time]-[random string]</code>. 
                                        If <code>-i</code> is specified, this will be the name of the output directory.</td></tr>
                                        
                                <tr><td><code>--pileup</code></td>
                                    <td>If this option is set, Referee will read the input file(s) in pileup format and use this info to calculate genotype 
                                        likelihoods prior to the reference quality score.</td></tr> 
                                            
                                <tr><td><code>--mapq</code></td>
                                    <td>If pileup file(s) are given as input, set this to incorporate mapping quality into Referee's quality score calculation.
                                        Mapping quality can be output by samtools mpileup with the <code>-s</code> option, and will appear in the 7th column of the file. 
                                        If <code>--mapq</code> is not set, mapping qualities will be ignored even if they are present.</td></tr>

                                <tr><td><code>--fastq</code></td>
                                    <td>With this option, Referee scores will also be output in FASTQ format. Scores will be converted to 
                                        <a href="https://en.wikipedia.org/wiki/ASCII">ASCII</a> characters: score + 35 = ASCII char. Note 1: If 
                                        <code>--correct</code> is set, corrected bases will appear as lower case. Note 2: This option cannot be set with 
                                        <code>--mapped</code>.</td></tr>

                                <tr><td><code>--bed</code></td>
                                    <td>Referee can output scores in binned BED format for visualizing tracks of scores in most genome browsers. One <code>.bed</code>
                                        file will be created for each scaffold scored and these will be placed in a directory ending with -bed-files. 
                                        Note: This option cannot be set with <code>--mapped</code>.</td></tr>

                                <tr><td><code>--haploid</code></td>
                                    <td>Set this option if your input sequencing data comes from a haploid species. Referee will limit it's likelihood calculations
                                        to single base states. Note: This option can only be used with an input <code>--pileup</code> file.</td></tr>

                                <tr><td><code>--correct</code></td>
                                    <td>With this option, sites where reads do not support the called reference base (score <= 0) will have a higher scoring base 
                                        suggested. In the tab delimited output, the corrected base and score are reported in additional columns. In FASTQ output, the 
                                        corrected positions are indicated by lower case bases.</td></tr>

                                <tr><td><code>--mapped</code></td>
                                    <td>Only report scores for sites with reads mapped to them. Note: This option cannot be set with <code>--fastq</code> 
                                        or <code>--bed</code>.</td></tr>
                                        
                                <tr><td><code>--quiet</code></td>
                                    <td>Set this option to prevent Referee from printing out runtime statistics for each step.</td></tr>

                                <tr><td><code>-p</code></td>
                                    <td>The number of processes Referee can use.</td></tr>      
                            </tbody>
                        </table>

            </div>
		</div>
		<div class="pure-u-3-24" id="margin"></div>
	</div>

    {footer}
</body>
"""

######################
# Main block
######################
pagefile = "readme.html";
print("Generating " + pagefile + "...");
title = "Referee README"

head = RC.readHead(title);
nav = RC.readNav(pagefile);
footer = RC.readFooter();

outfilename = "../../" + pagefile;

with open(outfilename, "w") as outfile:
    outfile.write(html_template.format(head=head, nav=nav, footer=footer));