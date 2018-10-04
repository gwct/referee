############################################################
# For qtip, 09.18
# Small analysis of qtip output
# Gregg Thomas
############################################################

library(ggplot2)
#this.dir <- dirname(parent.frame(2)$ofile)
#setwd(this.dir)
cat("----------\n")

#in_data = read.table("qtip-r-test.txt", header=F)
in_data = read.table("qtip-returns.txt", header=F)
names(in_data) = c("scaff", "pos", "score")
#in_data = in_data[which(in_data$score!=-9999&in_data$score!=-9998&in_data$score!=9999),]
#in_data = in_data[which(in_data$score>=-100&in_data$score<=1200),]


print("Calculating mean...")
mean_score = mean(in_data$score)
print(paste("Mean: ", mean_score))
print("Calculating SD...")
sd_score = sd(in_data$score)
print(paste("SD: ", sd_score))
print("Generating histogram...")

score_p = ggplot(in_data, aes(x=score)) +
  geom_histogram(binwidth=1, fill="#d3d3d3", color="#000000") +
  geom_vline(xintercept = mean(in_data$score), color="#999999", size=1, linetype="dashed") +
  geom_vline(xintercept = mean_score + sd_score, color="#999999", size=1, linetype="dotted") +
  geom_vline(xintercept = mean_score - sd_score, color="#999999", size=1, linetype="dotted") +
  geom_vline(xintercept = mean_score + (2*sd_score), color="#999999", size=0.5, linetype="dotted") +
  geom_vline(xintercept = mean_score - (2*sd_score), color="#999999", size=0.5, linetype="dotted") +
  labs(x="Qtip score", y="# of sites") +
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
#print(score_p)
ggsave(file="qtip-hist.png", score_p, width=8, height=6, units="in")