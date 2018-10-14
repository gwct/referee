############################################################
# Functions for Referee markdown site, 10.18
# Gregg Thomas
############################################################

gl <- function(reads, base_probs, map_probs, ref, meth){
  genotypes = c("AA","AT","AC","AG","TT","TC","TG","CC","CG","GG")
  gt_data = data.frame(genotypes)
  gt_data$probs = 1
  
  for(gt in gt_data$genotypes){
    a1 = substr(gt,1,1)
    a2 = substr(gt,2,2)
    rprobs = c()
    
    for(i in 1:length(reads)){
      r = reads[i]
      p = base_probs[i] * map_probs[i]
      aprobs = c()
      for(a in c(a1,a2)){
        if(r==a){
          aprobs = c(aprobs, 1-p)
        }else if (r!=a){
          aprobs = c(aprobs, p/3)
        }
      }
      rprobs = c(rprobs, ((0.5 * aprobs[1]) + (0.5 * aprobs[2])))
    }
    gt_data$probs[which(gt_data$genotypes==gt)] = prod(rprobs)
  }
  
  gt_data$pl = -10 * log(gt_data$probs, 10)
  gt_data$norm_pl = gt_data$pl - min(gt_data$pl)
  gt_data$norm_pl[which(gt_data$norm_pl==0)] = NA
  min_gt = gt_data$genotype[which(gt_data$pl==min(gt_data$pl))]
  gq = gt_data$norm_pl[which(gt_data$norm_pl==min(gt_data$norm_pl, na.rm=T))]
  
  match_gt = subset(gt_data, grepl(ref, genotypes))
  unmatch_gt = subset(gt_data, !grepl(ref, genotypes))
  
  p_correct = sum(match_gt$probs)
  p_incorrect = sum(unmatch_gt$probs)
  
  #p_ratio = p_incorrect / p_correct
  #p_ratio = abs(2 * (log(p_correct) - log(p_incorrect)))
  
  if(meth==1){
    rq = abs(p_incorrect - p_correct)
    rq = -10 * log(rq, 10)
  }else if(meth=="1a"){
    if(grepl(ref, min_gt)){
      rq = abs(p_correct - p_incorrect)
    }else{
      rq = abs(1 - (p_correct - p_incorrect))
    }
    rq = -10 * log(rq, 10)
  }else if(meth==2){
    rq = (p_correct / p_incorrect)
    rq = log(rq, 10)
  }else if(meth==3){
    rq = 2 * (log(p_incorrect) - log(p_correct))
    rq = -10 * log(abs(rq), 10)
  }else if(meth==4){
    rq = -10 * log(p_correct, 10)
  }else if(meth==5){
    rq = -10 * log(max(match_gt$probs), 10)
  }
  
  gl_result = c(as.character(min_gt), gq[1], rq)
  return(gl_result)
}
#####

cycleReads <- function(cur_read_set, meth){
  min_gts = c()
  quals = c()
  alt_b_quals = c()
  alt_m_quals = c()
  ref_quals = c()
  
  #cat(cur_read_set$num, cur_read_set$reads, "\n")
  
  alt_b_qual = 40
  while(alt_b_qual > 0){
    baseq = c()
    for(i in 1:length(cur_read_set$reads)){
      baseq = c(baseq, 40)
    }
    baseq[length(baseq)] = alt_b_qual
    basep = 10^(-baseq / 10)
    
    alt_m_qual = 40
    while(alt_m_qual > 0){
      #cat(alt_b_qual, alt_m_qual, "\n")
      mapq = c()
      for(i in 1:length(cur_read_set$reads)){
        mapq = c(mapq, 40)
      }
      mapq[length(mapq)] = alt_m_qual
      mapp = 10^(-mapq / 10)
      
      r = gl(cur_read_set$reads, basep, mapp, cur_read_set$ref, meth)
      
      min_gts = c(min_gts, r[1])
      quals = c(quals, as.numeric(r[2]))
      ref_quals = c(ref_quals, as.numeric(r[3]))
      alt_b_quals = c(alt_b_quals, alt_b_qual)
      alt_m_quals = c(alt_m_quals, alt_m_qual)
      
      alt_m_qual = alt_m_qual - 1 
    }
    alt_b_qual = alt_b_qual - 1
  }
  
  cur_results = data.frame(read_set=cur_read_set$num, ref_base=cur_read_set$ref, ref_type=cur_read_set$ans, genotypes=min_gts, gt_quality=quals, alt_base_quality=alt_b_quals, alt_map_quality=alt_m_quals, ref_quality=ref_quals)
  
  return(cur_results)
}
#####

plotScores <- function(results_df, num, ref, ans){
  p_rq = ggplot(results_df, aes(alt_base_quality, alt_map_quality, z=ref_quality)) +
    geom_raster(aes(fill=genotypes)) +
    scale_fill_manual(name="Genotype",values=c("AA"="#999999","AT"="#d3d3d3")) +
    
    geom_contour(color="#000000", linetype=2) +
    geom_dl(aes(label=..level..), method="bottom.pieces", stat="contour", color="#000000") +
    
    ggtitle(paste("Read set: ", num, "\nReference base:", ref, ans)) +
    labs(x="Alternate allele\nsequencing quality score", y="Alternate allele\nmapping quality score") +
    theme_classic() +
    theme(axis.text=element_text(size=12), 
          axis.title=element_text(size=12), 
          axis.title.y=element_text(margin=margin(t=0,r=0,b=0,l=0),color="black"), 
          axis.title.x=element_text(margin=margin(t=0,r=0,b=0,l=0),color="black"),
          axis.line=element_line(colour='#595959',size=0.75),
          axis.ticks=element_line(colour="#595959",size = 1),
          axis.ticks.length=unit(0.2,"cm"),
          legend.title=element_text(size=12),
          legend.text=element_text(size=12),
          plot.margin=unit(c(0,0.5,1,0), "cm"),
          plot.title = element_text(size=14)
          #panel.background = element_rect(fill="#666666")
    )
  return(p_rq)
}
#####
topScores <- function(df_list, score){
  if(score==40){
    cap="Scores at max base and mapping quality"
  }else if(score==1){
    cap="Scores at min base and mapping quality"
  }else{
    cap=paste("Scores at base and mapping quality = ", score)
  }
  
  scores = data.frame()
  for(i in 1:length(df_list)){
    scores = rbind(scores, subset(df_list[[i]], alt_base_quality==score & alt_map_quality==score))
  }
  kable(scores, "html", caption=cap) %>%
    kable_styling(bootstrap_options=c("striped", "condensed", "responsive"), full_width=F)
}