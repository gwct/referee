import sys, os, refcore as RC
#############################################################################

def optParse(globs):
# This function handles the command line options and prepares the output directory and files.
	#try:
	#	from Bio import SeqIO
	#except:
	#	sys.exit("\n*** ERROR: Your installation of Python is missing the Biopython module. Please install the module with: pip install biopython\n")
	# First check if the argparse module is installed. If not, the input options cannot be parsed.
	try:
		import argparse;
	except:
		sys.exit("\n*** ERROR: Your installation of Python is missing the argparse module. Please try a different version of Python (2.7 or later) or install the module.\n")
	# First check if the argparse module is installed. If not, the input options cannot be parsed.
	try:
		import psutil
		globs['psutil'] = True;
	except:
		globs['psutil'] = False;
	# Check if psutil is installed for memory usage stats.

	parser = argparse.ArgumentParser(description="Referee: Reference genome quality scoring.");

	parser.add_argument("-ref", dest="ref_file", help="The FASTA assembly to which you have mapped your reads.", default=False);
	parser.add_argument("-gl", dest="gl_file", help="The file containing the genotype likelihood calculations.", default=False);
	parser.add_argument("-i", dest="input_list", help="A file containing the paths to multiple input files containing genotype likelihoods and their reference FASTA files. Each line should contain one genotype likelihood file path and one FASTA file path separated by a tab.", default=False);
	# Inputs
	parser.add_argument("-o", dest="out_dest", help="A PREFIX name for the output files/directories. Default: referee-out-[date]-[time]", default=False);
	# Output
	parser.add_argument("-p", dest="processes", help="The number of processes Referee should use. Default: 1.", default=False);
	# User params
	parser.add_argument("--pileup", dest="pileup_flag", help=argparse.SUPPRESS, action="store_true", default=False);
	parser.add_argument("--fastq", dest="fastq_flag", help="Set this option to output in FASTQ format in addition to the default tab delimited format.", action="store_true", default=False);
	parser.add_argument("--correct", dest="correct_flag", help="Set this option to allow Referee to suggest alternate reference bases for sites that score 0.", action="store_true", default=False);
	parser.add_argument("--mapped", dest="mapped_flag", help="Set this to calculate scores only for positions that have reads mapped to them.", action="store_true", default=False);
	parser.add_argument("--mapq", dest="mapq_flag", help="Set with --pileup to indicate whether to consider mapping quality scores in the final score calculation. These should be in the seventh column of the pileup file.", action="store_true", default=False);
	parser.add_argument("--quiet", dest="quiet_flag", help="Set this flag to prevent Referee from reporting detailed information about each step.", action="store_true", default=False);
	# User options	
	#parser.add_argument("-s", dest="startpos", help="Set the starting position for the input file(s). Default: 1", default=False);
	#parser.add_argument("-e", dest="endpos", help="Set the end position for the input file(s). Default: last position in assembly/scaffold", default=False);
	#parser.add_argument("-c", dest="score_cutoff", help="The cut-off score for --correct. Sites that score below this cut-off will have an alternate reference base suggested. If --correct isn't set, this option is ignored. Default: 1", default=False);
	#parser.add_argument("--stats", dest="stats_opt", help=argparse.SUPPRESS, action="store_true", default=False);
	parser.add_argument("--allcalcs", dest="allcalc_opt", help=argparse.SUPPRESS, action="store_true", default=False);
	parser.add_argument("-f", dest="fasta_opt", help=argparse.SUPPRESS, type=int, default=1);
	parser.add_argument("-s", dest="score_opt", help=argparse.SUPPRESS, type=int, default=1);
	# Performance tests

	args = parser.parse_args();
	# The input options and help messages
	if args.out_dest:
		globs['logfilename'] = args.out_dest + "-log.log";

	if args.fasta_opt in [1,2,3]:
		globs['fasta'] = args.fasta_opt;
	else:
		RC.errorOut(0, "Invalid fasta opt.", globs);

	if args.fasta_opt in [1,2]:
		globs['method'] = args.score_opt;
	else:
		RC.errorOut(0, "Invalid score method opt.", globs);

	if not args.input_list and not args.gl_file:
		RC.errorOut(1, "No input method specified. Make sure one input method (either just -i or -gl) is specified.", globs);
	if args.input_list and args.gl_file:
		RC.errorOut(2, "Only one input method (-i or -gl) should be specified.", globs);
	# Make sure at least one and only one input method has been specified (either -i or -gl).

	if not args.ref_file:
		RC.errorOut(3, "A reference genome in FASTA format must be provided with -ref", globs);
	elif not os.path.isfile(args.ref_file):
		RC.errorOut(4, "Cannot find reference genome FASTA file: " + args.ref_file, globs);
	else:
		globs['reffile'] = args.ref_file;
	# Check and read the reference genome file.

	if args.processes and not args.processes.isdigit():
		RC.errorOut(5, "-p must be an integer value greater than 1.", globs);
	elif args.processes:
		globs['num-procs'] = int(args.processes);
	# Checking the number of processors option.

	if args.fastq_flag:
		globs['fastq'] = True;
	# Checking the fastq option.

	if args.mapped_flag:
		if args.fastq_flag:
			RC.errorOut(6, "Cannot output to --fastq when only doing --mapped positions. Pick one.", globs);
			# Raise error if both --fastq and --mapped are selected. FASTQ output without all positions would be confusing.
		else:
			globs['mapped'] = True;
	# Checking the mapped option.

	if args.correct_flag:
		globs['correct-opt'] = True;
	# Checking the correct option.

	if args.allcalc_opt:
		globs['allcalc'] = True;
		globs['fastq'] = False;

	if args.pileup_flag:
		globs['pileup'] = True;
		globs['mapq'] = True;

	RC.startProg(globs);
	# After all the essential options have been set, call the welcome function.

	if args.quiet_flag:
		globs['stats'] = False;
		step_start_time = "";
	else:
		if globs['psutil']:
			import psutil
			globs['pids'] = [psutil.Process(os.getpid())];	
		globs['stats'] = True;
		step_start_time = RC.report_stats(globs, stat_start=True);
	# Initializing the stats options if --stats is set.
	# Parse performance options.

	file_paths, file_num = {}, 1;
	# Variables to store the file info.
	if args.input_list:
	# If the input method is -i
		if not os.path.isfile(args.input_list):
			RC.errorOut(7, "Cannot find file specified by -i.", globs);
		# Make sure we can find the input file.

		if not args.out_dest:
			globs['outdir'] = "referee-out-" + globs['startdatetime'] + RC.getRandStr();
		else:
			globs['outdir'] = args.out_dest;
		if not os.path.isdir(globs['outdir']):
			RC.printWrite(globs['logfilename'], globs['log-v'], "+ Making output directory: " + globs['outdir']);
			os.makedirs(globs['outdir']);
		# Specifiy and create the output directory, if necessary.

		if globs['stats']:
			step_start_time  = RC.report_stats(globs, "Reading input", step_start=step_start_time);
		else:
			print("# Reading input file paths...");
		for line in open(args.input_list):
			cur_gl_file = line.strip();
			if not cur_gl_file:
				continue;
			# Skip the line if its empty.

			if not os.path.isfile(cur_gl_file):
				RC.errorOut(8, "Invalid file path found in input file: " + cur_gl_file, globs);
			basename = os.path.splitext(os.path.basename(cur_gl_file));
			if basename[1] == '.gz':
				basename = os.path.splitext(basename[0])[0];
			else:
				basename = basename[0];

			cur_outfiletab = os.path.join(globs['outdir'], basename + "-out.txt");
			cur_outfiletmp = os.path.join(globs['outdir'], basename + "-" + globs['startdatetime'] + "-" + RC.getRandStr() + ".tmp");
			cur_outfilefq = os.path.join(globs['outdir'], basename + ".fq");

			# if not args.out_dest:
			# 	cur_outfiletab = os.path.join(globs['outdir'], os.path.splitext(cur_gl_file)[0] + "-referee-out.txt");
			# 	cur_outfiletmp = os.path.join(globs['outdir'], os.path.splitext(cur_gl_file)[0] + str(file_num) + "-referee-tmp-" + globs['startdatetime'] + ".tmp");
			# 	cur_outfilefq = os.path.join(globs['outdir'], os.path.splitext(cur_gl_file)[0] + "-referee-out.fq");
			# else:
			# 	cur_outfiletab = os.path.join(globs['outdir'], args.out_dest + "-" + str(file_num) + ".txt");
			# 	cur_outfiletmp = os.path.join(globs['outdir'], args.out_dest + "-" + str(file_num) + ".tmp");
			# 	cur_outfilefq = os.path.join(globs['outdir'], args.out_dest + "-" + str(file_num) + ".fq");				
			# Output file names.

			file_paths[file_num] = { 'in' : cur_gl_file, 'out' : cur_outfiletab, 'tmpfile' : cur_outfiletmp, 'outfq' : cur_outfilefq };
			file_num += 1;
		# Read the input file and get all the file paths. Also specify output file paths.

	else:
	# If the input method is -gl
		if not os.path.isfile(args.gl_file):
			RC.errorOut(9, "Cannot find genotype likelihood file specified by -gl.", globs);
		# Check if the genotype likelihood file is a valid file.

		if not args.out_dest:
			outfiletab = "referee-out-" + globs['startdatetime'] + RC.getRandStr() + ".txt";
			outfiletmp = "referee-tmp-" + globs['startdatetime'] + RC.getRandStr() + ".tmp";
			outfilefq = "referee-out-" + globs['startdatetime'] + RC.getRandStr() + ".fq";
		else:
			outfiletab = args.out_dest + ".txt";
			outfiletmp = args.out_dest + "-tmp-" + globs['startdatetime'] + "-" + RC.getRandStr() + ".tmp";
			outfilefq = args.out_dest + ".fq";
		# Specify the output files.

		file_paths[file_num] = { 'in' : args.gl_file, 'out' : outfiletab, 'tmpfile' : outfiletmp, 'outfq' : outfilefq };
	# Get the file paths for the current files.

	if globs['pileup'] and globs['mapq']:
		for file_num in file_paths:
			if not RC.mapQCheck(file_paths[file_num]['in']):
				RC.errorOut(10, "--mapq is set, but couldn't find mapping qualities on the first line of a file: " + file_paths[file_num]['in'], globs);

	return file_paths, globs, step_start_time;

#############################################################################

def multiSplit(files, globs):
# Given a file and a number of splits (in this case, the number of processors), this function splits
# the file into files with equal numbers of lines.
	import math

	file_info = files[1];
	#infilename, reffilename, outfilename, scaffs, globs = files[1];
	RC.printWrite(globs['logfilename'], globs['log-v'],"+ Making tmp directory: " + globs['tmpdir']);
	os.makedirs(globs['tmpdir']);
	# Make the temporary directory to store the split files and split outputs.

	new_files = {};
	# The dictionary for the new temporary files.

	tmpfiles = [os.path.join(globs['tmpdir'], str(i) + "-chunk.txt") for i in range(globs['num-procs'])];
	# Generate the names of the tmp input files.

	num_lines = RC.getFileLen(file_info['in']);
	linespersplit = int(math.ceil(num_lines / float(globs['num-procs'])));
	# Count the number of lines in the input file and get the number of lines per split.

	with RC.getFileReader(file_info['in'])(file_info['in'], "r") as infile:
		file_lines, file_num = 0, 0;
		tmpfile = open(tmpfiles[file_num], "w");
		for line in infile:
			tmpfile.write(line);
			file_lines += 1;
			if file_lines == linespersplit:
				tmpfile.close();
				newoutfile = os.path.join(globs['tmpdir'], str(file_num) + "-chunk-out.txt");
				new_files[file_num] = { 'in' : tmpfiles[file_num], 'out' : newoutfile };
				file_lines = 0;
				file_num += 1;
				if file_num != len(tmpfiles):
					tmpfile = open(tmpfiles[file_num], "w");
	# Read through every line in the input file and write it to one of the sub-files, updating the
	# subfile if we've reached the number of lines per split in that file.

	if len(new_files) != len(tmpfiles):
		tmpfile.close();
		newoutfile = os.path.join(globs['tmpdir'], str(file_num) + "-out.txt");
		new_files[file_num] = { 'in' : tmpfiles[file_num], 'out' : newoutfile };
	# If the last file has fewer lines than the rest it won't get added in the loop so we add it here.

	return new_files;

#############################################################################

def mergeFiles(outfile, files, globs):
# This function merges the tmp output files back into the main output file.
	import shutil
	with open(outfile, "w") as out:
		for file_num in sorted(files.keys()):
			with open(files[file_num]['out']) as infile:
				for line in infile:
					out.write(line);
	try:
		RC.printWrite(globs['logfilename'], globs['log-v'],"+ Removing tmp directory and files: " + globs['tmpdir']);
		shutil.rmtree(globs['tmpdir']);
	except:
		RC.printWrite(globs['logfilename'], globs['log-v'],"+ Could not remove tmp directory and files. User can remove manually: " + globs['tmpdir']);
	# Try to remove the tmp directory and files.

#############################################################################
