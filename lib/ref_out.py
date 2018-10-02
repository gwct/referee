def outputFastq(outdict, outfile, fq_seq, fq_scores, fq_curlen, fq_lastpos, globs, final=False):
    fq_seq.append(outdict['ref']);
    score = str(unichr(int(round(outdict['rq'])+35)));
    fq_scores.append(score);
    fq_curlen += 1;

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

def outputTab(outdict, outfile, globs):
    outline = [outdict['scaff'], str(outdict['pos']), str(int(round(outdict['rq'])))];

    if globs['debug']:
        if score != -2:
            max_gt, max_gl = "", -9999;
            for gt in gls:
                if gls[gt] > max_gl:
                    max_gt = gt;
                    max_gl = gls[gt];
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

    