############################################################
# For Referee docs, 11.19
# This generates the file "walkthrough.html"
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
				<h1>Referee walkthrough</h1>
                <h3>This page is a brief guide with command examples to go from reads and assembly to an assembly annotated with
                     Referee's quality scores. We will first map all the reads used to make the assembly back 
                     to the assembly to obtain a single sorted BAM file. Then we will show how to use the BAM file to calculate genotype 
                     likelihoods with ANGSD or mpileup and Referee and produce a FASTQ reference file.</h3>
                
                <p><strong>Important note:</strong> The following example is for Illumina reads. If you have reads from other technologies, 
                    the tools and steps may be different.</p>
                
                <h2>Step 0: Software used</h2>
                    <p>The following walkthrough assumes you have these programs available to use:</p>

                    <p><a href="https://github.com/lh3/bwa">BWA</a> for read mapping.</p>
                    <p><a href="https://github.com/samtools/samtools">Samtools</a> and <a href="https://broadinstitute.github.io/picard/">Picard</a> for 
                        manipulation of SAM/BAM files and creating a pileup file (if necessary).</p>
                    <p>If you want to pre-calculate genotype log-likelihoods instead of creating a pileup and having Referee calculate them, we 
                        use <a href="https://github.com/ANGSD/angsd">ANGSD</a>.</p>
                    <p><a href="https://github.com/gwct/referee">Referee</a> for quality score calculation.</p>

                <h2>Step 1: Preparing the reference FASTA file.</h2>
                    <p>We'll start from the point of having a completed genome/transcriptome assembly in <strong>fasta</strong> format: <code>reference.fa</code></p>

                    <p>First we'll need to do the following 3 things to prepare the reference fasta file.</p>

                    <ol>
                        <li>Index the reference for mapping.
                            <pre><code>bwa index reference.fa</code></pre>

                            <p>This command will produce 5 files (i.) <strong>reference.fa.amb</strong>, (ii.) <strong>reference.fa.ann</strong>, (iii.) 
                                <strong>reference.fa.bwt</strong>, (iv.) <strong>reference.fa.pac</strong>, (v.) <strong>reference.fa.sa</strong>. 
                                You won't need to look at these files, but they are used by BWA later on.</p>
                        </li>

                        <li>Index the reference for samtools. Though not necessary for mapping, it will be necessary to have this index later on:
                            <pre><code>samtools faidx reference.fa</code></pre>

                            <p>This command will produce the file <strong>reference.fai</strong>. You won't need to look at this file, but it will be 
                                used by samtools later on.</p>
                        </li>

                        <li>We can also create the sequence dictionary with Picard. This is necessary if BWA doesn't create a proper header in the SAM file:
                            <pre><code>java -jar picard.jar CreateSequenceDictionary R=reference.fa O=reference.dict</code></pre>
                            
                            <p>This command will produce the file <strong>reference.dict</strong>.</p>
                        </li>
                    </ol>

                    <p>In all, these commands simply create files that make the reference easier to read for these programs.</p>

                <h2>Step 2: Mapping the reads back to your assembly.</h2>
                    <p>In addition to the assembled fasta file, we should also have all reads that were used to make this assembly 
                        in <strong>fastq</strong> format. These can be paired end or not, but for this example we will assume 
                        paired end reads: <code>reads_1.fq</code> and <code>reads_2.fq</code></p>

                    <p>If there were multiple sequencing runs there will be multiple fastq files that were used to make the assembly. This 
                        just means you'll have to run some of the following commands on each fastq file set.</p>

                    <p>To map the reads back to the reference assembly, we use BWA, but any mapping software can be used as long as it makes sense 
                        the subsequent steps (i.e. produces SAM files as output).</p>
                    <pre><code>bwa mem reference.fa reads_1.fq reads_2.fq &gt; reads-mapped.sam</code></pre>
                    
                    <p>Remember, if you have multiple sequencing runs, you'll want to run BWA on each one, which will result in multiple SAM files.</p>

                <h2>Step 3: Preparing the BAM file.</h2>
                <p>If the header of the SAM file is improperly formatted from BWA (i.e. the first line does not start with
                     <span class="citation">@HD</span>), you can use the reference dictionary created with Picard in Step 1 to fix it:</p>
                <pre><code>java -jar picard.jar ReplaceSamHeader I=reads-mapped.sam HEADER=reference.dict O=reads-mapped-hd.sam</code></pre>

                <p>Next, convert the SAM file to a BAM file with samtools:</p>
                <pre><code>samtools view -b reads-mapped-hd.sam &gt; reads-mapped-hd.bam</code></pre>

                <p>If you had multiple sequencing runs you should have run <code>bwa mem</code> and <code>samtools view</code> 
                    (and possibly <code>picard.jar ReplaceSamHeader</code>) on each read set, resulting multiple BAM files. If this is the 
                    case, we can merge the BAM files now:</p>
                <pre><code>samtools merge reads-mapped-merged.bam reads-mapped-hd-1.bam reads-mapped-hd-2.bam ... etc.</code></pre>

                <p>Then we sort the single BAM file:</p>
                <pre><code>samtools sort reads-mapped-hd.bam -o reads-mapped-hd-sorted.bam</code></pre>

                <p>As a result of these steps, you should have a single <strong>.bam</strong> file, regardless of how many sequencing 
                    runs you had as input (thanks to the <code>merge</code> step).</p>

                <h2>Step 4: Preparing inputs for Referee</h2>
                    <p>At this point, you could either pre-calculate genotype log-likelihoods with whatever method you 
                        choose (see <a href="https://github.com/gwct/referee">README</a> for proper file format), or make a 
                        pileup file so Referee can calulate genotype likelihoods. You only need to do one of Steps 4a or 4b.</p>

                    <ul style="list-style: none;">
                        <li>
                            <h3>Step 4a: Calculating genotype log-likelihoods with ANGSD</h3>
                                <p>If you want to pre-calculate genotype log-likelihoods for Referee, you can use any program you want. 
                                    However, <a href="https://github.com/ANGSD/angsd">ANGSD</a> is easy and provides the likelihoods in 
                                    a format that Referee can read. Here is how to use ANGSD for genotype log-likelihood calculation:</p>
                                <pre><code>angsd -GL 2 -i reads-mapped-hd-sorted.bam -ref reference.fa -minQ 0 -doGlf 4 -o reads-gl</code></pre>

                                <p>This will produce 2 files: <strong>reads-gl.glf.gz</strong> which contains the genotype log-likelihoods and 
                                    <strong>reads-gl.arg</strong> which is a log file produced by ANGSD.</p>

                                <p>A brief explanation of the options used in the above command:</p>
                                <table class="pure-table pure-table-striped" style="width: auto !important; margin-left: auto; margin-right: auto;">
                                    <tr><td><code>-GL 2</code></td> <td>Indicates we want to calculate genotype likelihoods</td></tr>
                                    <tr><td><code>-minQ 0</code></td> <td>Sets the minimum mapping quality of a site to 0 to ensure all sites are used</td></tr>
                                    <tr><td><code>-doGlf 4</code></td> <td>Use the original GATK method for calculating genotype likelihoods (same as Referee)</td></tr>
                                </table>
                            </li>
                        <li>
                            <h3>Step 4b: Generate a pileup file to calculate genotype likelihoods with Referee</h3>
                                <p>To have Referee calculate the genotype likelihoods, we'll need the mapped reads in pileup format:</p>
                                <pre><code>samtools mpileup -d 999999999 -f reference.fa -Q 0 -s -B -o reads.pileup reads-mapped-hd-sorted.bam</code></pre>

                                <p>This will produce a single file, <strong>reads.pileup</strong></p>

                                <p>A brief explanation of the options used in the above command:</p>
                                <table class="pure-table pure-table-striped" style="width: auto !important; margin-left: auto; margin-right: auto;">
                                    <tr><td><code>-d 999999999</code></td> <td>Sets the maximum read depth to count a site to a value high enough such 
                                        that all sites will be counted.</td></tr>
                                    <tr><td><code>-Q 0</code></td> <td>Sets the minumum quality score for a site to be counted to 0. Again this ensures all 
                                        sites are counted.</td></tr>
                                    <tr><td><code>-s</code></td> <td>Include mapping quality in the pileup output (optional).</td></tr>
                                    <tr><td><code>-B</code></td> <td>Disables mpileup's BAQ adjustment to the base quality scores.</td></tr>
                                </table>
                            </li>
                    </ul>

                    <p><strong>Important note:</strong> Referee may give different scores depending on how you calculate genotype likelihoods.
                        This is because different programs may filter or trim different reads when calculating the likelihoods. Just be aware
                        of this moving forward. To guarantee that mpileup and ANGSD produce the same scores, make sure they use ALL reads by
                        using the <code>-x</code> option in mpileup and the <code>-remove_bads 0</code> option in ANGSD, though this is not
                        the best practice.</p>

                <h2>Step 5: Calculate reference quality scores with Referee</h2>
                    <p>If you used pre-calculated genotype log-likelihoods with ANGSD:</p>
                    <pre><code>referee.py -gl reads-gl.glf.gz -ref reference.fa --fastq --correct -o reference</code></pre>

                    <p>Or if you have a pileup for Referee to use:</p>
                    <pre><code>referee.py -gl reads.pileup -ref reference.fa --pileup --fastq --correct -o reference</code></pre>

                    <p>A brief explanation of the options used in the above command:</p>
                    <table class="pure-table pure-table-striped" style="width: auto !important; margin-left: auto; margin-right: auto;">
                        <tr><td><code>-gl</code></td> <td>This is the input file for Referee. It is the output file from step 4, either the .glf.gz file 
                            from ANGSD or the pileup file.</td></tr>
                        <tr><td><code>-ref</code></td> <td>The reference fasta file.</td></tr>
                        <tr><td><code>--pileup</code></td> <td>This flag indicates that the input specified with <code>-gl</code> is in pileup format. If 
                            you have a .glf.gz file from ANGSD, leave this off.</td></tr>
                        <tr><td><code>--fastq</code></td> <td>This tells Referee to produce the FASTQ output file.</td></tr>
                        <tr><td><code>--correct</code></td> <td>This tells Referee to correct sites that have more support for an alternate base than the 
                            one called in the assembly.</td></tr>
                        <tr><td><code>-o</code></td> <td>This is the prefix for all output created by Referee.</td></tr>
                    </table>

                    <p>This will produce the following files:</p>
                    <table class="pure-table pure-table-striped" style="width: auto !important; margin-left: auto; margin-right: auto;">
                        <tr><td><strong>reference.log</strong></td> <td>A log containing info for the run.</td></tr>
                        <tr><td><strong>reference.txt</strong></td> <td>Tab delimited scores (columns: scaffold, position, Referee score, corrected base, 
                            corrected base score).</td></tr>
                        <tr><td><strong>reference.fq</strong></td> <td>FASTQ formatted reference genome.</td></tr>
                    </table>

                    <p>See the <a href="readme.html">README</a> for more information on these file formats.</p>
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
pagefile = "walkthrough.html";
print("Generating " + pagefile + "...");
title = "Referee walkthrough"

head = RC.readHead(title);
nav = RC.readNav(pagefile);
footer = RC.readFooter();

outfilename = "../../" + pagefile;

with open(outfilename, "w") as outfile:
    outfile.write(html_template.format(head=head, nav=nav, footer=footer));