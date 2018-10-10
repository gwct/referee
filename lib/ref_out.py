import refcore as RC
#############################################################################

def outputFastq(outdict, fq_vars, globs, final=False):
# For output to FASTQ format.
    if not final:
        fq_vars["fq_seq"] += outdict['ref'];
        score = str(unichr(int(round(outdict['rq'])+35)));
        fq_vars["fq_scores"] += score;
    # Adds the current base and ascii score to the corresponding lists.

    if len(fq_vars["fq_seq"]) == globs['fastq-len'] or final:
        cur_title = "@" + outdict['scaff'] + " " + str(outdict["pos"]-int(len(fq_vars["fq_seq"]))+1) + ":" + str(outdict["pos"]) + " length=" + str(len(fq_vars["fq_seq"]));
        # Set the current FASTQ title.

        fq_vars["fqoutfile"].write(cur_title + "\n");
        fq_vars["fqoutfile"].write(fq_vars["fq_seq"] + "\n");
        fq_vars["fqoutfile"].write("+\n");
        fq_vars["fqoutfile"].write(fq_vars["fq_scores"] + "\n");
        # Write the title, sequence, and scores.

        fq_vars['fq_seq'], fq_vars['fq_scores'] = "", "";
        # Reset the sequence and score strings.
    # This writes the sequence and scores if the length of the sequence matches the max fastq line length (global) or if its the final line.

    return fq_vars;
#############################################################################

def outputTab(outdict, outfile, globs):
# For output to tab delimited format.
    outline = [outdict['scaff'], str(outdict['pos']), str(int(round(outdict['rq'])))];
    # Set-up the basic output: scaffold, position, and score.

    if globs['allcalc']:
        if outdict['rq'] != -2:
            max_gt, max_gl = "", -9999;
            for gt in outdict['gls']:
                if outdict['gls'][gt] > max_gl:
                    max_gt = gt;
                    max_gl = outdict['gls'][gt];
        outline += [str(outdict['lr']), str(outdict['l_match']), str(outdict['l_mismatch']), str(outdict['ref']), max_gt, str(max_gl)];
    # Add the extra columns if --allcalcs.

    if globs['correct-opt']:
        try:
            cor_score = str(int(round(outdict['cor_score'])));
            cor_base = outdict['cor_ref']
        except:
            cor_score, cor_base = "", "";
        outline += [cor_base, cor_score]
    # See if this position has a corrected score if --correct is specified.

    outfile.write("\t".join(outline) + "\n");
    # Write the line.
#############################################################################

def addUnmapped(file_info, globs):
# Since we need to have a score for every position in the reference genome and some of those positions are unmapped,
# this function goes through the positions in the output file and adds the unmapped positions.

    scaff_pos, last_scaff, first = 1, "", True;
    # scaff_pos keeps track of the last position we've filled in. Comparing it to the current position in the output file
    # or the length of the current scaffold allows us to fill in the missing sites.

    with open(file_info['tmpfile'], "w") as tmpoutfile:
        fq_vars = {};
        if globs['fastq']:
            fqoutfile = open(file_info['outfq'], "w");
            fq_vars = { "fqoutfile" : fqoutfile, "fq_seq" : "", "fq_scores" : "", "filled" : False }
        # Variables for FASTQ output.

        for line in open(file_info['out']):
            linelist = line.strip().split("\t");
            scaff, pos = linelist[0], int(linelist[1]);
            if scaff not in file_info['scaffs']:
                continue;
            if scaff != last_scaff:
                if first:
                    first = False
                else:
                    scaff_pos, fq_vars = fillUnmapped(scaff_pos, seqlen, last_scaff, seq, tmpoutfile, globs, fq_vars);
                # If this is not the first scaffold, fill in all positions from the last position on the last scaffold.
                # until the end of that scaffold.

                if globs['fasta'] == 1:
                    seq = RC.fastaGet(globs['reffile'], globs['ref'][scaff])[1];
                elif globs['fasta'] == 2:
                    seq = globs['ref'][scaff];
                elif globs['fasta'] == 3:
                    seq = globs['ref'][scaff];

                seqlen = len(seq);
                scaff_pos = 1;
                last_scaff = scaff;
                # When the scaffold changes, get the new seq, seqlen, last_scaff, and reset scaff_pos to 1.

            scaff_pos, fq_vars = fillUnmapped(scaff_pos, pos-1, scaff, seq, tmpoutfile, globs, fq_vars);
            # If the current scaff_pos is below the pos in the output file, we need to fill in the unmapped positions
            # up to that position.

            if globs['fastq']:
                fqoutdict = { 'scaff' : scaff, 'pos' : pos, 'ref' : seq[pos-1], 'rq' : int(line.strip().split("\t")[2]) };
                fq_vars = outputFastq(fqoutdict, fq_vars, globs);
            # Output the current position to FASTQ.

            tmpoutfile.write(line);
            scaff_pos += 2; 
            # Simply re-write the line to the tmp file and iterate the scaff_pos.
            # Since the pass to fillUnmapped passed the INDEX (pos-1), I need to add one to get it back into POSITION. Then I need to
            # add one more to go to the next position... hence += 2.

        scaff_pos, fq_vars = fillUnmapped(scaff_pos, seqlen, last_scaff, seq, tmpoutfile, globs, fq_vars, final=True);
        # After the last line of the output file, fill in the rest of the positions for that scaffold.
        if globs['fastq']:
            if not fq_vars['filled'] and fq_vars['fq_seq'] != "":
                fq_vars = outputFastq(fqoutdict, fq_vars, globs, final=True);
            fqoutfile.close();
        # Write the final FASTQ line if the last position was mapped and had a score and close the FASTQ output file.

#############################################################################

def fillUnmapped(start, stop, scaff, seq, outfile, globs, fq_vars, final=False, first=True):
# Given a start and stop position, this function fills in the scores for unmapped positions
# up to the stop position. The score for unmapped positions is -2.

    while start <= stop:
        if final and first:
            first, fq_vars['filled'] = False, True;
        # If its the last call, we need to know if the last position is unmapped for FASTQ output.
        # If it is, then we call the final FASTQ output here. If not, then we call it back in addUnmapped
        # with the last scored base.

        outdict = { 'scaff' : scaff, 'pos' : start, 'ref' : seq[start-1], 
                    'rq' : -2, 'lr' : "NA", 'l_match' : "NA", 'l_mismatch' : "NA", 
                    'gls' : "NA", 'cor_ref' : "NA", 'cor_score' : "NA" };
        # Format the output info for an unmapped position.
        
        outputTab(outdict, outfile,  globs);
        # Output to tab file.

        if globs['fastq']:
            fq_vars = outputFastq(outdict, fq_vars, globs);
        # Output to Fastq file.

        start += 1;

    if final and fq_vars['filled'] and globs['fastq'] and fq_vars['fq_seq'] != "":
        fq_vars = outputFastq(outdict, fq_vars, globs, final=True);
    # If this is the final call and the last position was unmapped, we call the final FASTQ output here.

    return stop, fq_vars;

#############################################################################
