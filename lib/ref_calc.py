import gzip, math, global_vars as globs, ref_out as OUT
from Bio import SeqIO

def refCalc(file_item):
    gl_file, ref_file, outfilename = file_item[0], file_item[1][0], file_item[1][1];

    genotypes = ["AA", "AC", "AG", "AT", "CC", "CG", "CT", "GG", "GT", "TT"]
    last_scaff = "";

    fq_seq, fq_scores, fq_curlen, fq_lastpos = [], [], 0, 1;
    # Variables for FASTQ output. If FASTQ is not specified, these will remain unchanged and just be passed back and forth.

    with open(outfilename, "w") as outfile:
        try:
            gzip_check = gzip.open(gl_file).read(1);
            reader = gzip.open;
        except:
            reader = open;
        # Check if the genotype likelihood file is gzipped, and if so set gzip as the file reader. Otherwise, read as a normal text file.

        for line in reader(gl_file):
            line = line.strip().split("\t");
            scaff, pos, gl_list = line[0], int(line[1]), line[2:];
            gls = { genotypes[x] : math.exp(float(gl_list[x])) for x in range(len(gl_list)) };
            # Parse the info from the current line -- scaffold, position, genotype likelihoods.

            if scaff != last_scaff:
                #if globs.fastq:
                #    outfile.write("@" + scaff + "\n");
                for record in SeqIO.parse(ref_file, "fasta"):
                    if record.id == scaff:
                        seq = record.seq;
                        break;
                scaff_pos = 1;
            last_scaff = scaff;
            # If the scaffold of the current line is different from the last scaffold, retrieve the sequence.

            while scaff_pos != pos:
                scaff_ref = seq[scaff_pos-1];
                fq_seq, fq_scores, fq_curlen, fq_lastpos = OUT.outputScores(outfile, scaff, str(pos), scaff_ref, -2, fq_seq, fq_scores, fq_curlen, fq_lastpos);

                
                scaff_pos += 1;
            # If the current position has skipped ahead from where we are in the scaffold, that means there are
            # intervening positions with no reads. This fills in those scores as -2.

            ref = seq[pos-1];
            # Gets the called reference base at the current position.

            if ref.upper() in "NXB-":
                rq = -1;
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
                    rq = 92;
                # If the sum of the genotypes that don't match the called reference base is 0, assign maximum score.
                # This should scale with read depth somehow, though...
                elif l_match == 0:
                    rq = -3;
                # If the sum of the genotyps that match the called reference base is 0, assign a score of -3. This should never happen.
                else:
                    lr = l_match / l_mismatch;
                    rq = math.log(lr, 10);
                    # Calculate the match : mismatch ratio and log transform.
                    if rq > 91:
                        rq = 91;
                    if rq < 0:
                        rq = 0;
                    # Scale the scores so the max score is 91 and the all negative scores are 0.

            fq_seq, fq_scores, fq_curlen, fq_lastpos = OUT.outputScores(outfile, scaff, str(pos), scaff_ref, rq, fq_seq, fq_scores, fq_curlen, fq_lastpos);
            scaff_pos += 1;
            # Write the score to the output file and iterate the scaff_pos.

        fq_seq, fq_scores, fq_curlen, fq_lastpos = OUT.outputScores(outfile, scaff, str(pos), scaff_ref, rq, fq_seq, fq_scores, fq_curlen, fq_lastpos, final=True);