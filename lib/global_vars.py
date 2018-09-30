# This file holds some global variables for some of the input options.
# Global variables are exclusively read only.

import timeit, refcore as RC

def init():
# 	global spec_type;
# 	spec_type = "";

# 	global cap;
# 	cap = "";
	
# 	global lca_opt;
# 	lca_opt = "";

    global num_procs;
    num_procs = 1;

    global fastq;
    fastq = False;

    global fastq_lnlen;
    fastq_lnlen = 100;

    global correct_opt;
    correct_opt = False;

# 	global v;
# 	v = "";

    global log_v;
    log_v = 1;

# 	global pad;
# 	pad = 75;

# 	global label_opt;
# 	label_opt = "";

# 	global mul_opt;
# 	mul_opt = "";

# 	global check_nums;
# 	check_nums = "";

# 	global maps_opt;
# 	maps_opt = "";

# 	global orth_opt;
# 	orth_opt = "";

# 	global labeled_tree_file;
# 	labeled_tree_file = "";

# 	global orth_file_name;
# 	orth_file_name = "";

    global stats;
    stats = False;

    global startdatetime;
    startdatetime = RC.getOutTime();

    global logfilename;
    logfilename = "referee-" + startdatetime + ".log";

    global starttime;
    starttime = timeit.default_timer();

# 	global output_directory;
# 	output_directory = "";

# 	global detoutfilename;
# 	detoutfilename = "";

# 	global checkfilename;
# 	checkfilename = "";

# 	global gene_file_filtered;
# 	gene_file_filtered = "";

# 	global pickle_dir;
# 	pickle_dir = "";