#!/usr/bin/python
#############################################################################
# Reference genome quality score annotation
# This is the main interface.
#
# Gregg Thomas
# Fall 2018
#############################################################################

import sys, os, multiprocessing as mp, shutil, lib.refcore as RC, lib.ref_calc as CALC, \
	lib.opt_parse as OP, lib.ref_out as OUT, lib.global_vars as GV

#############################################################################

def referee(files, globs, step_start_time):
	if globs['stats']:
		if globs['psutil']:
			import psutil
		step_start_time = RC.report_stats(globs, "Index ref fasta", step_start=step_start_time);
	# Initialize the stats output if --stats is set

	globs['ref'] = RC.fastaReadInd(globs['reffile']);
	# Index the reference FASTA file.

	if globs['pileup']:
		if globs['stats']:
			step_start_time = RC.report_stats(globs, "GL Init", step_start=step_start_time);
		globs['probs'] = CALC.glInit(globs['mapq']);

	if globs['stats']:
		file_start_time = RC.report_stats(globs, "Calcs", step_start=step_start_time);
	# --stats update.

	if globs['num-procs'] == 1:
		for file_num in files:
			result = CALC.refCalc((file_num, files[file_num], globs));
			if globs['stats']:
				step_start_time = RC.report_stats(globs, "File " + str(result) + " calcs done", file_start_time);
	# The serial version.
	else:
		if len(files) == 1:
			if globs['stats']:
				step_start_time = RC.report_stats(globs, "Split files", step_start=step_start_time);
			new_files = OP.multiSplit(files, globs);
		else:
			new_files = files;
		# If multiple processors are available for 1 file, we split the file into chunks.

		pool = mp.Pool(processes = globs['num-procs']);
		if globs['stats'] and globs['psutil']:
			for result in pool.imap(RC.getSubPID, range(globs['num-procs'])):
				globs['pids'].append(result);
		for result in pool.imap(CALC.refCalc, ((file_num, new_files[file_num], globs) for file_num in new_files)):
			if globs['stats']:
				step_start_time = RC.report_stats(globs, "File " + str(result) + " calcs done", file_start_time);
		# Creates the pool of processes and passes each file to one process to calculate scores on.

		if len(files) == 1:
			if globs['stats']:
				step_start_time = RC.report_stats(globs, "Merge files", step_start=step_start_time);
			OP.mergeFiles(files[1]['out'], new_files, globs);
		# Merges the split tmp files back into a single output file.
	# The parallel verison.

	if globs['stats']:
		file_start_time = RC.report_stats(globs, "Adding unmapped ", step_start=step_start_time);
	if not globs['mapped']:
		if globs['num-procs'] == 1 or len(files) == 1:
			for file_num in files:
				result = OUT.addUnmapped((file_num, files[file_num], globs));
				if globs['stats']:
					step_start_time = RC.report_stats(globs, "File " + str(result) + " unmapped done", step_start=file_start_time);
					RC.printWrite(globs['logfilename'], globs['log-v'], "+ Renaming tmp file to output file: " + files[result]['tmpfile'] + " -> " + files[result]['out']);
				shutil.move(files[result]['tmpfile'], files[result]['out']);
		# Serial version to add unmapped sites.
		else:
			for result in pool.imap(OUT.addUnmapped, ((file_num, files[file_num], globs) for file_num in new_files)):
				if globs['stats']:
					step_start_time = RC.report_stats(globs, "File " + str(result) + " unmapped done", step_start=file_start_time);
				RC.printWrite(globs['logfilename'], globs['log-v'], "+ Renaming tmp file to output file: " + files[result]['tmpfile'] + " -> " + files[result]['out']);
				shutil.move(files[result]['tmpfile'], files[result]['out']);

		# Parallel version to add unmapped sites.
		
	# If all positions are to be assigned a score, this fills in the unmapped positions. Requires one pass through of the output file.

	if globs['stats']:
		step_start_time = RC.report_stats(globs, "End program", step_start=step_start_time, stat_end=True);
	# A step update for --stats.

	return;
#############################################################################

if __name__ == '__main__':
# Main is necessary for multiprocessing to work on Windows.
	globs = GV.init();
	files, globs, step_start_time = OP.optParse(globs);
	# Getting the input parameters from optParse.
	referee(files, globs, step_start_time);
	RC.endProg(globs);

#############################################################################
