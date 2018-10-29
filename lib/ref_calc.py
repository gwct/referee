import math, re, refcore as RC, ref_out as OUT, sys
#############################################################################

def glInit(mapq):
# If the input is a pileup from which to calculate genotype likelihoods, this function
# precalculates the probabilities for each quality score (or combination of quality scores
# if mapping quality is provided).
    log_probs = {};
    for i in range(1,94):
        bq = unichr(i+33);
        bpe = 10.0 ** (-i/10.0);

        if mapq:
            for j in range(1,94):
                mq = unichr(j+33);
                mpe = 10.00 ** (-j/10.0);
                log_probs[bq+mq] = [0,0,0];
                match_p = (0.5 * (1-bpe)) * (0.5 * (1-mpe));
                mismatch_p = (0.5 * (bpe/3.0)) * (0.5 * (mpe/3.0));

                log_probs[bq+mq][0] = math.log(match_p + match_p);
                log_probs[bq+mq][1] = math.log(match_p + mismatch_p);
                log_probs[bq+mq][2] = math.log(mismatch_p + mismatch_p);

        else:
            log_probs[bq] = [0,0,0];

            match_p = (0.5 * (1-bpe));
            mismatch_p = (0.5 * (bpe/3.0));

            log_probs[bq][0] = math.log(match_p + match_p);
            log_probs[bq][1] = math.log(match_p + mismatch_p);
            log_probs[bq][2] = math.log(mismatch_p + mismatch_p);

    return log_probs;

#############################################################################

def calcScore(ref, gls, method):
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
            score, lr = 91, 0;
        # If the sum of the genotypes that don't match the called reference base is 0, assign maximum score.
        # This should scale with read depth somehow, though...
        elif l_match == 0:
            score, lr = -3, "NA";
        # If the sum of the genotyps that match the called reference base is 0, assign a score of -3. This should never happen.
        else:
            if method == 1:
                lr = l_match / l_mismatch;
                score = math.log(lr, 10);
            # Calculate the match : mismatch ratio and log transform.
            elif method == 2:
                lr = "NA";
                score = -1 * math.log(l_mismatch, 10);
            # Use the negative log of the sum of the mismatch likelihoods as the score.
            if score > 90:
                score = 90;
            if score < 0:
                score = 0;
            # Scale the scores so the max score is 91 and the all negative scores are 0.
    return score, lr, l_match, l_mismatch;
#############################################################################

def correctRef(max_score, ref, gls, method):
# If the score is negative, or the reference base is N, we can suggest a higher scoring
# base. This loops through all alternative bases, calculates the quality score, and
# returns the highest scoring one.
    max_base = ref;
    bases = "ATCG";
    for base in bases:
        if base == max_base:
            continue;
        score, lr, l_match, l_mismatch = calcScore(base, gls, method);
        if score > max_score:
            max_base, max_score = base, score;

    if max_base == ref:
        return "", "";
    else:
        return max_base, max_score;
#############################################################################

def glCalc(line, genotypes, log_probs, mapq):
    if not mapq:
        scaff, pos, ref, depth, reads, bqs = line;
        mqs = [unichr(1+33) for char in bqs];
    # If there are no mapping qualities, just assign dummy values of 1 for mapping probs for every read.
    elif mapq:
        scaff, pos, ref, depth, reads, bqs, mqs = line;
    # If there are mapping qualities, convert them to probabilities here.
    pos = int(pos);
    ref = ref.upper();
    while True:
        indel = re.search(r'[-+]\d+', reads)
        if indel == None:
            break;
        start, end = indel.span()
        reads = reads.replace(reads[start:end + int(reads[start+1:end])], "");
    # First, we use some regular expressions to remove the indel strings (ie +2AG, -3CAT)
    reads = re.sub("\^.", "", reads);
    reads = reads.replace("$","").upper();
    reads = list(re.sub("[,|.]", ref, reads));
    # Next we remove the symbols that indicate beginning (^) and end (&) of reads.
    # If it is the beginning of the read, we must also removing the following quality score symbol -- \w!\"#$%&'()*+,./:;<=>?@-
    # In regex, . matches ANY CHARACTER but \n
    # Then convert the . and , symbols to the actual base stored in ref

    log_gls = {};
    for gt in genotypes:
        log_gls[gt] = 0;
        for i in range(len(reads)):
            base = reads[i];
            qual_key = bqs[i];
            if mapq:
                qual_key += mqs[i];
            if base == "*" or '!' in qual_key:
                continue;
            # Skip the bad bases marked by pileup
            if gt[0] == gt[1] and base == gt[0]:
                log_gls[gt] += log_probs[qual_key][0];
            elif gt[0] != gt[1] and (base == gt[0] or base == gt[1]):
                log_gls[gt] += log_probs[qual_key][1];
            else:
                log_gls[gt] += log_probs[qual_key][2];
    # Calculate the genotype likelihood for every genotype given the current reads and probabilities.

    #log_gls_scaled = { gt : log_gls[gt] - max(log_gls.values()) for gt in log_gls };

    return ref, log_gls;#_scaled;
#############################################################################

def refCalc(file_item):
# Reads through a genotype likelihood file and calculates a quality scores for each line.
    file_num, file_info, globs = file_item;
    calc_rq_flag = True;

    last_scaff = "";
    with open(file_info['out'], "w") as outfile:
        for line in RC.getFileReader(file_info['in'])(file_info['in']):
            line = line.strip().split("\t");
            scaff, pos = line[0], int(line[1]);
            cor_ref, cor_score = "NA", "NA";

            if globs['pileup']:
            # If the input type is pileup, we calculate the genotype likelihoods here.
                if line[3] == "0":
                    ref, rq, lr, l_match, l_mismatch, log_gls = line[3].upper(), -2, "NA", "NA", "NA", "NA";
                    calc_rq_flag = False;
                # If no reads have mapped to the site, assign score -2 and skip everything else.
                else:
                    ref, log_gls = glCalc(line, globs['genotypes'], globs['probs'], globs['mapq']);
                # Otherwise call the genotype likelihood function.

            else:
            # If the input type is pre-calculated genotype likelihoods, just parse the line and pass it to calcScore.
                scaff, pos, gl_list = line[0], int(line[1]), line[2:];
                #gls = { globs['genotypes'][x] : math.exp(float(gl_list[x])) for x in range(len(gl_list)) };
                log_gls = { globs['genotypes'][x] : float(gl_list[x]) for x in range(len(gl_list)) };
                # Parse the info from the current line -- scaffold, position, genotype likelihoods.

                if last_scaff != scaff:
                    seq = RC.fastaGet(globs['reffile'], globs['ref'][scaff])[1];
                    last_scaff = scaff;
                ref = seq[pos-1].upper();
                # Gets the called reference base at the current position.

            if calc_rq_flag:
                gls = { gt : math.exp(log_gls[gt]) for gt in log_gls };

                rq, lr, l_match, l_mismatch = calcScore(ref, gls, globs['method']);
                # Call the scoring function.

                if globs['correct-opt'] and rq in [0,-1,-3]:
                    cor_ref, cor_score = correctRef(rq, ref, gls, globs['method']);
                # With --correct, suggest a better/corrected reference base if the score is negative (0), the reference is undetermined (-1), or no reads support the matching base (-3)

            outdict = { 'scaff' : scaff, 'pos' : pos, 'ref' : ref, 'rq' : rq, 'lr' : lr,  
                        'l_match' : l_match, 'l_mismatch' : l_mismatch, 'gls' : gls, 
                        'cor_ref' : cor_ref, 'cor_score' : cor_score };
            # Store the info from the current site to be written once returned.


            if globs['debug']:
                for gt in log_gls:
                   print gt, log_gls[gt];
                print rq, lr, l_match, l_mismatch;
            # Debug info
            
            OUT.outputTab(outdict, outfile, globs);
            # Writes the output to the current output file.

    return file_num;
#############################################################################