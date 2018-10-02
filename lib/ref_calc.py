import gzip, math, sys, refcore as RC
from Bio import SeqIO
#############################################################################
def calcScore(ref, gls):
    if ref.upper() in "NXB-":
        score, lr, l_match, l_mismatch = -1, "NA", "NA", "NA";
    # If the called base at this position is undefined, score it as -1, otherwise do the calculation.
    else:
        l_match, l_mismatch = 0, 0;
        for gt in gls:
            if ref in gt:
                l_match += gls[gt];
            else:
                l_mismatch += gls[gt];
        # Sum the genotypes that match the called reference base and those that don't (mismatch).

        if l_mismatch == 0:
            score, lr = 92, 0;
        # If the sum of the genotypes that don't match the called reference base is 0, assign maximum score.
        # This should scale with read depth somehow, though...
        elif l_match == 0:
            score, lr = -3, "NA";
        # If the sum of the genotyps that match the called reference base is 0, assign a score of -3. This should never happen.
        else:
            lr = l_match / l_mismatch;
            score = math.log(lr, 10);
            # Calculate the match : mismatch ratio and log transform.
            if score > 91:
                score = 91;
            if score < 0:
                score = 0;
            # Scale the scores so the max score is 91 and the all negative scores are 0.
    return score, lr, l_match, l_mismatch;
#############################################################################
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
def correctRef(max_score, ref, gls):
    max_base = ref;
    bases = "ATCG";
    for base in bases:
        if base == max_base:
            continue;
        score, lr, l_match, l_mismatch = calcScore(base, gls);
        if score > max_score:
            max_base, max_score = base, score;

    if max_base == ref:
        return "", "";
    else:
        return max_base, str(round(max_score));
#############################################################################

def refCalc2(line, globs):
    genotypes = ["AA", "AC", "AG", "AT", "CC", "CG", "CT", "GG", "GT", "TT"];

    line = line.strip().split("\t");
    scaff, pos, gl_list = line[0], int(line[1]), line[2:];

    cor_ref, cor_score = "NA", "NA";

    gls = { genotypes[x] : math.exp(float(gl_list[x])) for x in range(len(gl_list)) };
    # Parse the info from the current line -- scaffold, position, genotype likelihoods.

    ref = globs['ref'][scaff].seq[pos-1];
    # Gets the called reference base at the current position.

    rq, lr, l_match, l_mismatch = calcScore(ref, gls);
    # Call the scoring function.

    if globs['correct-opt']:
        cor_ref, cor_score = correctRef(rq, ref, gls); 

    outdict = { 'scaff' : scaff, 'pos' : pos, 'ref' : ref, 'rq' : rq, 'lr' : lr,  
                'l_match' : l_match, 'l_mismatch' : l_mismatch, 'gls' : gls, 
                'cor_ref' : cor_ref, 'cor_score' : cor_score };

    return outdict;

#############################################################################

def unmappedPos(cur_pos, stop_pos, scaff, seq):
    outinfo = [];
    while cur_pos <= stop_pos:
        cur_ref = seq[cur_pos-1];
        outinfo.append(scaff, cur_pos, cur_ref, -2, "NA", "NA", "NA", "NA", "NA", "NA");
    return outinfo;

#############################################################################