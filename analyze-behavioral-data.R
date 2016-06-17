#! /usr/bin/env Rscript
# =======================================
# Script 'voc/rev behavioral mixed model'
# =======================================
# This script reads in behavioral data from two psychoacoustics experiments
# (vocoder/reverb) and models the conditions with mixed effects regression.
#
# Author: Dan McCloy <drmccloy@uw.edu>
# License: BSD (3-clause)

library(stringi)
library(lme4)
library(ez)

parse_py_list <- function(str) {
    if (str == "[]") return(NA)
    else {
        str <- stri_replace_all_fixed(str, pattern="[", replacement="")
        str <- stri_replace_all_fixed(str, pattern="]", replacement="")
        str <- stri_split_fixed(str, pattern=", ", simplify=TRUE)
        return(as.numeric(str))
    }
}

data_dir <- "data-behavioral"
rev_fname <- file.path(data_dir, "rev-behdata-longform.tsv")
voc_fname <- file.path(data_dir, "voc-behdata-longform.tsv")

rev <- read.delim(rev_fname, sep="\t",
                  colClasses=c(subj="numeric", block="numeric", trial="numeric",
                               t_start="numeric", t_audio="numeric",
                               t_resp_check="numeric", t_done="numeric",
                               is_training="numeric", run_index="numeric",
                               band="numeric", cue_1u_2d="numeric",
                               maint1_switch2="numeric", hits="numeric",
                               misses="numeric", false_alarms="numeric",
                               reax_times="character"))

voc <- read.delim(voc_fname, sep="\t",
                  colClasses=c(subj="numeric", block="numeric", trial="numeric",
                               t_start="numeric", t_audio="numeric",
                               t_resp_check="numeric", t_done="numeric",
                               is_training="numeric", run_index="numeric",
                               band="numeric", cue_1u_2d="numeric",
                               maint1_switch2="numeric", hits="numeric",
                               misses="numeric", false_alarms="numeric",
                               reax_times="character"))

rev$reax_times <- lapply(rev$reax_times, parse_py_list)
rev$reverb <- c("10"=TRUE, "20"=FALSE)[as.character(rev$band)]
rev$attn <- c("1"="maint", "2"="switch")[as.character(rev$maint1_switch2)]
rev$gender <- c("1"="MM", "2"="MF")[as.character(rev$cue_1u_2d)]
rev$corr_rej <- 4 - rev$hits - rev$false_alarms
columns <- c("subj", "block", "trial", "run_index", "attn", "gender", "reverb",
             "hits", "misses", "false_alarms", "corr_rej", "reax_times")
rev <- rev[columns]


voc$reax_times <- lapply(voc$reax_times, parse_py_list)
voc$attn <- c("1"="maint", "2"="switch")[as.character(voc$maint1_switch2)]
voc$bands <- as.character(voc$band)
voc$gap_len <- c("1"="short", "2"="long")[as.character(voc$cue_1u_2d)]
voc$corr_rej <- 4 - voc$hits - voc$false_alarms
columns <- c("subj", "block", "trial", "run_index", "attn", "gap_len", "bands",
             "hits", "misses", "false_alarms", "corr_rej", "reax_times")
voc <- voc[columns]




stop()
mm_zero <- glmer(press ~ (1|subj),
                 data=wl, family=binomial(link="probit"),
                 control=glmerControl(optCtrl=list(maxfun=20000)))
mm_null <- glmer(press ~ truth + (1|subj),
                 data=wl, family=binomial(link="probit"),
                 control=glmerControl(optCtrl=list(maxfun=20000)))
#relgrad <- with(mm_null@optinfo$derivs, solve(Hessian, gradient))
#print(max(abs(relgrad)))




## aggregate
agg_cols <- c("hits", "misses", "false_alarms", "corr_rej")
by_cols_rev <- c("subj", "attn", "reverb", "gender")
by_cols_voc <- c("subj", "attn", "bands", "gap_len")
keep_cols_rev <- c(by_cols_rev, agg_cols, "reax_times")  # "block", "trial",
keep_cols_voc <- c(by_cols_voc, agg_cols, "reax_times")  # "block", "trial",
rev2 <- rev[keep_cols_rev]
voc2 <- voc[keep_cols_voc]
rev_agg <- aggregate(rev2[agg_cols], by=rev2[by_cols_rev], FUN=sum, simplify=TRUE)
voc_agg <- aggregate(voc2[agg_cols], by=voc2[by_cols_voc], FUN=sum, simplify=TRUE)

## dprime
rev_agg$hitrate <- with(rev_agg, (hits + 0.5) / (hits + misses + 1))
rev_agg$fa_rate <- with(rev_agg, (false_alarms + 0.5) / (false_alarms + corr_rej + 1))
rev_agg$dprime <- with(rev_agg, qnorm(hitrate)-qnorm(fa_rate))

voc_agg$hitrate <- with(voc_agg, (hits + 0.5) / (hits + misses + 1))
voc_agg$fa_rate <- with(voc_agg, (false_alarms + 0.5) / (false_alarms + corr_rej + 1))
voc_agg$dprime <- with(voc_agg, qnorm(hitrate)-qnorm(fa_rate))

# ANOVAs
anova_rev <- ezANOVA(data=rev_agg, dv=dprime, wid=subj, within=list(attn, reverb, gender))
anova_voc <- ezANOVA(data=voc_agg, dv=dprime, wid=subj, within=list(attn, bands, gap_len))

## barplot
bars_rev <- aggregate(rev_agg["dprime"], by=rev_agg[c("attn", "reverb", "gender")],
                      FUN=mean, simplify=TRUE)
sd_rev <- aggregate(rev_agg["dprime"], by=rev_agg[c("attn", "reverb", "gender")],
                    FUN=sd, simplify=TRUE)
bars_rev$upper <- bars_rev$dprime + sd_rev$dprime / (length(unique(rev_agg$subj)) - 1)
bars_rev$lower <- bars_rev$dprime - sd_rev$dprime / (length(unique(rev_agg$subj)) - 1)
rev_x <- barplot(bars_rev$dprime, ylim=c(0, max(bars_rev$upper)))
Hmisc::errbar(rev_x, y=bars_rev$dprime, yplus=bars_rev$upper, yminus=bars_rev$lower,
              add=TRUE, xpd=TRUE)

