#!/usr/bin/python
#############################################################################
# Reference genome quality score annotation
# This is the main interface.
#
# Gregg Thomas
# Fall 2018
#############################################################################

import sys, os, multiprocessing as mp, lib.refcore as RC, lib.ref_calc as CALC, \
	lib.opt_parse as OP, lib.global_vars as GV
try:
	from Bio import SeqIO
except:
	sys.exit("\n*** ERROR: Your installation of Python is missing the Biopython module. Please install the module.\n");
# Have to have Biopython to read the FASTA files.

#############################################################################

def referee(globs):
	files, globs = OP.optParse(globs);
	# Getting the input parameters from optParse.

	for file_num in files:
		if globs['num-procs'] == 1:
			start, last_scaff, first = 1, "", True;
			for line in open(files[file_num]['in']):
				result = RC.refCalc2(line, start, last_scaff, first, files[file_num]['ref'], globs);


	# if globs['num-procs'] == 1:
	# 	if globs['stats']:
	# 		globs['stepstartime'] = RC.report_stats(globs, "Calculating scores");
	# 	for f in files.iteritems():
	# 		CALC.refCalc(f);
	# # A serial version.
	# else:
	# 	if len(files) == 1:
	# 		if globs['stats']:
	# 			globs['stepstartime'] = RC.report_stats(globs, "Splitting files");
	# 		files = OP.multiPrep(files);
	# 	pool = mp.Pool(processes = globs['num-procs']);

	# 	if globs['stats']:
	# 		globs['stepstartime'] = RC.report_stats(globs, "Calculating scores");
	# 		for result in pool.imap_unordered(RC.getSubPID, range(globs['num-procs'])):
	# 			globs['pids'].append(result);

	# 	for result in pool.imap_unordered(CALC.refCalc, files.iteritems()):
	# 		continue;
	# # The parallel version

	if globs['stats']:
		globs['stepstartime'] = RC.report_stats(globs, "End program", stat_end=True);

	return;
#############################################################################

if __name__ == '__main__':
# Main is necessary for multiprocessing to work on Windows.
	globs = GV.init();
	RC.startProg(globs);
	referee(globs);
	RC.endProg(globs);

#############################################################################