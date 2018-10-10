#!/usr/bin/python
#############################################################################
# Reference genome quality score annotation
# This is the main interface.
#
# Gres Thomagg
# Fall 2018
#############################################################################

import sys, os, multiprocessing as mp, shutil, lib.refcore as RC, lib.ref_calc as CALC, \
	lib.opt_parse as OP, lib.ref_out as OUT, lib.global_vars as GV

#############################################################################

def referee(files, globs, step_start_time):
	if globs['stats']:
		import psutil
		step_start_time  = RC.report_stats(globs, "Index ref fasta", step_start=step_start_time);
	# Initialize the stats output if --stats is set

	if globs['fasta'] == 1:
		globs['ref'] = RC.fastaReadInd(globs['reffile']);
	# My fasta index functions
	elif globs['fasta'] == 2:
		globs['ref'] = RC.fastaRead(globs['reffile'], globs);
	# My fasta dict function
	elif globs['fasta'] == 3:
		from Bio import SeqIO
		globs['ref'] = SeqIO.to_dict(SeqIO.parse(globs['reffile'], "fasta"))
	# Index the reference FASTA file.

	if globs['stats']:
		step_start_time  = RC.report_stats(globs, "Calcs", step_start=step_start_time);
		file_start_time = step_start_time;
	# --stats update.

	if globs['num-procs'] == 1:
		for file_num in files:
			result = CALC.refCalc((file_num, files[file_num], globs));
			files[file_num]['scaffs'] = result[1];
			if globs['stats']:
				file_start_time = RC.report_stats(globs, "File " + str(result[0]), file_start_time);
	# The serial version.
	else:
		if len(files) == 1:
			if globs['stats']:
				step_start_time  = RC.report_stats(globs, "Split files", step_start=step_start_time);
			new_files = OP.multiSplit(files, globs);
		else:
			new_files = files;
		# If multiple processors are available for 1 file, we split the file into chunks.

		pool = mp.Pool(processes = globs['num-procs']);
		if globs['stats']:
			for result in pool.imap(RC.getSubPID, range(globs['num-procs'])):
				globs['pids'].append(result);
		for result in pool.imap(CALC.refCalc, ((file_num, new_files[file_num], globs) for file_num in new_files)):
			if len(files) == 1:
				new_files[file_num]['scaffs'] = result[1];
			else:
				files[file_num]['scaffs'] = result[1];
			if globs['stats']:
				file_start_time = RC.report_stats(globs, "File " + str(result[0]), file_start_time);
		# Creates the pool of processes and passes each file to one process to calculate scores on.

		if len(files) == 1:
			if globs['stats']:
				step_start_time  = RC.report_stats(globs, "Merge files", step_start=step_start_time);
			OP.mergeFiles(files[1]['out'], new_files, globs);
			for file_num in new_files:
				files[1]['scaffs'] = files[1]['scaffs'].union(new_files[file_num]['scaffs']);
			
		# Merges the split tmp files back into a single output file.
	# The parallel verison.
	if not globs['mapped']:
		for file_num in files:
			print file_num, files[file_num]['scaffs'];
			if globs['stats']:
				step_start_time  = RC.report_stats(globs, "Add unmapped " + str(file_num), step_start=step_start_time);
			OUT.addUnmapped(files[file_num], globs);
			RC.printWrite(globs['logfilename'], globs['log-v'], "+ Renaming tmp file to output file: " + files[file_num]['tmpfile'] + " -> " + files[file_num]['out']);
			shutil.move(files[file_num]['tmpfile'], files[file_num]['out']);
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
