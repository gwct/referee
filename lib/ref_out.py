import sys, os, math, refcore as RC
#############################################################################

def outputFastq(outdict, fq_vars, globs, final=False):
# For output to FASTQ format.
    if not final:
        #if globs['correct-opt'] and outdict['rq'] in [0,-1,-3]:
        #    fq_vars["fq_seq"] = outdict["cor_ref"];
        #    score = str(unichr(int(round(outdict["cor_score"])+35)));
        #else:
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

def outputBed(bed, bed_vars):
    with open(bed_vars['bedout'], "w") as bedfile:
        bedfile.write("browser position " + bed['scaff'] + "\n");
        bedfile.write("browser hide all\n");
        bedfile.write("track name=\"" + bed['scaff'] + " Referee\" description=\"Quality scores calculated by Referee\" visibility=2\n");

        for b in bed['bins']:
            outline = "\t".join([bed['scaff'], "0", str(bed['scaff-end']), bed['bins'][b]['name'], ".", "0", str(bed['scaff-end']), bed['bins'][b]['rgb']]);
            outline += "\t" + str(bed['bins'][b]['num-chunks']);
            outline += "\t" + ",".join(bed['bins'][b]['chunk-sizes']);
            outline += "\t" + ",".join(bed['bins'][b]['chunk-starts']);
            bedfile.write(outline + "\n");

#############################################################################

def bedInit(scaff, seqlen, globs, score):
    cur_bed = {
            'scaff' : scaff, 'scaff-start' : 0, 'scaff-end' : seqlen, 
            'bins' : 
            {
                1 : { 'name' : '<=0', 'rgb' : "255,0,0", 'num-chunks' : 0, 'chunk-sizes' : [], 'chunk-starts' : []},
                2 : { 'name' : '1-10', 'rgb' : "255,0,0", 'num-chunks' : 0, 'chunk-sizes' : [], 'chunk-starts' : []},
                3 : { 'name' : '11-20', 'rgb' : "255,0,0", 'num-chunks' : 0, 'chunk-sizes' : [], 'chunk-starts' : []},
                4 : { 'name' : '21-30', 'rgb' : "255,0,0", 'num-chunks' : 0, 'chunk-sizes' : [], 'chunk-starts' : []},
                5 : { 'name' : '31-40', 'rgb' : "255,0,0", 'num-chunks' : 0, 'chunk-sizes' : [], 'chunk-starts' : []},
                6 : { 'name' : '41-50', 'rgb' : "255,0,0", 'num-chunks' : 0, 'chunk-sizes' : [], 'chunk-starts' : []},
                7 : { 'name' : '51-60', 'rgb' : "255,0,0", 'num-chunks' : 0, 'chunk-sizes' : [], 'chunk-starts' : []},
                8 : { 'name' : '61-70', 'rgb' : "255,0,0", 'num-chunks' : 0, 'chunk-sizes' : [], 'chunk-starts' : []},
                9 : { 'name' : '71-80', 'rgb' : "255,0,0", 'num-chunks' : 0, 'chunk-sizes' : [], 'chunk-starts' : []},
                10 : { 'name' : '81+', 'rgb' : "255,0,0", 'num-chunks' : 0, 'chunk-sizes' : [], 'chunk-starts' : []}
            }
        };
    bed_vars = { 'bedout' : os.path.join(globs['beddir'], scaff + ".bed"),
                 'chunk-start' : 0, 'last-bin' : getBedBin(score), 'cur-bin' : getBedBin(score) };

    return cur_bed, bed_vars;

#############################################################################

def getBedBin(score):
    if score <= 0:
        b = 1;
    elif score >= 81:
        b = 10;
    else:
        upper = int(math.ceil(score / 10.0)) * 10;
        if upper == 10:
            b = 2;
        elif upper == 20:
            b = 3
        elif upper == 30:
            b = 4
        elif upper == 40:
            b = 5
        elif upper == 50:
            b = 6
        elif upper == 60:
            b = 7
        elif upper == 70:
            b = 8
        elif upper == 80:
            b = 9
    return b;

#############################################################################

def finishBedBin(bed, bed_vars, pos):

    print pos, bed_vars;

    bed['bins'][bed_vars['cur_bin']]['num-chunks'] += 1;
    cur_size = pos - bed_vars['chunk-start'] - 1
    bed['bins'][bed_vars['cur_bin']]['chunk-sizes'].append(str(cur_size));
    bed['bins'][bed_vars['cur_bin']]['chunk-starts'].append(str(bed_vars['chunk-start']));

    bed_vars['chunk-start'] = pos;
    bed_vars['last_bin'] = bed_vars['cur_bin'];

    return bed_vars, bed;

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

def addUnmapped(file_item):
# Since we need to have a score for every position in the reference genome and some of those positions are unmapped,
# this function goes through the positions in the output file and adds the unmapped positions.

    file_num, file_info, globs = file_item;
    scaff_pos, last_scaff, first = 1, "", True;
    # scaff_pos keeps track of the last position we've filled in. Comparing it to the current position in the output file
    # or the length of the current scaffold allows us to fill in the missing sites.

    with open(file_info['tmpfile'], "w") as tmpoutfile:
        fq_vars = {};
        if globs['fastq']:
            fqoutfile = open(file_info['outfq'], "w");
            fq_vars = { "fqoutfile" : fqoutfile, "fq_seq" : "", "fq_scores" : "", "filled" : False }
        # Variables for FASTQ output.

        bed_vars = { 'last-bin' : "" };
        # A dummy bed_vars to pass to functions when --bed isn't called.

        for line in open(file_info['out']):
            linelist = line.strip().split("\t");
            scaff, pos, score = linelist[0], int(linelist[1]), int(linelist[2]);
            if globs['bed']:
                cur_bin = getBedBin(score);

            if scaff != last_scaff:
                if first:
                    first = False
                else:
                    scaff_pos, fq_vars, bed_vars = fillUnmapped(scaff_pos, seqlen, last_scaff, seq, tmpoutfile, globs, fq_vars, bed_vars);
                    if globs['bed']:
                        outputBed(cur_bed, bed_vars);
                # If this is not the first scaffold, fill in all positions from the last position on the last scaffold.
                # until the end of that scaffold.

                seq = RC.fastaGet(globs['reffile'], globs['ref'][scaff])[1];
                seqlen = len(seq);
                scaff_pos = 1;
                last_scaff = scaff;
                # When the scaffold changes, get the new seq, seqlen, last_scaff, and reset scaff_pos to 1.

                if globs['bed']:
                    cur_bed, bed_vars = bedInit(scaff, seqlen, globs, score);
                # Initialize the BED structures for this scaffold.

            scaff_pos, fq_vars, bed_vars = fillUnmapped(scaff_pos, pos-1, scaff, seq, tmpoutfile, globs, fq_vars, bed_vars);
            # If the current scaff_pos is below the pos in the output file, we need to fill in the unmapped positions
            # up to that position.

            if globs['fastq']:
                if globs['correct-opt'] and len(linelist) == 5:
                    fqoutdict = { 'scaff' : scaff, 'pos' : pos, 'ref' : linelist[3].lower(), 'rq' : int(linelist[4]) };
                else:
                    fqoutdict = { 'scaff' : scaff, 'pos' : pos, 'ref' : seq[pos-1], 'rq' : int(linelist[2]) };
                fq_vars = outputFastq(fqoutdict, fq_vars, globs);
            # Output the current position to FASTQ.

            tmpoutfile.write(line);
            scaff_pos += 2; 
            # Simply re-write the line to the tmp file and iterate the scaff_pos.
            # Since the pass to fillUnmapped passed the INDEX (pos-1), I need to add one to get it back into POSITION. Then I need to
            # add one more to go to the next position... hence += 2.

            print score, cur_bin;
            if bed_vars['cur_bin'] != bed_vars['last-bin']:
                bed_vars, cur_bed = finishBedBin(cur_bed, bed_vars, pos);
            # If the bin of the current score is different from the bin of the last score,
            # finish the BED bin.

        if globs['bed'] and bed_vars['cur_bin'] != 1:
            bed_vars, cur_bed = finishBedBin(cur_bed, bed_vars, pos);
        # If we're at the end of the loop and the bin isn't 1, we need to finish it before checking for
        # unmapped positions.

        scaff_pos, fq_vars, bed_vars = fillUnmapped(scaff_pos, seqlen, last_scaff, seq, tmpoutfile, globs, fq_vars, bed_vars, final=True);
        # After the last line of the output file, fill in the rest of the positions for that scaffold.
        if globs['fastq']:
            if not fq_vars['filled'] and fq_vars['fq_seq'] != "":
                fq_vars = outputFastq(fqoutdict, fq_vars, globs, final=True);
            fqoutfile.close();
        # Write the final FASTQ line if the last position was mapped and had a score and close the FASTQ output file.

        if globs['bed']:
            bed_vars = finishBedBin(cur_bin, cur_bed, bed_vars, pos);
            print bed_vars;
            outputBed(cur_bed, bed_vars);

        return file_num;

#############################################################################

def fillUnmapped(start, stop, scaff, seq, outfile, globs, fq_vars, bed_vars, final=False, first=True):
# Given a start and stop position, this function fills in the scores for unmapped positions
# up to the stop position. The score for unmapped positions is -2.

    while start <= stop:
        bed_vars['last-bin'] = 1
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

    if globs['fastq'] and final and fq_vars['filled'] and fq_vars['fq_seq'] != "":
        fq_vars = outputFastq(outdict, fq_vars, globs, final=True);
    # If this is the final call and the last position was unmapped, we call the final FASTQ output here.

    return stop, fq_vars, bed_vars;

#############################################################################
