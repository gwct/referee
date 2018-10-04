#############################################################################
# INITIAL ATTEMPT TO PARALLELIZE BY SPITTING FILES INTO CHUNKS
# def multiPrep(files):
# 	import math

# 	file_info = files[1];
# 	globs = file_info['globs'];
# 	#infilename, reffilename, outfilename, scaffs, globs = files[1];
# 	RC.printWrite(globs['logfilename'], globs['log-v'],"+ Making tmp directory: " + globs['tmpdir']);
# 	os.system("mkdir " + globs['tmpdir']);
# 	# Make the temporary directory to store the split files and split outputs.

# 	if len(file_info['scaffs']) == 1:
# 		new_files = {};
# 		tmpfiles = [os.path.join(globs['tmpdir'], str(i) + ".txt") for i in range(globs['num-procs'])];
# 		num_pos = RC.getFileLen(file_info['in']);

# 		pospersplit = int(math.ceil(num_pos / float(globs['num-procs'])));
# 		with open(file_info['in'], "r") as infile:
# 			cur_scaffs = [];
# 			file_num, file_pos = 0, 0;
# 			tmpfile = open(tmpfiles[file_num], "w");
# 			for line in infile:
# 				tmpline = line.strip().split("\t");
# 				scaff, pos = tmpline[0], int(tmpline[1]);
# 				if scaff not in cur_scaffs:
# 					cur_scaffs.append(scaff);
# 				tmpfile.write(line);
# 				file_pos += 1;
# 				if file_pos >= pospersplit:
# 					tmpfile.close();
# 					newoutfile = os.path.join(globs['tmpdir'], str(file_num) + "-out.txt");
# 					new_files[file_num] = { 'in' : tmpfiles[file_num], 'ref' : file_info['ref'], 'out' : newoutfile, 
# 											'scaffs' : cur_scaffs, 'start' : False, 'stop' : False, 'globs' : globs };
# 					file_pos = 0;
# 					file_num += 1;
# 					if file_num != len(tmpfiles):
# 						tmpfile = open(tmpfiles[file_num], "w");

# 		if len(new_files) != len(tmpfiles):
# 			tmpfile.close();
# 			newoutfile = os.path.join(globs['tmpdir'], str(file_num) + "-out.txt");
# 			new_files[file_num] = { 'in' : tmpfiles[file_num], 'ref' : file_info['ref'], 'out' : newoutfile, 
# 									'scaffs' : cur_scaffs, 'start' : False, 'stop' : False, 'globs' : globs };

# 	else:
# 		new_files = {};
# 		tmpfiles = { scaff : os.path.join(globs['tmpdir'], scaff + ".txt") for scaff in file_info['scaffs'] };

# 		last_scaff = file_info['scaffs'][0];
# 		tmpfile = open(tmpfiles[last_scaff], "w");
# 		file_num = 1;
# 		with open(file_info['in'], "r") as infile:
# 			for line in infile:
# 				cur_scaff = line.split("\t")[0];
# 				if cur_scaff != last_scaff:
# 					tmpfile.close();
# 					newoutfile = os.path.join(globs['tmpdir'], last_scaff + "-out.txt");
# 					new_files[file_num] = { 'in' : tmpfiles[file_num], 'ref' : file_info['ref'], 'out' : newoutfile, 
# 											'scaffs' : cur_scaffs, 'start' : False, 'stop' : False, 'globs' : globs };					
# 					file_num += 1;
# 					tmpfile = open(tmpfiles[cur_scaff], "w");
# 				tmpfile.write(line);
# 				last_scaff = cur_scaff;

# 		tmpfile.close();
# 		newoutfile = os.path.join(globs['tmpdir'], last_scaff + "-out.txt");
# 		new_files[file_num] = { 'in' : tmpfiles[file_num], 'ref' : file_info['ref'], 'out' : newoutfile, 
# 								'scaffs' : cur_scaffs, 'start' : False, 'stop' : False, 'globs' : globs };

# 	return new_files;

#############################################################################
# IF I WANTED TO NUMBER THE STEPS
# def printStep(step, msg):
# # Prints a message and increments a counter.
# 	if globs.v not in [-2,-1]:
# 		print(msg);
# 	return step+1;

#############################################################################
# IF I NEEDED TO CHECK THE OS
# def osCheck(test_cmd):
# # For the tests script. Need to know if we are on Windows in order to pass the command correctly.
# 	import platform
# 	if platform.system == 'Windows':
# 		test_cmd = " ".join(test_cmd);
# 	return test_cmd;

#############################################################################
# A WAY TO GET A FASTA SEQUENCE BASED ON TITLE USING BIOPYTHON
# from Bio import SeqIO
# def getFastaInfo(ref_file, scaff_id):
# 	for record in SeqIO.parse(ref_file, "fasta"):
# 		if record.id == scaff_id:
# 			seq = record.seq;
# 			seqlen = len(record.seq);
# 			break;
# 	return seq, seqlen;

#############################################################################
# A WAY TO GET SEQUENCE LENGTHS USING BIOPYTHON
# def getScaffLens(ref_file):
# 	cur_lens = {};
# 	for record in SeqIO.parse(ref_file, "fasta"):
# 		cur_lens[record.id] = len(record.seq);
# 	return cur_lens;

#############################################################################
# A WAY TO GET ALL THE TITLES IN A FASTA FILE
# def getScaffs(i_name):
# 	scaffs = [];
# 	try:
# 		gzip_check = gzip.open(i_name).read(1);
# 		reader = gzip.open;
# 	except:
# 		reader = open;
# 	# Check if the genotype likelihood file is gzipped, and if so set gzip as the file reader. Otherwise, read as a normal text file.
# 	for line in reader(i_name):
# 		scaff = line.split("\t")[0];
# 		if scaff not in scaffs:
# 			scaffs.append(scaff);
# 	return scaffs;

#############################################################################
# GETS THE NUMBER OF LINES IN A FILE
# def getFileLen(i_name):
# 	num_lines = 0;
# 	for line in open(i_name).xreadlines(): num_lines += 1;
# 	return float(num_lines);

#############################################################################
# THE ORIGINAL SCORE CALCULATION FUNCTION WHEN I WAS PARALLELIZING BY CHUNKS
# def refCalc(file_item):
#     gl_file, ref_file, outfilename = file_item[1]['in'], file_item[1]['ref'], file_item[1]['out'];
#     scaffs, start, stop = file_item[1]['scaffs'], file_item[1]['start'], file_item[1]['stop'];
#     globs = file_item[1]['globs'];

#     genotypes = ["AA", "AC", "AG", "AT", "CC", "CG", "CT", "GG", "GT", "TT"]
#     last_scaff, cor_ref, cor_score, scaff_pos = "", "", "", 1;

#     if globs['fastq']:
#         fq_seq, fq_scores, fq_curlen, fq_lastpos = [], [], 0, 1;
#     # Variables for FASTQ output.

#     with open(outfilename, "w") as outfile:
#         try:
#             gzip_check = gzip.open(gl_file).read(1);
#             reader = gzip.open;
#         except:
#             reader = open;
#         # Check if the genotype likelihood file is gzipped, and if so set gzip as the file reader. Otherwise, read as a normal text file.

#         for line in reader(gl_file):
#             line = line.strip().split("\t");
#             scaff, pos, gl_list = line[0], int(line[1]), line[2:];

#             if start:
#                 start_scaff, start_pos = start;
#                 if start_scaff == scaff and pos < start_pos:
#                     continue;

#             if stop:
#                 stop_scaff, stop_pos = stop;

#             if scaff != last_scaff:
#                 seq, seqlen = RC.getFastaInfo(ref_file, scaff);
#             last_scaff = scaff;
#             # If the scaffold of the current line is different from the last scaffold, retrieve the sequence.

#             if not globs['mapped']:
#                 while scaff_pos != pos:
#                     scaff_ref = seq[scaff_pos-1];
#                     if globs['fastq']:
#                         fq_seq, fq_scores, fq_curlen, fq_lastpos = OUT.outputFastq(outfile, scaff, scaff_pos, scaff_ref, -2, fq_seq, fq_scores, fq_curlen, fq_lastpos, globs);
#                     else:
#                         OUT.outputTab(outfile, scaff, str(scaff_pos), scaff_ref, -2, "NA", "NA", "NA", "NA", globs, cor_base=cor_ref, cor_score=cor_score);
#                     scaff_pos += 1;

#                     if stop and stop_scaff == scaff and scaff_pos == stop_pos:
#                         break;
#             # If the current position has skipped ahead from where we are in the scaffold, that means there are
#             # intervening positions with no reads mapped. This fills in those scores as -2.

#             if stop and stop_scaff == scaff and scaff_pos == stop_pos:
#                 break;

#             gls = { genotypes[x] : math.exp(float(gl_list[x])) for x in range(len(gl_list)) };
#             # Parse the info from the current line -- scaffold, position, genotype likelihoods.

#             ref = seq[pos-1];
#             # Gets the called reference base at the current position.

#             rq, lr, l_match, l_mismatch = calcScore(ref, gls);
#             # Call the scoring function.

#             if globs['correct-opt']:
#                 cor_ref, cor_score = correctRef(rq, ref, gls);        

#             if globs['fastq']:
#                 fq_seq, fq_scores, fq_curlen, fq_lastpos = OUT.outputFastq(outfile, scaff, pos, ref, rq, fq_seq, fq_scores, fq_curlen, fq_lastpos, globs);
#             else:
#                 OUT.outputTab(outfile, scaff, str(pos), ref, rq, lr, l_match, l_mismatch, gls, globs, cor_base=cor_ref, cor_score=cor_score);
#             scaff_pos += 1;
#             # Write the score to the output file and iterate the scaff_pos.

#         if globs['fastq']:
#             fq_seq, fq_scores, fq_curlen, fq_lastpos = OUT.outputFastq(outfile, scaff, pos, ref, rq, fq_seq, fq_scores, fq_curlen, fq_lastpos, globs, final=True);

#############################################################################

# print pos, len(RC.fastaGet(globs['reffile'], globs['ref'][scaff])[1]), globs['reffile']
# print RC.fastaGet(globs['reffile'], globs['ref'][scaff])[1]
# print RC.fastaGet(globs['reffile'], globs['ref'][scaff])[1][pos-1];
# SOME LINES FOR CHECKING THE FASTA READER IN ref_calc BEFORE ASSIGNING ref.

# ref = ref_ind[scaff].seq[pos-1];
# READS THE ref IF USING BIOPYTHON.

#############################################################################
# THE PARALLELIZATION TEST SCRIPT

# import sys, os, multiprocessing as mp, lib.ref_calc as CALC, lib.ref_out as OUT

# def testFunc2(x):
#     return 3;

# def testFunc(it):
#     x, c = it;
#     y = testFunc2(x)
#     return {1 : x, 2 : c, 3 : y};

# def testPrint(x, c):
# 	print(x[1]);

# infilename = 'data/angsd-output-snippet.txt';
# #f = open(infilename, "r");
# #for line in f.iteritems():
# #    print line;

# if __name__ == '__main__':
#     procs = 4;
#     pool = mp.Pool(processes = procs);
#     #f = open(infilename, "r")
#     c = {1 : "A", 2 : "B", 3 : "C"}
#     with open(infilename, "r") as infile:
#         for outt in pool.map(CALC.testFunc, ((line, c) for line in infile)):
#             print outt;
#             OUT.testPrint(outt, c);
#             #print result;   

#############################################################################

