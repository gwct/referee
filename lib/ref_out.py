import refcore as RC
#############################################################################

def outputFastq(outdict, fq_vars, globs, final=False):
    fq_vars["fq_seq"].append(outdict['ref']);
    score = str(unichr(int(round(outdict['rq'])+35)));
    print outdict['scaff'], outdict['pos'], outdict['rq'], score;
    fq_vars["fq_scores"].append(score);
    fq_vars["fq_curlen"] += 1;
    #print fq_curlen, globs['fastq-len'];    

    if fq_vars["fq_curlen"] == globs['fastq-len'] or final:
        if final:
            cur_title = "@" + outdict['scaff'] + " " + str(fq_vars["fq_lastpos"]) + ":" + str(fq_vars["fq_lastpos"]+int(outdict['pos'])-1) + " length=" + str(-1 * (fq_vars["fq_lastpos"]-int(outdict['pos'])-1));
        else:
            cur_title = "@" + outdict['scaff'] + " " + str(fq_vars["fq_lastpos"]) + ":" + str(fq_vars["fq_lastpos"]+int(outdict['pos'])) + " length=" + str(globs['fastq-len']);

        fq_vars["fqoutfile"].write(cur_title + "\n");
        fq_vars["fqoutfile"].write("".join(fq_vars["fq_seq"]) + "\n");
        fq_vars["fqoutfile"].write("+\n");
        fq_vars["fqoutfile"].write("".join(fq_vars["fq_scores"]) + "\n");
        fq_vars["fq_lastpos"] = outdict['pos'];
    return fq_vars;
#############################################################################

def outputTab(outdict, outfile, globs):
    outline = [outdict['scaff'], str(outdict['pos']), str(int(round(outdict['rq'])))];

    if globs['debug']:
        if outdict['rq'] != -2:
            max_gt, max_gl = "", -9999;
            for gt in outdict['gls']:
                if outdict['gls'][gt] > max_gl:
                    max_gt = gt;
                    max_gl = outdict['gls'][gt];
        outline += [str(outdict['lr']), str(outdict['l_match']), str(outdict['l_mismatch']), str(outdict['ref']), max_gt, max_gl];
    # Add the extra columns if --debug.

    if globs['correct-opt']:
        try:
            cor_score = str(int(round(outdict['cor_score'])));
            cor_base = outdict['cor_ref']
        except:
            cor_score, cor_base = "", "";
        outline += [cor_base, cor_score]
    # See if this position has a corrected score if --correct is specified.

    outfile.write("\t".join(outline) + "\n");
#############################################################################

def addUnmapped(file_info, globs):
    scaff_pos, last_scaff, first = 1, "", True;
    # Since we need to have a score for every position in the reference genome and some of those positions are unmapped,
    # scaff_pos keeps track of the last position we've filled in. Comparing it to the current position in the output file
    # or the length of the current scaffold allows us to fill in the missing sites.

    with open(file_info['tmpfile'], "w") as tmpoutfile:
        fq_vars = "";
        if globs['fastq']:
            fqoutfile = open(file_info['outfq'], "w");
            fq_vars = { "fqoutfile" : fqoutfile, "fq_seq" : [], "fq_scores" : [], "fq_curlen" : 0, "fq_lastpos" : 1 }
        # Variables for FASTQ output.

        for line in open(file_info['out']):
            linelist = line.strip().split("\t");
            scaff, pos = linelist[0], int(linelist[1]);
            if scaff != last_scaff:
                if first:
                    first = False
                else:
                    scaff_pos, fq_vars = fillUnmapped(scaff_pos, seqlen, last_scaff, seq, tmpoutfile, globs, fq_vars);
                # If this is not the first scaffold, fill in all positions from the last position on the last scaffold.
                # until the end of that scaffold.

                seq = RC.fastaGet(globs['reffile'], globs['ref'][scaff])[1];
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

            tmpoutfile.write(line);
            scaff_pos += 2; 
            # Simply re-write the line to the tmp file and iterate the scaff_pos.
            # Since the pass to fillUnmapped passed the INDEX (pos-1), I need to add one to get it back into POSITION. Then I need to
            # add one more to go to the next position... hence += 2.

        scaff_pos, fq_vars, filled = fillUnmapped(scaff_pos, seqlen, last_scaff, seq, tmpoutfile, globs, fq_vars, final=True);
        if globs['fastq'] and not filled:
            fqoutdict = { 'scaff' : scaff, 'pos' : pos, 'ref' : seq[pos-1], 'rq' : int(line.strip().split("\t")[2]) };
            fq_vars = outputFastq(fqoutdict, fq_vars, globs, final=True);
            fqoutfile.close();

        # After the last line of the output file, fill in the rest of the positions for that scaffold.
     

#############################################################################

def fillUnmapped(start, stop, scaff, seq, outfile, globs, fq_vars, final=False):
    if final:
        first, filled = True, False;
    while start <= stop:
        if final and first:
            first, filled = False, True;
        outdict = { 'scaff' : scaff, 'pos' : start, 'ref' : seq[start-1], 
                    'rq' : -2, 'lr' : "NA", 'l_match' : "NA", 'l_mismatch' : "NA", 
                    'gls' : "NA", 'cor_ref' : "NA", 'cor_score' : "NA" }; 
        outputTab(outdict, outfile,  globs);

        if globs['fastq']:
            fq_vars = outputFastq(outdict, fq_vars, globs);

        start += 1;

    if final:
        return stop, fq_vars, filled;
    else:
        return stop, fq_vars;

#############################################################################
def testPrint(x, c):
	print(x[1]);