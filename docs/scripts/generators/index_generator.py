############################################################
# For Referee docs, 11.19
# This generates the file "index.html"
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
				<img class="pure-img" id="logo_main" src="img/ref-logo.png">
				<h1>Referee: Genome assembly quality scores</h1>
				<h3>Referee is a program to calculate a quality score for every position in a genome assembly. This allows for easy filtering of 
					low quality sites for any downstream analysis.</h3>

				<p id="paper">Thomas GWC and Hahn MW. 2019. Referee: reference assembly quality scores. <em>Genome Biology and Evolution</em>
				<a href="https://doi.org/10.1093/gbe/evz088" target="_blank">10.1093/gbe/evz088</a></p>

				<div id="buttons_container">
						<a class="button-secondary pure-button" id="install_btn" href="readme.html">README &raquo;</a><span id="buffer"></span>
						<a class="button-secondary pure-button" id="install_btn" href="https://github.com/gwct/referee/releases/latest" target="_blank">Download &raquo;</a>
				</div>

				<h3>Update: v1.2 &#8212; 08.25.2020</h3>
				<p>Referee now implements a more streamlined multi-processing scheme that does not require duplications of large input files or multiple read-throughs
					of input files!</p>

				<h3>About</h3>
				<p>Modern genome sequencing technologies provide a succinct measure of quality at each position in every read, however all of 
					this information is lost in the assembly process. Referee summarizes the quality information from the reads that map to a site 
					in an assembled genome to calculate a quality score for each position in the genome assembly.</p>

				<p>We accomplish this by first calculating genotype likelihoods for every site. For a given site in a diploid genome, there 
					are 10 possible genotypes (AA, AC, AG, AT, CC, CG, CT, GG, GT, TT). Referee takes as input the genotype likelihoods 
					calculated for all 10 genotypes given the called reference base at each position. For haploid genomes, the likelihood
					calculations are limited to the four bases with the <code>--haploid</code> option.</p>

				<p>To obtain these likelihoods, one must first map the reads used to make the assembly back onto the finished assembly. 
					Then these reads can be used to calculate genotype likelihoods using any method/program. <a href="calcs.html">Referee can calculate</a> 
					the likelihoods from a pileup file as input or use pre-calculated log likelihoods, such as those output by 
					<a href="https://github.com/ANGSD/angsd">ANGSD</a>. Then, Referee compares the log of the ratio of the sum of 
					genotype likelihoods for genotypes that contain the reference base vs. the sum of those that do not contain the reference base. 
					Positive scores indicate support for the called reference base while negative scores indicate support for some other base. Scores close 
					to 0 indicate less confidence while higher scores indicate more confidence in the reference base. Scores range from 0 to 91, with some 
					special cases (see <a href="readme.html">README</a>). With the <code>--correct</code> option specified Referee will 
					also output the highest scoring base for sites with negative scores.</p>

				<center>
						<h3><strong>For more information on the usage and inputs, see the <a href="readme.html">README</a></strong></h3>
				</center>
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
pagefile = "index.html";
print("Generating " + pagefile + "...");
title = "Referee"

head = RC.readHead(title);
nav = RC.readNav(pagefile);
footer = RC.readFooter();

outfilename = "../../" + pagefile;

with open(outfilename, "w") as outfile:
    outfile.write(html_template.format(head=head, nav=nav, footer=footer));