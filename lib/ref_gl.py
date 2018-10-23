import sys, math, refcore as RC
#############################################################################

def glInit(mapq):
    log_probs = {};
    for i in range(1,94):
        bq = unichr(i+33);
        bpe = 10.0 ** (-i/10.0);

        if mapq:
            for j in range(1,94):
                mq = unichr(j+33);
                mpe = 10.00 ** (-j/10.0);
                log_probs[bq+mq] = [0,0,0];
                match_p = (0.5 * (1-bpe)) * (0.5 * (1-mpe));
                mismatch_p = (0.5 * (bpe/3.0)) * (0.5 * (mpe/3.0));

                log_probs[bq+mq][0] = math.log(match_p + match_p);
                log_probs[bq+mq][1] = math.log(match_p + mismatch_p);
                log_probs[bq+mq][2] = math.log(mismatch_p + mismatch_p);

        else:
            log_probs[bq] = [0,0,0];

            match_p = (0.5 * (1-bpe));
            mismatch_p = (0.5 * (bpe/3.0));

            log_probs[bq][0] = math.log(match_p + match_p);
            log_probs[bq][1] = math.log(match_p + mismatch_p);
            log_probs[bq][2] = math.log(mismatch_p + mismatch_p);

    return log_probs;

