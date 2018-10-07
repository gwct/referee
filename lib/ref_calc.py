import math, refcore as RC, ref_out as OUT
#############################################################################

def calcScore(ref, gls):
# Given a reference base and a set of genotype likelihoods, this function calculates a reference quality
# score by taking the ratio of the sum of genotypes containing the reference base to the sum of the 
# genotypes that don't contain the reference. Scores range from 0-91. Negative scores get score of 0.
# Scores for special cases:
# Reference base = N, X, or B: -1
# Sum of mismatch genotypes = 0: 92 (no support for any other base; need some way to scale with read depth)
# Sum of match genotypes = 0: -3 (this shouldn't happen ever)
# No reads mapped: -2 (this is handled in the fullUnmapped function in ref_out)
    if ref.upper() in "NXB":
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

def correctRef(max_score, ref, gls):
# If the score is negative, or the reference base is N, we can suggest a higher scoring
# base. This loops through all alternative bases, calculates the quality score, and
# returns the highest scoring one.
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
        return max_base, max_score;
#############################################################################

def refCalc(file_item):
# Reads through a genotype likelihood file and calculates a quality scores for each line.
    file_num, file_info, globs = file_item;
    genotypes = ["AA", "AC", "AG", "AT", "CC", "CG", "CT", "GG", "GT", "TT"];

    last_scaff = "";
    with open(file_info['out'], "w") as outfile:
        for line in RC.getFileReader(file_info['in'])(file_info['in']):
            line = line.strip().split("\t");
            scaff, pos, gl_list = line[0], int(line[1]), line[2:];

            cor_ref, cor_score = "NA", "NA";

            gls = { genotypes[x] : math.exp(float(gl_list[x])) for x in range(len(gl_list)) };
            # Parse the info from the current line -- scaffold, position, genotype likelihoods.

            if globs['fasta'] == 1:
                if last_scaff != scaff:
                    seq = RC.fastaGet(globs['reffile'], globs['ref'][scaff])[1];
                    last_scaff = scaff;
                ref = seq[pos-1];
            elif globs['fasta'] == 2:
                ref = globs['ref'][scaff][pos-1];
            elif globs['fasta'] == 3:
                ref = globs['ref'][scaff][pos-1];
            # Gets the called reference base at the current position.

            rq, lr, l_match, l_mismatch = calcScore(ref, gls);
            # Call the scoring function.

            if globs['correct-opt'] and rq in [0,-1,-3]:
                cor_ref, cor_score = correctRef(rq, ref, gls);
            # With --correct, suggest a better/corrected reference base if the score is negative (0), the reference is undetermined (-1), or no reads support the matching base (-3)

            outdict = { 'scaff' : scaff, 'pos' : pos, 'ref' : ref, 'rq' : rq, 'lr' : lr,  
                        'l_match' : l_match, 'l_mismatch' : l_mismatch, 'gls' : gls, 
                        'cor_ref' : cor_ref, 'cor_score' : cor_score };
            # Store the info from the current site to be written once returned.

            OUT.outputTab(outdict, outfile, globs);
            # Writes the output to the current output file.

    return file_num;

#############################################################################