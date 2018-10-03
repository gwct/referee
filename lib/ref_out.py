import refcore as RC
#############################################################################

def outputFastq(outdict, outfile, fq_seq, fq_scores, fq_curlen, fq_lastpos, globs, final=False):
    fq_seq.append(outdict['ref']);
    score = str(unichr(int(round(outdict['rq'])+35)));
    fq_scores.append(score);
    fq_curlen += 1;
    print fq_curlen, globs['fastq-len'];    

    if fq_curlen == globs['fastq-len'] or final:
        if final:
            cur_title = "@" + outdict['scaff'] + " " + str(fq_lastpos) + ":" + str(fq_lastpos+int(outdict['pos'])-1) + " length=" + str(-1 * (fq_lastpos-int(outdict['pos'])-1));
        else:
            cur_title = "@" + outdict['scaff'] + " " + str(fq_lastpos) + ":" + str(fq_lastpos+int(outdict['pos'])) + " length=" + str(globs['fastq-len']);

        outfile.write(cur_title + "\n");
        outfile.write("".join(fq_seq) + "\n");
        outfile.write("+\n");
        outfile.write("".join(fq_scores) + "\n");
        fq_lastpos = outdict['pos'];
    return fq_seq, fq_scores, fq_curlen, fq_lastpos;
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

    with open(file_info['tmpfile'], "w") as tmpoutfile, open(file_info['outfq'], "w") as fqoutfile:
        #fq_vars = { 'seq' : [], 'scores' []}

        if globs['fastq']:
            fqoutfile = open(file_info['outfq']);
            fq_seq, fq_scores, fq_curlen, fq_lastpos = [], [], 0, 1;
        # Variables for FASTQ output.

        for line in open(file_info['out']):
            linelist = line.strip().split("\t");
            scaff, pos = linelist[0], int(linelist[1]);
            if scaff != last_scaff:
                if first:
                    first = False
                else:
                    scaff_pos, fq_seq, fq_scores, fq_curlen, fq_lastpos = fillUnmapped(scaff_pos, seqlen, last_scaff, seq, tmpoutfile, globs,
                                                                                        fqfile, fq_seq fq_scores fq_curlen fq_lastpos);
                # If this is not the first scaffold, fill in all positions from the last position on the last scaffold.
                # until the end of that scaffold.

                seq = RC.fastaGet(globs['reffile'], globs['ref'][scaff])[1];
                seqlen = len(seq);
                scaff_pos = 1;
                last_scaff = scaff;
                # When the scaffold changes, get the new seq, seqlen, last_scaff, and reset scaff_pos to 1.

            scaff_pos = fillUnmapped(scaff_pos, pos-1, scaff, seq, tmpoutfile, globs) + 1;
            # If the current scaff_pos is below the pos in the output file, we need to fill in the unmapped positions
            # up to that position.

            tmpoutfile.write(line);
            scaff_pos += 1; 
            # Simply re-write the line to the tmp file and iterate the scaff_pos.

        scaff_pos = fillUnmapped(scaff_pos, seqlen, last_scaff, seq, tmpoutfile, globs);
        # After the last line of the output file, fill in the rest of the positions for that scaffold.
     

#############################################################################

def fillUnmapped(start, stop, scaff, seq, outfile, globs, fqfile=False, fq_seq="", fq_scores="", fq_curlen="", fq_lastpos=""):
    while start <= stop:
        outdict = { 'scaff' : scaff, 'pos' : start, 'ref' : seq[start-1], 
                    'rq' : -2, 'lr' : "NA", 'l_match' : "NA", 'l_mismatch' : "NA", 
                    'gls' : "NA", 'cor_ref' : "NA", 'cor_score' : "NA" }; 
        outputTab(outdict, outfile,  globs);
        if globs['fastq']:
            fq_seq, fq_scores, fq_curlen, fq_lastpos = outputFastq(outdict, fqfile, fq_seq, fq_scores, fq_curlen, fq_lastpos, globs)

        start += 1;
    return stop, fq_seq, fq_scores, fq_curlen, fq_lastpos;





#############################################################################
def testPrint(x, c):
	print(x[1]);