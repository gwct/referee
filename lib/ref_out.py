import os, math, copy, sys, lib.refcore as RC
#############################################################################

def outputDistributor(outdict, prev_scaff, next_pos, outfile, fastqfile, fastafile, globs):
# This function reads an output dictionary for a site and distributes it to the proper output functions.
# If the site being output is preceded by unmapped sites this also fills in those sites in all specified
# outputs with scores of -2.

    cur_scaff, cur_pos = outdict['scaff'], outdict['pos'];
    # Get the scaffold and position for the current site.

    if cur_scaff != prev_scaff:
    # If the current scaffold is not the same as the previous scaffold we may need to fill in positions
    # at the end of the previous scaffold.
        globs['scaffs-written'].append(prev_scaff);
        # Keep track of the scaffolds that have been written.

        # if cur_scaff == "NODE_2_length_11424_cov_14.180312":
        #     print(1, prev_scaff, next_pos, cur_scaff, cur_pos);

        if next_pos <= globs['scaff-lens'][prev_scaff]:
        # If the next position to be added from the previous scaffold does not exceed the scaffold length
        # then we need to add in the unadded positions.

            seq = RC.fastaGet(globs['ref-file'], globs['ref'][prev_scaff])[1];
            # Read the sequence for the previous scaffold.  

            while next_pos <= globs['scaff-lens'][prev_scaff]:
            # Under the conditions outlined above, we want to fill in positions from the previous position to the
            # end of that scaffold.

                unmapped_outdict = { 'scaff' : prev_scaff, 'pos' : next_pos, 'ref' : seq[next_pos-1], 
                            'rq' : -2, 'raw' : "NA", 'lr' : "NA", 'l_match' : "NA", 
                            'l_mismatch' : "NA", 'gls' : "NA", 'cor_ref' : "NA", 
                            'cor_score' : "NA", 'cor_raw' : "NA" };
                # Format the output info for an unmapped position.

                globs['hist'][2]['count'] += 1;
                # Add the score for the unmapped position to the appropriate hist bin.

                outputTab(unmapped_outdict, outfile, globs);
                # Output to tabbed file

                if globs['fastq-opt']:
                    globs = outputFastq(unmapped_outdict, fastqfile, globs);
                # Output to FASTQ file if --fastq was specified.

                if globs['fasta-opt']:
                    globs = outputFasta(unmapped_outdict, fastafile, globs);
                # Output to FASTA file if --fasta was specified.

                if globs['bed-opt']:
                    globs['cur-bed'] = getBedBin(unmapped_outdict['rq'], globs['cur-bed']);
                    if globs['cur-bed']['cur-bin'] != globs['cur-bed']['last-bin']:
                        globs['cur-bed'] = finishBedBin(globs['cur-bed'], next_pos);      
                    # Get score/bin
                # Handle bed binning if --bed was specified.

                next_pos += 1;
                # Iterate the position until it catches up to the end of the scaffold

            if globs['bed-opt']:
                outputBed(globs['cur-bed']);
                globs['cur-bed'] = initializeBed(cur_scaff, globs);
            # Write the bed file for the previous scaffold and and initialize the bed dictionary for the current scaffold.

        prev_scaff, next_pos = cur_scaff, 1;
        # Set the previous scaffold and position to the start of the new scaffold in case there are positions at
        # the beginning of the current scaffold that need to be filled in too.

        # if cur_scaff == "NODE_2_length_11424_cov_14.180312":
        #     print(2, prev_scaff, next_pos, cur_scaff, cur_pos);
    # Fill in sites at the end of the previous scaffold that are unmapped.

    if next_pos != cur_pos:#(cur_pos != (prev_pos + 1) or (prev_pos == 1 and cur_pos != 1)):#prev_pos < cur_pos:# cur_pos != (prev_pos + 1):
    # If the current scaffold is the same as the previous scaffold and (determined by if statement above)
    # the next position to be added is not the current position, then we need to fill in the positions before the current position.

        # if cur_scaff == "NODE_2_length_11424_cov_14.180312":
        #     print(3, prev_scaff, next_pos, cur_scaff, cur_pos);

        seq = RC.fastaGet(globs['ref-file'], globs['ref'][cur_scaff])[1];
        # Read the sequence for the current scaffold

        while next_pos < cur_pos:
        # Under the conditions outlined above, we want to fill in scores until we catch up to the current
        # position.

            #if prev_scaff == "NODE_1_length_16341_cov_45.411461":
            #    print(2, prev_scaff, next_pos, seq[next_pos-1], cur_scaff, cur_pos);

            unmapped_outdict = { 'scaff' : cur_scaff, 'pos' : next_pos, 'ref' : seq[next_pos-1], 
                        'rq' : -2, 'raw' : "NA", 'lr' : "NA", 'l_match' : "NA", 
                        'l_mismatch' : "NA", 'gls' : "NA", 'cor_ref' : "NA", 
                        'cor_score' : "NA", 'cor_raw' : "NA" };
            # Format the output info for an unmapped position.

            globs['hist'][2]['count'] += 1;
            # Add the score for the unmapped position to the appropriate hist bin.

            outputTab(unmapped_outdict, outfile, globs);
            # Output to tabbed file

            if globs['fastq-opt']:
                globs = outputFastq(unmapped_outdict, fastqfile, globs);
            # Output to FASTQ file if --fastq was specified.

            if globs['fasta-opt']:
                globs = outputFasta(unmapped_outdict, fastafile, globs);
            # Output to FASTA file if --fasta was specified.

            if globs['bed-opt']:
                globs['cur-bed'] = getBedBin(unmapped_outdict['rq'], globs['cur-bed']);
                if globs['cur-bed']['cur-bin'] != globs['cur-bed']['last-bin']:
                    globs['cur-bed'] = finishBedBin(globs['cur-bed'], next_pos); 
                # Get score/bin
            # Handle bed binning if --bed was specified.

            next_pos += 1;
            # Iterate the previous position until it catches up to the current position.
    # Fill in sites on current scaffold that precede the current position and are unmapped.

    #if cur_scaff == "NODE_1_length_16341_cov_45.411461":
    #     print(3, prev_scaff, next_pos, cur_scaff, cur_pos, outdict['ref']);

    if globs['correct-opt'] and outdict['cor_ref'] != "NA":
        cur_score = outdict['cor_score'];
        globs['num-corrected'] += 1;
        globs['err-types'][outdict['ref'] + outdict['cor_ref']] += 1;
    else:
        cur_score = outdict['rq'];

    for score_bin in globs['hist']:
        if outdict['rq'] >= globs['hist'][score_bin]['min'] and outdict['rq'] <= globs['hist'][score_bin]['max']:
            globs['hist'][score_bin]['count'] += 1;
            break;
    # Add the score for the unmapped position to the appropriate hist bin.

    # if cur_scaff == "NODE_6_length_8265_cov_5.359917" or prev_scaff == "NODE_6_length_8265_cov_5.359917":
    #     print(prev_scaff, prev_pos, outdict['ref'], cur_scaff, cur_pos);

    outputTab(outdict, outfile, globs);
    # Output to tabbed file

    if globs['fastq-opt']:
        globs = outputFastq(outdict, fastqfile, globs);
    # Output to FASTQ file if --fastq was specified.

    if globs['fasta-opt']:
        globs = outputFasta(outdict, fastafile, globs);
    # Output to FASTA file if --fasta was specified.

    if globs['bed-opt']:
        if cur_scaff != prev_scaff:
            outputBed(globs['cur-bed']);
            globs['cur-bed'] = initializeBed(cur_scaff, globs);
        # Write the bed file for the previous scaffold and and initialize the bed dictionary for the current scaffold.

        globs['cur-bed'] = getBedBin(cur_score, globs['cur-bed']);
        if globs['cur-bed']['cur-bin'] != globs['cur-bed']['last-bin']:
            globs['cur-bed'] = finishBedBin(globs['cur-bed'], next_pos);   
            # Get score/bin
        # Handle bed binning if --bed was specified.
    # Handle bed output for current site if --bed was specified.
    # Output the score for the current site

    return cur_scaff, cur_pos+1, globs;

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
        if outdict['cor_ref'] != "NA":
            cor_score = str(int(round(outdict['cor_score'])));
            cor_base = outdict['cor_ref'];
            if globs['raw-opt']:
                cor_raw = str(outdict['cor_raw']);
        else:
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
    if globs['correct-opt'] and outdict['cor_ref'] != "NA":
        globs['cur-fastq-seq'] += outdict['cor_ref'];
        score = str(chr(int(round(outdict['cor_score'])+35)));
    else:
        globs['cur-fastq-seq'] += outdict['ref'];
        score = str(chr(int(round(outdict['rq'])+35)));
    globs['cur-fastq-scores'] += score;
    globs['cur-fastq-len'] += 1;
    # Adds the current base and ascii score to the corresponding lists.

    if globs['cur-fastq-len'] == globs['fastq-line-len'] or pos == globs['scaff-lens'][scaff]:    
        cur_title = "@" + outdict['scaff'] + " " + str(outdict["pos"]-int(len(globs["cur-fastq-seq"]))+1) + ":" + str(outdict["pos"]) + " length=" + str(len(globs["cur-fastq-seq"]));
        # Set the current header info.

        fastqfile.write(cur_title + "\n");
        fastqfile.write(globs["cur-fastq-seq"] + "\n");
        fastqfile.write("+\n");
        fastqfile.write(globs["cur-fastq-scores"] + "\n");
        # Write the title, sequence, and scores to the FASTQ file.

        globs['cur-fastq-seq'], globs['cur-fastq-scores'], globs['cur-fastq-len']  = "", "", 0;
        # Reset the sequence and score strings.
    # This writes the sequence and scores if the length of the sequence matches the max fastq line length (global) or if its the final position of the scaffold.

    return globs;

#############################################################################

def outputFasta(outdict, fastafile, globs):
# For output to FASTA format.
    scaff, pos = outdict['scaff'], outdict['pos'];
    if globs['correct-opt'] and outdict['cor_ref'] != "NA":
        globs['cur-fasta-seq'] += outdict['cor_ref'];
        globs['scaff-errs'] += 1;
    else:
        globs['cur-fasta-seq'] += outdict['ref'];
        score = str(chr(int(round(outdict['rq'])+35)));

    if outdict['rq'] == -2:
        globs['scaff-unmapped'] += 1;
    # Adds the current base and ascii score to the corresponding lists.

    if pos == globs['scaff-lens'][scaff]:
        scaff_err_rate = globs['scaff-errs'] / globs['scaff-lens'][scaff];
        perc_unmapped = ( globs['scaff-unmapped'] / globs['scaff-lens'][scaff] ) * 100;
        cur_title = ">" + scaff + " REFEREE_ERRORS_CORRECTED:" + str(globs['scaff-errs']) + " REFEREE_ERROR_RATE:" + str(scaff_err_rate) + " POSITIONS_UNMAPPED:" + str(globs['scaff-unmapped']) + " PERCENT_UNMAPPED:" + str(perc_unmapped);
        cur_lines = [ globs['cur-fasta-seq'][i:i+globs['fasta-line-len']] for i in range(0, len(globs['cur-fasta-seq']), globs['fasta-line-len']) ];
        # Split the current sequence into evenly spaced lines

        fastafile.write(cur_title + "\n");
        for line in cur_lines:
            fastafile.write(line + "\n");

        globs['cur-fasta-seq'], globs['scaff-errs'], globs['scaff-unmapped'] = "", 0, 0;
    return globs;
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