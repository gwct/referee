#!/usr/bin/python
#############################################################################
# Reference genome quality score annotation
# This is the main interface.
#
# Gregg Thomas
# Fall 2018
#############################################################################

import sys, os, timeit, multiprocessing as mp, lib.refcore as RC, \
	lib.opt_parse as OP, lib.global_vars as globs
try:
    from Bio import SeqIO
except:
    sys.exit("\n*** ERROR: Your installation of Python is missing the Biopython module. Please install the module.\n");
# First check if the argparse module is installed. If not, the input options cannot be parsed.

#############################################################################

def referee():

	###########################
	### Prep
	files = OP.optParse(0);
	# Getting the input parameters from optParse.

	print files;

	return;


#############################################################################

if __name__ == '__main__':
# Necessary for multiprocessing to work on Windows.
	globs.init();
	print("");
	RC.printWrite(globs.logfilename, 1, "# =========================================================================");
	RC.printWrite(globs.logfilename, 1, "# Welcome to Referee -- Reference genome quality score calculator.");
	RC.printWrite(globs.logfilename, 1, "# The date and time at the start is: " + RC.getDateTime());
	referee();
	RC.endProg();

#############################################################################