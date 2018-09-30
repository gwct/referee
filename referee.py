#!/usr/bin/python
#############################################################################
# Reference genome quality score annotation
# This is the main interface.
#
# Gregg Thomas
# Fall 2018
#############################################################################

import sys, os, multiprocessing as mp, lib.refcore as RC, lib.ref_calc as CALC, \
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

	if globs.num_procs == 1:
		for f in files.iteritems():
			CALC.refCalc(f);
	# A serial version.
	else:
		pool = mp.Pool(processes = globs.num_procs);
		for result in pool.imap_unordered(CALC.refCalc, files.iteritems()):
			continue;
	# The parallel version

	return;
#############################################################################

if __name__ == '__main__':
# Necessary for multiprocessing to work on Windows.
	globs.init();
	print("");
	RC.printWrite(globs.logfilename, 1, "# =========================================================================");
	RC.printWrite(globs.logfilename, 1, "# Welcome to Referee -- Reference genome quality score calculator.");
	RC.printWrite(globs.logfilename, 1, "# The date and time at the start is: " + RC.getDateTime());
	RC.printWrite(globs.logfilename, 1, "\n" + "-" * 40 + "\n");
	RC.printWrite(globs.logfilename, 1, "** IMPORTANT! Please ensure that your input genotype likelihood files are tab delimited with the following columns in this exact order:");
	RC.printWrite(globs.logfilename, 1, "** Scaffold\tPosition\tAA\tAC\tAG\tAT\tCC\tCG\tCT\tGG\tGT\tTT");
	RC.printWrite(globs.logfilename, 1, "** IMPORTANT! Failure to do so will result in inaccurate calculations!!");
	RC.printWrite(globs.logfilename, 1, "\n" + "-" * 40 + "\n");
	referee();
	RC.endProg();

#############################################################################