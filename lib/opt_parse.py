import sys, os, lib.refcore as RC
#############################################################################

def optParse(globs):
# This function handles the command line options and prepares the output directory and files.
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
	parser.add_argument("-gl", dest="gl_file", help="The file containing the genotype likelihood calculations or a pileup file (be sure to set --pileup!).", default=False);
	#parser.add_argument("-i", dest="input_list", help="A file containing the paths to multiple input files containing genotype likelihoods and their reference FASTA files. Each line should contain one genotype likelihood file path or one pileup file path.", default=False);
	# Inputs
	parser.add_argument("-d", dest="outdir", help="An output directory for all files associated with this run. Will be created if it doesn't exist. Default: referee-[date]-[time]", default=False);
	parser.add_argument("-prefix", dest="prefix", help="A prefix for all files associated with this run. Default: referee-[date]-[time]", default=False);
	parser.add_argument("--overwrite", dest="overwrite", help="Set this option to explicitly overwrite files within a previous output directory.", action="store_true", default=False);
	# Output
	parser.add_argument("-p", dest="processes", help="The number of processes Referee should use. Default: 1.", default=False);
	parser.add_argument("-l", dest="lines_per_proc", help="The number of lines to be read per process. Decreasing may reduce memory usage at the cost of slightly higher run times. Default: 100000.", default=False);
	# User params
	parser.add_argument("--pileup", dest="pileup_flag", help="Set this option if your input file(s) are in pileup format and Referee will calculate genotype likelihoods for you.", action="store_true", default=False);
	parser.add_argument("--fastq", dest="fastq_flag", help="Set this option to output in FASTQ format in addition to the default tab delimited format.", action="store_true", default=False);
	parser.add_argument("--fasta", dest="fasta_flag", help="Set this option to output the corrected sequence in FASTA format in addition to the default tab delimited format. Can only be set with --corrected.", action="store_true", default=False);
	parser.add_argument("--bed", dest="bed_flag", help="Set this option to output in BED format in addition to the default tab delimited format. BED files can be viewed as tracks in genome browsers.", action="store_true", default=False);
	parser.add_argument("--haploid", dest="haploid_flag", help="Set this option if your input data are from a haploid species. Referee will limit its likelihood calculations to the four haploid genotypes. Can only be used with --pileup.", action="store_true", default=False);
	parser.add_argument("--correct", dest="correct_flag", help="Set this option to allow Referee to suggest alternate reference bases for sites that score 0.", action="store_true", default=False);
	parser.add_argument("--mapped", dest="mapped_flag", help="Set this to calculate scores only for positions that have reads mapped to them.", action="store_true", default=False);
	parser.add_argument("--mapq", dest="mapq_flag", help="Set with --pileup to indicate whether to consider mapping quality scores in the final score calculation. These should be in the seventh column of the pileup file.", action="store_true", default=False);
	parser.add_argument("--raw", dest="raw_flag", help="Set this flag to output the raw score as the fourth column in the tabbed output.", action="store_true", default=False);
	parser.add_argument("--quiet", dest="quiet_flag", help="Set this flag to prevent Referee from reporting detailed information about each step.", action="store_true", default=False);
	parser.add_argument("--version", dest="version_flag", help="Simply print the version and exit. Can also be called as '-version', '-v', or '--v'", action="store_true", default=False);
	# User options
	parser.add_argument("--norun", dest="norun", help=argparse.SUPPRESS, action="store_true", default=False);
	parser.add_argument("--allcalcs", dest="allcalc_opt", help=argparse.SUPPRESS, action="store_true", default=False);
	parser.add_argument("--debug", dest="debug_opt", help=argparse.SUPPRESS, action="store_true", default=False);
	parser.add_argument("--nolog", dest="nolog_opt", help=argparse.SUPPRESS, action="store_true", default=False);
	parser.add_argument("--scoreopt", dest="score_opt", help=argparse.SUPPRESS, type=int, default=1);
	# Performance tests

	args = parser.parse_args();
	# The input options and help messages

	if args.score_opt in [1,2]:
		globs['method'] = args.score_opt;
	else:
		RC.errorOut(0, "Invalid score method opt.", globs);
	if args.debug_opt:
		globs['debug'] = True;
	if args.nolog_opt:
		globs['log-v'] = -1;
	if args.norun:
		globs['norun'] = True;
	# Hidden test options

	if not args.gl_file or not os.path.isfile(args.gl_file):
		RC.errorOut("OP1", "Cannot find input file! A genotype likelihood or pileup file is required (-i).", globs);
	globs['in-file'] = args.gl_file
	# Check input file.

	if not args.ref_file or not os.path.isfile(args.ref_file):
		RC.errorOut("OP2", "Cannot find reference file! A genome file in FASTA format is required (-r).", globs);
	globs['ref-file'] = args.ref_file;
	# Check reference genome fasta file.

	globs['num-procs'] = RC.isPosInt(args.processes);
	if not globs['num-procs']:
		RC.errorOut("OP3", "-p must be an integer value greater than 1.", globs);
	# Checking the number of processors option.

	if args.lines_per_proc:
		globs['lines-per-proc'] = RC.isPosInt(args.lines_per_proc);
		if not globs['lines-per-proc']:
			RC.errorOut("OP4", "-l must be an integer value greater than 1.", globs);
	globs['chunk-size'] = globs['num-procs'] * globs['lines-per-proc'];
	# Checking the lines per proc option and then setting the chunk size based on that and the number of procs.

	if args.fastq_flag:
		globs['fastq-opt'] = True;
	# Checking the fastq option.

	if args.bed_flag:
		globs['bed-opt'] = True;
	# Checking the BED option.

	if args.mapped_flag:
		if args.fastq_flag or args.bed_flag:
			RC.errorOut("OP5", "Cannot output to --fastq or --bed when only doing --mapped positions. Pick one.", globs);
			# Raise error if both --fastq or --bed and --mapped are selected. FASTQ output without all positions would be confusing.
		else:
			globs['mapped-only-opt'] = True;
	# Checking the mapped option.

	if args.haploid_flag:
		if not args.pileup_flag:
			RC.errorOut("OP6", "Please provide a --pileup file for internal genotype likelihood calculations when input data is --haploid.", globs);
			# Raise error if haploid is set without pileup input.
		globs['haploid-opt'] = True;
		globs['genotypes'] = globs['haploid-gt'];
	# Checking the haploid option.

	if args.correct_flag:
		globs['correct-opt'] = True;
	# Checking the correct option.

	if args.fasta_flag:
		if not globs['correct-opt']:
			RC.errorOut("OP7", "--correct must be set to generate --fasta output, otherwise it's just a copy of the input file.", globs);
		globs['fasta-opt'] = True;
	# Checking the correct option.

	if args.raw_flag:
		globs['raw-opt'] = True;
	# Checking the raw score option.

	if args.allcalc_opt:
		globs['allcalc-opt'] = True;
		#globs['fastq-opt'] = False;
	# Allcalc option (hidden)

	if args.pileup_flag:
		globs['pileup-opt'] = True;
		if args.mapq_flag:
			globs['mapq-opt'] = True;
	# Pileup option

	if not args.prefix:
		globs['out-prefix'] = "referee-" + globs['startdatetime'];
	else:
		globs['out-prefix'] = args.prefix;
	# Get the output prefix
	
	if not args.outdir:
		args.outdir = globs['out-prefix'];

	if not os.path.isdir(args.outdir):
		os.system("mkdir " + args.outdir);
	elif os.path.isdir(args.outdir) and not args.overwrite:
		RC.errorOut("OP7", "Output directory already exists. Please specify --overwrite if you wish to overwrite the previous referee files within.", globs);
	globs['out-dir'] = args.outdir;
	# Output directory

	globs['out-tab'] = os.path.join(globs['out-dir'], globs['out-prefix'] + ".tab");
	globs['out-summary'] = os.path.join(globs['out-dir'], globs['out-prefix'] + "-summary.txt");
	if globs['fastq-opt']:
		globs['out-fq']  = os.path.join(globs['out-dir'], globs['out-prefix'] + ".fq");
	if globs['fasta-opt']:
		globs['out-fa']  = os.path.join(globs['out-dir'], globs['out-prefix'] + "-corrected.fa");
	if globs['bed-opt']:
		globs['bed-dir'] = os.path.join(globs['out-dir'], globs['out-prefix'] + "-bed");
		if not os.path.isdir(globs['bed-dir']):
			os.system("mkdir " + globs['bed-dir']);
	#globs['out'] = "referee-out-[start datetime]-[random string]";
	# Output files

	globs['logfilename'] = os.path.join(globs['out-dir'], globs['out-prefix'] + ".log");
	globs['endprog'] = True;
	# Log file

	ref_index = args.ref_file + ".fai"
	if os.path.isfile(ref_index):
		globs['ref-index'] = ref_index;
	# Check if there is an index for the reference FASTA file, which makes getting the scaffold lengths much quicker in some cases.

	if args.quiet_flag:
		globs['quiet'] = True;
		globs['log-v'] = 3;
	# Set the verbosity if the --quiet option is specified.

	if globs['pileup-opt'] and globs['mapq-opt']:
		if not RC.mapQCheck(globs['in-file']):
			RC.errorOut("OP8", "--mapq is set, but couldn't find mapping qualities on the first line of the input file: " + globs['infile'], globs);
	# Make sure the pileup file input has a mapping quality column if --mapq is specified as well.

	if globs['psutil']:
		globs['pids'] = [psutil.Process(os.getpid())];
	# Get the starting process ids to calculat memory usage throughout.

	startProg(globs);
	# After all the essential options have been set, call the welcome function.

	return globs;

#############################################################################


def startProg(globs):
# A nice way to start the program.
	start_v = 1;

	print("#");
	RC.printWrite(globs['logfilename'], 0, "# Welcome to Referee -- Reference genome quality score calculator.");
	RC.printWrite(globs['logfilename'], start_v, "# Version " + globs['version'] + " released on " + globs['releasedate']);
	RC.printWrite(globs['logfilename'], start_v, "# Referee was developed by Gregg Thomas and Matthew Hahn");
	RC.printWrite(globs['logfilename'], start_v, "# Citation:      " + globs['doi']);
	RC.printWrite(globs['logfilename'], start_v, "# Website:       " + globs['http']);
	RC.printWrite(globs['logfilename'], start_v, "# Report issues: " + globs['github']);
	RC.printWrite(globs['logfilename'], start_v, "#");
	RC.printWrite(globs['logfilename'], start_v, "# The date and time at the start is: " + RC.getDateTime());
	RC.printWrite(globs['logfilename'], start_v, "# Using Python version:              " + globs['pyver'] + "\n#");
	RC.printWrite(globs['logfilename'], start_v, "# The program was called as: " + " ".join(sys.argv) + "\n#");

	pad = 20;
	RC.printWrite(globs['logfilename'], start_v, "# " + "-" * 125);
	RC.printWrite(globs['logfilename'], start_v, "# INPUT/OUTPUT INFO");
	RC.printWrite(globs['logfilename'], start_v, RC.spacedOut("# Input file:", pad) + globs['in-file']);
	RC.printWrite(globs['logfilename'], start_v, RC.spacedOut("# Reference file:", pad) + globs['ref-file']);
	RC.printWrite(globs['logfilename'], start_v, RC.spacedOut("# Output directory:", pad) + globs['out-dir']);
	RC.printWrite(globs['logfilename'], start_v, RC.spacedOut("# Output prefix:", pad) + globs['out-prefix']);

	RC.printWrite(globs['logfilename'], start_v, "# " + "-" * 125);
	RC.printWrite(globs['logfilename'], start_v, "# OPTIONS INFO");	
	RC.printWrite(globs['logfilename'], start_v, RC.spacedOut("# Option", pad) + RC.spacedOut("Current setting", pad) + "Current action");
	RC.printWrite(globs['logfilename'], start_v, "# " + "-" * 125);

	if globs['pileup-opt']:
		RC.printWrite(globs['logfilename'], start_v, RC.spacedOut("# --pileup", pad) + 
					RC.spacedOut("True", pad) + 
					"Input type set to pileup. Referee will calculate genotype likelihoods.");
		if globs['mapq-opt']:
			RC.printWrite(globs['logfilename'], start_v, RC.spacedOut("# --mapq", pad) + 
						RC.spacedOut("True", pad) + 
						"Incorporating mapping qualities (7th column of pileup file) into quality score calculations if they are present.");
		else:
			RC.printWrite(globs['logfilename'], start_v, RC.spacedOut("# --mapq", pad) + 
						RC.spacedOut("False", pad) + 
						"Ignoring mapping qualities in pileup file if they are present.");
	else:
		RC.printWrite(globs['logfilename'], start_v, RC.spacedOut("# --pileup", pad) + 
					RC.spacedOut("False", pad) + 
					"Input is pre-calculated genotype log likelihoods.");
		if globs['mapq-opt']:
			RC.printWrite(globs['logfilename'], start_v, RC.spacedOut("# --mapq", pad) + 
						RC.spacedOut("True", pad) +  
						"--pileup not set. Ignoring --mapq option.");
	# Reporting the pileup option.

	if globs['fastq-opt']:
		RC.printWrite(globs['logfilename'], start_v, RC.spacedOut("# --fastq", pad) + 
					RC.spacedOut("True", pad) + 
					"Writing output in FASTQ format in addition to tab delimited: " + globs['out-fq']);
	else:
		RC.printWrite(globs['logfilename'], start_v, RC.spacedOut("# --fastq", pad) + 
					RC.spacedOut("False", pad) + 
					"Not writing output in FASTQ format.");
	# Reporting the fastq option.

	if globs['fasta-opt']:
		RC.printWrite(globs['logfilename'], start_v, RC.spacedOut("# --fasta", pad) + 
					RC.spacedOut("True", pad) + 
					"Writing corrected output in FASTA format in addition to tab delimited: " + globs['out-fq']);
	else:
		RC.printWrite(globs['logfilename'], start_v, RC.spacedOut("# --fasta", pad) + 
					RC.spacedOut("False", pad) + 
					"Not writing corrected output in FASTA format.");
	# Reporting the fastq option.

	if globs['bed-opt']:
		RC.printWrite(globs['logfilename'], start_v, RC.spacedOut("# --bed", pad) + 
					RC.spacedOut("True", pad) + 
					"Writing output in BED format in addition to tab delimited: " + globs['bed-dir']);
		# Specifiy and create the BED directory, if necessary.
	else:
		RC.printWrite(globs['logfilename'], start_v, RC.spacedOut("# --bed", pad) + 
					RC.spacedOut("False", pad) + 
					"Not writing output in BED format.");
	# Reporting the fastq option.

	if globs['mapped-only-opt']:
		RC.printWrite(globs['logfilename'], start_v, RC.spacedOut("# --mapped", pad) + 
					RC.spacedOut("True", pad) + 
					"Only calculating scores for positions with reads mapped to them.");
	else:
		RC.printWrite(globs['logfilename'], start_v, RC.spacedOut("# --mapped", pad) + 
					RC.spacedOut("False", pad) + 
					"Calculating scores for every position in the reference genome.");
	# Reporting the mapped option.

	if globs['haploid-opt']:
		RC.printWrite(globs['logfilename'], start_v, RC.spacedOut("# --haploid", pad) + 
					RC.spacedOut("True", pad) + 
					"Calculating genotype likelihoods and quality scores for HAPLOID data (4 genotypes).");
	else:
		RC.printWrite(globs['logfilename'], start_v, RC.spacedOut("# --haploid", pad) + 
					RC.spacedOut("False", pad) + 
					"Calculating genotype likelihoods and quality scores for DIPLOID data (10 genotypes).");
	# Reporting the haploid option.

	if globs['raw-opt']:
		RC.printWrite(globs['logfilename'], start_v, RC.spacedOut("# --raw", pad) + 
					RC.spacedOut("True", pad) + 
					"Printing raw Referee score in fourth column of tabbed output.");
	else:
		RC.printWrite(globs['logfilename'], start_v, RC.spacedOut("# --raw", pad) + 
					RC.spacedOut("False", pad) + 
					"NOT printing raw Referee score in tabbed output.");
	# Reporting the correct option.		

	if globs['correct-opt']:
		RC.printWrite(globs['logfilename'], start_v, RC.spacedOut("# --correct", pad) + 
					RC.spacedOut("True", pad) + 
					"Suggesting higher scoring alternative base when reference score is negative or reference base is N.");
	else:
		RC.printWrite(globs['logfilename'], start_v, RC.spacedOut("# --correct", pad) + 
					RC.spacedOut("False", pad) + 
					"Not suggesting higher scoring alternative base when reference score is negative or reference base is N.");
	# Reporting the correct option.

	if not globs['quiet']:
		RC.printWrite(globs['logfilename'], start_v, RC.spacedOut("# --quiet", pad) + 
					RC.spacedOut("False", pad) + 
					"Step info will be output while Referee is running.");
	else:
		RC.printWrite(globs['logfilename'], start_v, RC.spacedOut("# --quiet", pad) + 
					RC.spacedOut("True", pad) + 
					"No further information will be output while Referee is running.");
	# Reporting the correct option.

	RC.printWrite(globs['logfilename'], start_v, RC.spacedOut("# -p", pad) + 
				RC.spacedOut(str(globs['num-procs']), pad) + 
				"Referee will use this many processes to run.");
	# Reporting the number of processes specified.

	RC.printWrite(globs['logfilename'], start_v, RC.spacedOut("# -l", pad) + 
			RC.spacedOut(str(globs['lines-per-proc']), pad) + 
			"This many lines will be read per process to be calculated at one time in parallel");
	# Reporting the lines per proc option.

	if globs['allcalc-opt']:
		RC.printWrite(globs['logfilename'], start_v, RC.spacedOut("# --allcalcs", pad) + 
					RC.spacedOut("True", pad) + 
					"Using tab delimited output and reporting extra columns.");
	# Reporting the allcalc option.

	if globs['debug']:
		RC.printWrite(globs['logfilename'], start_v, RC.spacedOut("# --debug", pad) + 
					RC.spacedOut("True", pad) + 
					"Printing out a bit of debug info.");
	# Reporting the allcalc option.

	if not globs['pileup-opt']:
		RC.printWrite(globs['logfilename'], start_v, "#\n# " + "-" * 40);
		RC.printWrite(globs['logfilename'], start_v, "## IMPORTANT!");
		RC.printWrite(globs['logfilename'], start_v, "## Input columns: Scaffold\tPosition\tAA\tAC\tAG\tAT\tCC\tCG\tCT\tGG\tGT\tTT");
		RC.printWrite(globs['logfilename'], start_v, "## Please ensure that your input genotype likelihood files are tab delimited with columns in this exact order without headers.");
		RC.printWrite(globs['logfilename'], start_v, "## Failure to do so will result in inaccurate calculations!!");
		RC.printWrite(globs['logfilename'], start_v, "# " + "-" * 40 + "\n#");
	
	if globs['quiet']:
		RC.printWrite(globs['logfilename'], start_v, "# " + "-" * 125);
		RC.printWrite(globs['logfilename'], start_v, "# Running...");

#############################################################################

