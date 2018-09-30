import global_vars as globs

def outputScores(outfile, scaff, pos, ref, score, fq_seq, fq_scores, fq_curlen, fq_lastpos, final=False, cor_base="", cor_score=""):
    if globs.fastq:
        fq_seq.append(ref);
        score = str(unichr(int(round(score)+35)));
        fq_scores.append(score);
        fq_curlen += 1;

        if fq_curlen == globs.fastq_lnlen or final:
            if final:
                cur_title = "@" + scaff + " " + str(fq_lastpos) + ":" + str(fq_lastpos+int(pos)-1) + " length=" + str(-1 * (fq_lastpos-int(pos)-1));
            else:
                cur_title = "@" + scaff + " " + str(fq_lastpos) + ":" + str(fq_lastpos+int(pos)) + " length=" + str(globs.fastaq_lnlen);

            outfile.write(cur_title + "\n");
            outfile.write("".join(fq_seq) + "\n");
            outfile.write("+\n");
            outfile.write("".join(fq_scores) + "\n");
            fq_lastpos = pos;
    else:
        outfile.write("\t".join([scaff, str(pos), str(int(round(score))), cor_base, cor_score]) + "\n");

    return fq_seq, fq_scores, fq_curlen, fq_lastpos;