#!/usr/bin/env Rscript
############################################################
# For qtip, 09.18
# Small analysis of Referee output
# Gregg Thomas
############################################################

library(ggplot2)
cat("----------\n")

args = commandArgs(trailingOnly=TRUE)
# Command line entry of input files

#this.dir <- dirname(parent.frame(2)$ofile)
#setwd(this.dir)
#args = c("../data/om-scaff/JYKP02038398.1-out.txt", "../data/om-scaff/plots/", "../data/om-scaff/39093-JYKP02038398.1.pileup")
# Manual entry of input files

if(!length(args) %in% c(2,3) || "-h" %in% args){
  stop("\n\nUsage: Rscript [referee tabbed output file (required)] [output directory (required)] [genome pileup file (optional)]  [-h]\n\n")
}

infile = args[1]
if(!file.exists(infile)){
  stop("\n\nInput file not found.\n")
}
print(paste("Input file:", infile))

outdir = args[2]
if(!dir.exists(outdir)){
  stop("\n\nOutput directory not found.\n")
}
print(paste("Output directory:", outdir))
outfile_prefix = paste(outdir, "/", basename(tools::file_path_sans_ext(args[1])), sep="")
print(paste("Output file prexid:", outfile_prefix))
#dir.create(file.path(getwd(), outdir))

if(length(args)==3){
  pileupfile = args[3]
  if(!file.exists(pileupfile)){
    stop("\n\nPileup file not found.\n")
  }
  print(paste("Pileup file:", pileupfile))
}


print("---")
print("Reading referee table...")
in_data = read.table(infile, header=F, sep="\t")
if(length(in_data[1,])==3){
  names(in_data) = c("scaff", "pos", "score")
}else if(length(in_data[1,])==5){
  names(in_data) = c("scaff", "pos", "score", "cor.base", "cor.score") 
}else if(length(in_data[1,])==9){
  names(in_data) = c("scaff", "pos", "score", "lr", "l.match", "l.mismatch", "ref", "max.gt", "max.gl")
}else if(length(in_data[1,])==1){
  names(in_data) = c("scaff", "pos", "score", "lr", "l.match", "l.mismatch", "ref", "max.gt", "max.gl", "core.base", "core.score")
}

#print("Setting barplot option...")
#if(length(args>=2)){
#  barp = args[2]
#}

print("Calculating mean...")
mean_score = mean(in_data$score)
print(paste("Mean: ", mean_score))
print("Calculating SD...")
sd_score = sd(in_data$score)
print(paste("SD: ", sd_score))

print("Generating score histogram...")
score_p = ggplot(in_data, aes(x=score)) +
  geom_histogram(binwidth=1, fill="#d3d3d3", color="#000000") +
  geom_vline(xintercept = mean(in_data$score), color="#999999", size=1, linetype="dashed") +
  geom_vline(xintercept = mean_score + sd_score, color="#999999", size=1, linetype="dotted") +
  geom_vline(xintercept = mean_score - sd_score, color="#999999", size=1, linetype="dotted") +
  geom_vline(xintercept = mean_score + (2*sd_score), color="#999999", size=0.5, linetype="dotted") +
  geom_vline(xintercept = mean_score - (2*sd_score), color="#999999", size=0.5, linetype="dotted") +
  labs(x="Referee score", y="# of sites") +
  theme_classic() +
  theme(axis.text=element_text(size=10), 
        axis.title=element_text(size=12), 
        axis.title.y=element_text(margin=margin(t=0,r=20,b=0,l=0),color="black"), 
        axis.title.x=element_text(margin=margin(t=20,r=0,b=0,l=0),color="black"),
        axis.line=element_line(colour='#595959',size=0.75),
        axis.ticks=element_line(colour="#595959",size = 1),
        axis.ticks.length=unit(0.2,"cm"),
        legend.position="none"
  )

outfile = paste(outfile_prefix, "-score-hist.png", sep="")
ggsave(file=outfile, score_p, width=8, height=6, units="in")

if(length(args)==3){
  print("Reading pileup...")
  pileup_data = read.table(pileupfile, header=F, sep="\t", quote="", comment="", colClasses=c("character", "integer", "character", "integer", "character", "character"))
  names(pileup_data) = c("scaff", "pos", "base", "depth", "reads", "qual")
  
  print("Generating score-v-depth plot...")
  in_combo = merge(in_data, pileup_data, by=c("scaff", "pos"))
  depth_p = ggplot(in_combo, aes(x=score, y=depth)) +
    #geom_smooth(method='glm', color='#333333', fill="#d3d3d3", fullrange=T) +
    geom_point(color='#333333', size=0.5) +
    ylim(0, NA) +
    labs(x="Referee score", y="Depth") +
    theme_classic() +
    theme(axis.text=element_text(size=10), 
          axis.title=element_text(size=12), 
          axis.title.y=element_text(margin=margin(t=0,r=20,b=0,l=0),color="black"), 
          axis.title.x=element_text(margin=margin(t=20,r=0,b=0,l=0),color="black"),
          axis.line=element_line(colour='#595959',size=0.75),
          axis.ticks=element_line(colour="#595959",size = 1),
          axis.ticks.length=unit(0.2,"cm"),
          legend.position="none"
    )
  
  outfile = paste(outfile_prefix, "-score-v-depth.png", sep="")
  ggsave(file=outfile, depth_p, width=8, height=6, units="in")
}

# print("Generating barplots...")
# if(barp){
#   rm(score_p, depth_p,pileup_data)
#   scaff_scores = split(in_data, in_data[,"scaff"])
#   rm(in_data)
#   for(df in scaff_scores){
#     outfile = paste(outdir, "/", df[1,1], "-scores.png", sep="")
#     print(outfile)
#     png(outfile)
#     barplot(df$score, names.arg=df$pos, ylim=c(-2,92), xlab="Position", ylab="Score", border=NA, space=0)
#     #axis(1,at=bp,labels=df$pos)
#     dev.off()
    
#     #bar_p = ggplot(df, aes(x=pos, y=score)) +
#     #  geom_bar(stat="identity") +
#     #  labs(x="Position", y="Referee score") +
#     #  theme_classic() +
#     #  theme(axis.text=element_text(size=10), 
#     #        axis.title=element_text(size=12), 
#     #        axis.title.y=element_text(margin=margin(t=0,r=20,b=0,l=0),color="black"), 
#     #        axis.title.x=element_text(margin=margin(t=20,r=0,b=0,l=0),color="black"),
#     #        axis.line=element_line(colour='#595959',size=0.75),
#     #        axis.ticks=element_line(colour="#595959",size = 1),
#     #        axis.ticks.length=unit(0.2,"cm"),
#     #        legend.position="none"
#     #  )
#     #ggsave(file=outfile, bar_p, width=8, height=6, units="in")
#   }
  
# }
