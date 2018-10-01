def outputFastq(outfile, scaff, pos, ref, score, fq_seq, fq_scores, fq_curlen, fq_lastpos, globs, final=False):
    fq_seq.append(ref);
    score = str(unichr(int(round(score)+35)));
    fq_scores.append(score);
    fq_curlen += 1;

    if fq_curlen == globs['fastq-len'] or final:
        if final:
            cur_title = "@" + scaff + " " + str(fq_lastpos) + ":" + str(fq_lastpos+int(pos)-1) + " length=" + str(-1 * (fq_lastpos-int(pos)-1));
        else:
            cur_title = "@" + scaff + " " + str(fq_lastpos) + ":" + str(fq_lastpos+int(pos)) + " length=" + str(globs['fastq-len']);

        outfile.write(cur_title + "\n");
        outfile.write("".join(fq_seq) + "\n");
        outfile.write("+\n");
        outfile.write("".join(fq_scores) + "\n");
        fq_lastpos = pos;
    return fq_seq, fq_scores, fq_curlen, fq_lastpos;

def outputTab(outfile, scaff, pos, ref, score, lr, l_match, l_mismatch, gls, globs, cor_base="", cor_score=""):
    if globs['correct-opt']:
        try:
            cor_score = str(int(round(cor_score)));
        except:
            cor_score = "";
    if globs['debug']:
        if score != -2:
            max_gt, max_gl = "", -9999;
            for gt in gls:
                if gls[gt] > max_gl:
                    max_gt = gt;
                    max_gl = gls[gt];
            outline = [scaff, str(pos), str(int(round(score))), str(lr), str(l_match), str(l_mismatch), ref, max_gt, str(max_gl), cor_base, cor_score];
        else:
            max_gt, max_gl = "NA", "NA";
            outline = [scaff, str(pos), str(int(round(score))), lr, l_match, l_mismatch, ref, max_gt, max_gl, cor_base, cor_score];
    else:
        outline = [scaff, str(pos), str(int(round(score))), cor_base, cor_score]
        
    outfile.write("\t".join(outline) + "\n");

    