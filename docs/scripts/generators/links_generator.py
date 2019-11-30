############################################################
# For Referee docs, 11.19
# This generates the file "links.html"
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
                    <h1>Links</h1>
                    <h3>People and places related to Referee:</h3>
                        <ul>
                            <p><a href="http://www.indiana.edu/~hahnlab/" target="_blank">Hahn lab</a> / Referee was developed in Matthew Hahn's lab 
                                at Indiana University</p>
                            <p><a href="https://github.com/gwct/referee" target="_blank">Referee github</a> / Referee's github repository.</p>	
                        </ul>
                    <h3>Helpful software:</h3>
                        <ul>
                            <p><a href="https://github.com/lh3/bwa" target="_blank">BWA</a> / Read mapping software.</p>
                            <p><a href="https://broadinstitute.github.io/picard/" target="_blank">Picard</a> / Software for handling NGS data.</p>
                            <p><a href="https://github.com/samtools/samtools" target="_blank">Samtools</a> / Software for handling NGS data, especially mapped reads.</p>
                            <p><a href="https://github.com/ANGSD/angsd" target="_blank">ANGSD</a> / Software for calculating genotype log-likelihoods 
                                (and many other things).</p>
                            <p><a href="https://genome.ucsc.edu/" target="_blank">UCSC Genome browser</a> / A web based genome browser that accepts Referee's
                                Bed file outputs for visualization.</p>
                        </ul>
                    <!-- <h3>Previous versions of GRAMPA</h3>
                    <ul>
                        <p><a href="prev/v1.1.zip" download>Version 1.1</a> / March 22, 2016 / Implemented gene tree filtering and several useful options. No parallelization.</p>
                        <p><a href="prev/v1.0.zip" download>Version 1.0</a> / Summer 2015 / The first release. No gene tree filtering.</p>
                    </ul> -->
                </div>
            </div>
            <div class="pure-u-18-24" id="margin"></div>
        </div>

    {footer}
</body>
"""

######################
# Main block
######################
pagefile = "links.html";
print("Generating " + pagefile + "...");
title = "Referee links"

head = RC.readHead(title);
nav = RC.readNav(pagefile);
footer = RC.readFooter();

outfilename = "../../" + pagefile;

with open(outfilename, "w") as outfile:
    outfile.write(html_template.format(head=head, nav=nav, footer=footer));