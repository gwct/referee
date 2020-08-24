import os, math, copy, lib.refcore as RC
#############################################################################

def outputDistributor(outdict, prev_scaff, prev_pos, outfile, fastqfile, globs):
# This function reads an output dictionary for a site and distributes it to the proper output functions.
# If the site being output is preceded by unmapped sites this also fills in those sites in all specified
# outputs with scores of -2.

    cur_scaff, cur_pos = outdict['scaff'], outdict['pos'];
    # Get the scaffold and position for the current site.

    if prev_scaff != "" and cur_scaff != prev_scaff and prev_pos != globs['scaff-lens'][prev_scaff]:
    # If we're not on the first scaffold (prev_scaff != "") and
    # if the current scaffold is not the same as the previous scaffold and
    # the previous position is not the last position of the previous scaffold.

        seq = RC.fastaGet(globs['ref-file'], globs['ref'][prev_scaff])[1];
        # Read the sequence for the previous scaffold.

        while prev_pos <= globs['scaff-lens'][prev_scaff]:
        # Under the conditions outlined above, we want to fill in positions from the previous position to the
        # end of that scaffold.

            unmapped_outdict = { 'scaff' : prev_scaff, 'pos' : prev_pos, 'ref' : seq[prev_pos-1], 
                        'rq' : -2, 'raw' : "NA", 'lr' : "NA", 'l_match' : "NA", 
                        'l_mismatch' : "NA", 'gls' : "NA", 'cor_ref' : "NA", 
                        'cor_score' : "NA", 'cor_raw' : "NA" };
            # Format the output info for an unmapped position.

            outputTab(unmapped_outdict, outfile, globs);
            # Output to tabbed file

            if globs['fastq-opt']:
                outputFastq(unmapped_outdict, fastqfile, globs);
            # Output to FASTQ file if --fastq was specified.

            if globs['bed-opt']:
                globs['cur-bed'] = getBedBin(unmapped_outdict['rq'], globs['cur-bed']);
                if globs['cur-bed']['cur-bin'] != globs['cur-bed']['last-bin']:
                    globs['cur-bed'] = finishBedBin(globs['cur-bed'], prev_pos);      
                # Get score/bin
            # Handle bed binning if --bed was specified.

            prev_pos += 1;
            # Iterate the position until it catches up to the end of the scaffold

        if globs['bed-opt']:
            outputBed(globs['cur-bed']);
            globs['cur-bed'] = initializeBed(cur_scaff, globs);
        # Write the bed file for the previous scaffold and and initialize the bed dictionary for the current scaffold.

        prev_scaff, prev_pos = cur_scaff, 1;
        # Set the previous scaffold and position to the start of the new scaffold in case there are positions at
        # the beginning of the current scaffold that need to be filled in too.
    # Fill in sites at the end of the previous scaffold that are unmapped.

    if (cur_scaff == prev_scaff or prev_scaff == "") and cur_pos != (prev_pos + 1):
    # If the current scaffold is the same as the previous scaffold or this is the first scaffold and
    # The current position is not directly after the last position

        seq = RC.fastaGet(globs['ref-file'], globs['ref'][cur_scaff])[1];
        # Read the sequence for the current scaffold

        while prev_pos < cur_pos:
        # Under the conditions outlined above, we want to fill in scores until we catch up to the current
        # position.

            unmapped_outdict = { 'scaff' : cur_scaff, 'pos' : prev_pos, 'ref' : seq[prev_pos-1], 
                        'rq' : -2, 'raw' : "NA", 'lr' : "NA", 'l_match' : "NA", 
                        'l_mismatch' : "NA", 'gls' : "NA", 'cor_ref' : "NA", 
                        'cor_score' : "NA", 'cor_raw' : "NA" };
            # Format the output info for an unmapped position.

            outputTab(unmapped_outdict, outfile, globs);
            # Output to tabbed file

            if globs['fastq-opt']:
                outputFastq(unmapped_outdict, fastqfile, globs);
            # Output to FASTQ file if --fastq was specified.

            if globs['bed-opt']:
                globs['cur-bed'] = getBedBin(unmapped_outdict['rq'], globs['cur-bed']);
                if globs['cur-bed']['cur-bin'] != globs['cur-bed']['last-bin']:
                    globs['cur-bed'] = finishBedBin(globs['cur-bed'], prev_pos); 
                # Get score/bin
            # Handle bed binning if --bed was specified.

            prev_pos += 1;
            # Iterate the previous position until it catches up to the current position.
    # Fill in sites on current scaffold that precede the current position and are unmapped.

    outputTab(outdict, outfile, globs);
    # Output to tabbed file

    if globs['fastq-opt']:
        outputFastq(outdict, fastqfile, globs);
    # Output to FASTQ file if --fastq was specified.

    if globs['bed-opt']:
        if cur_scaff != prev_scaff:
            outputBed(globs['cur-bed']);
            globs['cur-bed'] = initializeBed(cur_scaff, globs);
        # Write the bed file for the previous scaffold and and initialize the bed dictionary for the current scaffold.

        globs['cur-bed'] = getBedBin(outdict['rq'], globs['cur-bed']);
        if globs['cur-bed']['cur-bin'] != globs['cur-bed']['last-bin']:
            globs['cur-bed'] = finishBedBin(globs['cur-bed'], prev_pos);   
            # Get score/bin
        # Handle bed binning if --bed was specified.
    # Handle bed output for current site if --bed was specified.
    # Output the score for the current site

    return cur_scaff, cur_pos;

#############################################################################

def outputTab(outdict, outfile, globs):
# For output to tab delimited format.

    outline = [outdict['scaff'], str(outdict['pos']), str(int(round(outdict['rq'])))];
    # Set-up the basic output: scaffold, position, and score.

    if globs['allcalc-opt']:
        if outdict['rq'] != -2:
            max_gt, max_gl = "", -9999;
            for gt in outdict['gls']:
                if outdict['gls'][gt] > max_gl:
                    max_gt = gt;
                    max_gl = outdict['gls'][gt];
        else:
            max_gt, max_gl = "NA", "NA"
        outline += [str(outdict['lr']), str(outdict['l_match']), str(outdict['l_mismatch']), str(outdict['ref']), max_gt, str(max_gl)];
    # Add the extra columns if --allcalcs.

    if globs['raw-opt']:
        outline += [str(outdict['raw'])];
    # Add the extra column for the --raw option.

    if globs['correct-opt']:
        try:
            cor_score = str(int(round(outdict['cor_score'])));
            cor_base = outdict['cor_ref'];
            if globs['raw-opt']:
                cor_raw = str(outdict['cor_raw']);
        except:
            cor_score, cor_base, cor_raw = "", "", "";
        if globs['raw-opt']:
            outline += [cor_base, cor_score, cor_raw];
        else:
            outline += [cor_base, cor_score];
    # See if this position has a corrected score if --correct is specified.

    outfile.write("\t".join(outline) + "\n");
    # Write the line.

#############################################################################

def outputFastq(outdict, fastqfile, globs):
# For output to FASTQ format.

    scaff, pos = outdict['scaff'], outdict['pos'];
    globs['cur-fastq-seq'] += outdict['ref'];
    score = str(chr(int(round(outdict['rq'])+35)));
    globs['cur-fastq-scores'] += score;
    globs['cur-fastq-len'] += 1;
    # Adds the current base and ascii score to the corresponding lists.

    if globs['cur-fastq-len'] == globs['fastq-line-len'] or pos == globs['scaff-lens'][scaff]:      
        cur_title = "@" + outdict['scaff'] + " " + str(outdict["pos"]-int(len(globs["cur-fastq-seq"]))+1) + ":" + str(outdict["pos"]) + " length=" + str(len(globs["cur-fastq-seq"]));
        # Set the current FASTQ title.

        fastqfile.write(cur_title + "\n");
        fastqfile.write(globs["cur-fastq-seq"] + "\n");
        fastqfile.write("+\n");
        fastqfile.write(globs["cur-fastq-scores"] + "\n");
        # Write the title, sequence, and scores.

        globs['cur-fastq-seq'], globs['cur-fastq-scores'], globs['cur-fastq-len']  = "", "", 0;
        # Reset the sequence and score strings.
    # This writes the sequence and scores if the length of the sequence matches the max fastq line length (global) or if its the final position of the scaffold.

#############################################################################

def initializeBed(scaff, globs):
# When a new scaffold is encountered, initialize the bed dictionary.
    cur_bed = copy.deepcopy(globs['bed-template']);
    cur_bed['scaff'] = scaff;
    cur_bed['out'] = os.path.join(globs['bed-dir'], scaff + ".bed");
    cur_bed['scaff-len'] = globs['scaff-lens'][scaff];
    return cur_bed;

#############################################################################

def getBedBin(score, cur_bed):
# Given a Referee score, this function returns the bin that score is in.
    if score <= 0:
        b = 1;
    elif score > 80:
        b = 10;
    else:
        upper = int(math.ceil(score / 10.0)) * 10;
        b = (upper / 10) + 1;
        # if upper == 10:
        #     b = 2;
        # elif upper == 20:
        #     b = 3
        # elif upper == 30:
        #     b = 4
        # elif upper == 40:
        #     b = 5
        # elif upper == 50:
        #     b = 6
        # elif upper == 60:
        #     b = 7
        # elif upper == 70:
        #     b = 8
        # elif upper == 80:
        #     b = 9

    cur_bed['cur-bin'] = b;
    # Set the current bin.

    if not cur_bed['last-bin']:
        cur_bed['last-bin'] = b;
    # If this is the first scaffold, set the last bin to be the same as the current bin.
    
    return cur_bed;

#############################################################################

def finishBedBin(cur_bed, pos, seqlen=""):
# After a given stretch of scores in the same bin, the info for that chunk is saved to the bin dictionary here.
# Am I off by 1?

    prev_bin, next_bin = cur_bed['last-bin'], cur_bed['cur-bin'];
    # Unpack the bins from the current bed dict.

    cur_bed['bins'][prev_bin]['num-chunks'] += 1;
    # Iterate the number of chunks.    

    cur_bed['bins'][prev_bin]['last-pos'] = pos;
    # Update the current last position. If its the last bin it will be the correct last position for the file.

    cur_size = (pos - cur_bed['chunk-start']);
    cur_bed['bins'][prev_bin]['chunk-sizes'].append(str(cur_size));
    # Calculate the size of the current chunk.

    cur_bed['bins'][prev_bin]['chunk-starts'].append(str(cur_bed['chunk-start']));
    # Add in the chunk start.

    cur_bed['chunk-start'] = pos;
    # Update the chunk start for the next bin.

    cur_bed['last-bin'] = cur_bed['cur-bin'];
    # Update the bin.

    return cur_bed

#############################################################################

def outputBed(cur_bed):
# For output to bed format.
    with open(cur_bed['out'], "w") as bedfile:
    # Open the bed output file.    
        bedfile.write("browser position " + cur_bed['scaff'] + "\n");
        bedfile.write("browser hide all\n");
        bedfile.write("track name=\"" + cur_bed['scaff'] + " Referee\" description=\"Referee quality scores\" visibility=2 itemRgb=\"On\"\n");
        # These are the bed header lines.

        for b in cur_bed['bins']:
            outline = "\t".join([cur_bed['scaff'], 
                str(cur_bed['bins'][b]['first-pos']), 
                str(cur_bed['bins'][b]['last-pos']), 
                cur_bed['bins'][b]['name'], 
                str(cur_bed['bins'][b]['shade']),  
                ".", 
                str(cur_bed['bins'][b]['first-pos']), 
                str(cur_bed['bins'][b]['last-pos']), 
                cur_bed['bins'][b]['rgb']]
                );
            outline += "\t" + str(cur_bed['bins'][b]['num-chunks']);
            outline += "\t" + ",".join(cur_bed['bins'][b]['chunk-sizes']);
            outline += "\t" + ",".join(cur_bed['bins'][b]['chunk-starts']);
            # The bed output info for each bin.
            bedfile.write(outline + "\n");

#############################################################################