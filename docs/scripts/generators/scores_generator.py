############################################################
# For Referee docs, 11.19
# This generates the file "scores.html"
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

    {main}

    {footer}
</body>
"""

######################
# Main block
######################
pagefile = "scores.html";
print("Generating " + pagefile + "...");
title = "Referee's scores"

head = RC.readHead(title);
nav = RC.readNav(pagefile);
scoresmain = RC.readScores();
footer = RC.readFooter();

outfilename = "../../" + pagefile;

with open(outfilename, "w") as outfile:
    outfile.write(html_template.format(head=head, nav=nav, main=scoresmain, footer=footer));