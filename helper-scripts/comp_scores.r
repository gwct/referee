#!/usr/bin/env Rscript
############################################################
# For Referee, 10.18
# Compare 2 referee score files
# Gregg Thomas
############################################################

library(ggplot2)
cat("----------\n")

############################################################
# Functions
refReader <- function(filehandle, file_num){
    in_data = read.table(filehandle, header=F, sep="\t")
    if(length(in_data[1,])==3){
    labels = c("score")
    }else if(length(in_data[1,])==5){
    labels = c("score", "cor.base", "cor.score") 
    }else if(length(in_data[1,])==9){
    labels = c("score", "lr", "l.match", "l.mismatch", "ref", "max.gt", "max.gl")
    }else if(length(in_data[1,])==1){
    labels = c("score", "lr", "l.match", "l.mismatch", "ref", "max.gt", "max.gl", "core.base", "core.score")
    }
    labels = c("scaff", "pos", paste(labels, file_num, sep=""))
    names(in_data) = labels
    return(in_data)
}

scoreStats <- function(data){
    print("Calculating mean...")
    mean_score = mean(data$score)
    print(paste("Mean: ", mean_score))
    print("Calculating SD...")
    sd_score = sd(data$score)
    print(paste("SD: ", sd_score))
}

############################################################

#args = commandArgs(trailingOnly=TRUE)
# Command line entry of input files

this.dir <- dirname(parent.frame(2)$ofile)
setwd(this.dir)
args = c("../data/angsd-s1.txt", "../data/pileup-s1.txt", "..", "test-prefix")
# Manual entry of input files

if(length(args) != 4 || "-h" %in% args){
  stop("\n\nUsage: Rscript [referee tabbed output file 1] [referee tabbed output file 2] [output directory] [outfile prefix] [-h]\n\n")
}

scorefile1 = args[1]
if(!file.exists(scorefile1)){
  stop("\n\nInput file not found.\n")
}
print(paste("Input file 1:", scorefile1))

scorefile2 = args[2]
if(!file.exists(scorefile2)){
  stop("\n\nInput file not found.\n")
}
print(paste("Input file 2:", scorefile2))

outdir = args[3]
if(!dir.exists(outdir)){
  stop("\n\nOutput directory not found.\n")
}
print(paste("Output directory:", outdir))
#outfile_prefix = paste(outdir, "/", basename(tools::file_path_sans_ext(args[1])), "-", basename(tools::file_path_sans_ext(args[1])), sep="")
outfile_prefix = paste(outdir, "/", args[4], sep="")
print(paste("Output file prexid:", outfile_prefix))
#dir.create(file.path(getwd(), outdir))

print("---")
print("Reading referee table 1...")
data1 = refReader(scorefile1, "1")
scoreStats(data1)

print("---")
print("Reading referee table 2...")
data2 = refReader(scorefile2, "2")
scoreStats(data2)
 
print("Generating score-v-score plot...")
in_combo = merge(data1, data2, by=c("scaff", "pos"))
comp_p = ggplot(in_combo, aes(x=score1, y=score2)) +
    #geom_smooth(method='glm', color='#333333', fill="#d3d3d3", fullrange=T) +
    #geom_point(color='#333333', size=1) +
    geom_bin2d(bins=94) +
    #scale_fill_gradientn(colors=cm.colors(4)) +
    labs(x=paste(args[1], "score"), y=paste(args[2], "score")) +
    theme_classic() +
    theme(axis.text=element_text(size=10), 
            axis.title=element_text(size=12), 
            axis.title.y=element_text(margin=margin(t=0,r=20,b=0,l=0),color="black"), 
            axis.title.x=element_text(margin=margin(t=20,r=0,b=0,l=0),color="black"),
            axis.line=element_line(colour='#595959',size=0.75),
            axis.ticks=element_line(colour="#595959",size = 1),
            axis.ticks.length=unit(0.2,"cm")
            #legend.position="none"
    )

outfile = paste(outfile_prefix, "-score-v-score.png", sep="")
ggsave(file=outfile, comp_p, width=8, height=6, units="in")
print(comp_p)


