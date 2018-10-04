import sys, os, refcore as RC
#############################################################################

def optParse(globs):
# This function handles the command line options and prepares the output directory and files.
	try:
		import argparse;
	except:
		sys.exit("\n*** ERROR: Your installation of Python is missing the argparse module. Please try a different version of Python (2.7 or later) or install the module.\n")
	# First check if the argparse module is installed. If not, the input options cannot be parsed.

	parser = argparse.ArgumentParser(description="Referee: Reference genome quality scoring.");

	parser.add_argument("-ref", dest="ref_file", help="The FASTA assembly to which you have mapped your reads.", default=False);
	parser.add_argument("-gl", dest="gl_file", help="The file containing the genotype likelihood calculations.", default=False);
	parser.add_argument("-i", dest="input_list", help="A file containing the paths to multiple input files containing genotype likelihoods and their reference FASTA files. Each line should contain one genotype likelihood file path and one FASTA file path separated by a tab.", default=False);
	# Inputs
	parser.add_argument("-o", dest="out_dest", help="A PREFIX name for the output files/directories. Default: referee-out-[date]-[time]", default=False);
	# Output
	parser.add_argument("--fastq", dest="fastq_flag", help="Set this option to output in FASTQ format instead of the default tab delimited format.", action="store_true", default=False);
	parser.add_argument("--correct", dest="correct_flag", help="Set this option to allow Referee to suggest alternate reference bases for sites that score below a cut-off set by -c.", action="store_true", default=False);
	parser.add_argument("--mapped", dest="mapped_flag", help="Set this to calculate scores only for positions that have reads mapped to them.", action="store_true", default=False);
	# User options	
	#parser.add_argument("-s", dest="startpos", help="Set the starting position for the input file(s). Default: 1", default=False);
	#parser.add_argument("-e", dest="endpos", help="Set the end position for the input file(s). Default: last position in assembly/scaffold", default=False);
	#parser.add_argument("-c", dest="score_cutoff", help="The cut-off score for --correct. Sites that score below this cut-off will have an alternate reference base suggested. If --correct isn't set, this option is ignored. Default: 1", default=False);
	parser.add_argument("-p", dest="processes", help="The number of processes Referee should use. Not that 1 process is always reserved for the main script, so to see any benefit you must enter 3 or above. Default: 1.", default=False);
	# User params
	parser.add_argument("--stats", dest="stats_opt", help=argparse.SUPPRESS, action="store_true", default=False);
	parser.add_argument("--allcalcs", dest="allcalc_opt", help=argparse.SUPPRESS, action="store_true", default=False);
	# Performance tests

	args = parser.parse_args();
	# The input options and help messages

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

	if args.mapped_flag and args.fastq_flag:
		RC.errorOut(5, "Cannot output to --fastq when only doing --mapped positions. Pick one.", globs);
	# Raise error if both --fastq and --mapped are selected. FASTQ output without all positions would be confusing.

	if args.processes and not args.processes.isdigit():
		RC.errorOut(6, "-p must be an integer value greater than 1.", globs);
	elif args.processes:
		globs['num-procs'] = int(args.processes);
	# Checking the number of processors option.

	if args.fastq_flag:
		globs['fastq'] = True;
		RC.printWrite(globs['logfilename'], globs['log-v'], "# --fastq : Output format is FASTQ.");
	else:
		RC.printWrite(globs['logfilename'], globs['log-v'], "# Output format is tab delimited.");
	# Checking the fastq option.

	if args.mapped_flag:
		globs['mapped'] = True;
		RC.printWrite(globs['logfilename'], globs['log-v'], "# --mapped : Only calculating scores for positions with reads mapped to them.");
	else:
		RC.printWrite(globs['logfilename'], globs['log-v'], "# Calculating scores for every reference position specified.");
	# Checking the mapped option.

	if args.correct_flag:
		globs['correct-opt'] = True;
		RC.printWrite(globs['logfilename'], globs['log-v'], "# --correct : Suggesting higher scoring alternative base when reference score is negative or reference base is N.");
	# Checking the correct option.

	if args.stats_opt:
		import psutil
		globs['stats'] = True;
		globs['pids'] = [psutil.Process(os.getpid())];		
		step_start_time = RC.report_stats(globs, stat_start=True);
	# Initializing the stats options if --stats is set.

	if args.allcalc_opt:
		RC.printWrite(globs['logfilename'], globs['log-v'], "# --allcalcs : Using tab delimited output and reporting extra columns.");
		globs['allcalc'] = True;
		globs['fastq'] = False;
	# Parse performance options.

	file_paths, file_num = {}, 1;
	# Variables to store the file info.
	if args.input_list:
	# If the input method is -i
		if not os.path.isfile(args.input_list):
			RC.errorOut(7, "Cannot find file specified by -i.", globs);
		# Make sure we can find the input file.

		if not args.out_dest:
			globs['outdir'] = "referee-out-" + globs['startdatetime'];
		else:
			globs['outdir'] = args.out_dest;
		if not os.path.isdir(globs['outdir']):
			RC.printWrite(globs['logfilename'], globs['log-v'], "+ Making output directory: " + globs['outdir']);
			#os.system("mkdir \"" + globs['outdir'] + "\"");
			os.makedirs(globs['outdir']);
		# Specifiy and create the output directory, if necessary.

		for line in open(args.input_list):
			cur_gl_file = line.strip();
			if not cur_gl_file:
				continue;
			# Skip the line if its empty.

			if not os.path.isfile(cur_gl_file):
				RC.errorOut(8, "Invalid file path found in input file: " + cur_gl_file, globs);
			if not args.out_dest:
				cur_outfiletab = os.path.join(globs['outdir'], os.path.splitext(cur_gl_file)[0] + "-referee-out.txt");
				cur_outfiletmp = os.path.join(globs['outdir'], os.path.splitext(cur_gl_file)[0] + str(file_num) + "-referee-tmp-" + globs['startdatetime'] + ".tmp");
				cur_outfilefq = os.path.join(globs['outdir'], os.path.splitext(cur_gl_file)[0] + "-referee-out.fq");
			else:
				cur_outfiletab = os.path.join(globs['outdir'], args.out_dest + "-" + str(file_num) + ".txt");
				cur_outfiletmp = os.path.join(globs['outdir'], args.out_dest + "-" + str(file_num) + ".tmp");
				cur_outfilefq = os.path.join(globs['outdir'], args.out_dest + "-" + str(file_num) + ".fq");				
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
			outfiletab = "referee-out-" + globs['startdatetime'] + ".txt";
			outfiletmp = "referee-tmp-" + globs['startdatetime'] + ".tmp";
			outfilefq = "referee-out-" + globs['startdatetime'] + ".fq";
		else:
			outfiletab = args.out_dest + ".txt";
			outfiletmp = args.out_dest + "-tmp-" + globs['startdatetime'] + ".tmp";
			outfilefq = args.out_dest + ".fq";
		# Specify the output files.

		file_paths[file_num] = { 'in' : args.gl_file, 'out' : outfiletab, 'tmpfile' : outfiletmp, 'outfq' : outfilefq };
	# Get the file paths for the current files.

	return file_paths, globs, step_start_time ;

#############################################################################