#!/usr/bin/python
#############################################################################
# Reference genome quality score annotation
# This is the main interface.
#
# Gregg Thomas
# Fall 2018
#############################################################################

import sys, os, multiprocessing as mp, lib.refcore as RC, lib.ref_calc as CALC, \
	lib.opt_parse as OP, lib.ref_out as OUT, lib.global_vars as GV
try:
	from Bio import SeqIO
except:
	sys.exit("\n*** ERROR: Your installation of Python is missing the Biopython module. Please install the module.\n");
# Have to have Biopython to read the FASTA files.

#############################################################################

def referee(globs):
	files, globs, step_start_time = OP.optParse(globs);
	# Getting the input parameters from optParse.

	for file_num in files:
		if globs['stats']:
			step_start_time  = RC.report_stats(globs, "Calc " + str(file_num), step_start=step_start_time);

		if globs['fastq']:
			fq_seq, fq_scores, fq_curlen, fq_lastpos = [], [], 0, 1;
		# Variables for FASTQ output.
		with open(files[file_num]['out'], "w") as outfile:
			if globs['num-procs'] == 1:
				for line in open(files[file_num]['in']):
					outdict = CALC.refCalc2(line, globs);
					if globs['fastq']:
						fq_seq, fq_scores, fq_curlen, fq_lastpos = OUT.outputFastq(outdict, outfile, fq_seq, fq_scores, fq_curlen, fq_lastpos, globs);
					else:
						OUT.outputTab(outdict, outfile,  globs);


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
		step_start_time = RC.report_stats(globs, "End program", step_start=step_start_time, stat_end=True);

	return;
#############################################################################

if __name__ == '__main__':
# Main is necessary for multiprocessing to work on Windows.
	globs = GV.init();
	RC.startProg(globs);
	referee(globs);
	RC.endProg(globs);

#############################################################################