#! /usr/bin/env Rscript
# =======================================
# Script 'voc/rev behavioral mixed model'
# =======================================
# This script reads in behavioral data from two psychoacoustics experiments
# (vocoder/reverb) and models the conditions with mixed effects regression.
#
# Author: Dan McCloy <drmccloy@uw.edu>
# License: BSD (3-clause)

library(parallel)
library(stringi)
library(lme4)
library(ez)

# file paths
data_dir <- "data-behavioral"
rev_fname <- file.path(data_dir, "rev-behdata-xlongform.tsv")
voc_fname <- file.path(data_dir, "voc-behdata-xlongform.tsv")
# data types
common_cols <- c(subj="integer", block="integer", trial="integer",
                 run_index="integer", attn="character", hit="logical",
                 miss="logical", fals="logical", crej="logical", frsp="logical",
                 slot="integer", attn_lett="character", mask_lett="character",
                 targ="logical", foil="logical", press="logical", 
                 onset="numeric", press_time="numeric", reax_time="numeric")
# add in the experiment-specific variables
rev_cols <- c(common_cols, reverb="character", gender="character")
voc_cols <- c(common_cols, voc_chan="character", gap_len="character")
# read in data
rev <- read.delim(rev_fname, sep="\t", colClasses=rev_cols)
voc <- read.delim(voc_fname, sep="\t", colClasses=voc_cols)

# SET FACTOR CONTRASTS
# treatment
txContrast <- function(x, ...) {
    x <- factor(x, ...)
    contrasts(x) <- contr.treatment
    colnames(contrasts(x)) <- paste0("_", levels(x)[-1])
    x
}
# sum-to-one
sumContrast <- function(x, ...) {
    x <- factor(x, ...)
    stopifnot(length(levels(x)) == 2)
    contrasts(x) <- contr.sum
    contrasts(x) <- contrasts(x) * 0.5
    colnames(contrasts(x)) <- paste0("_", levels(x)[1])
    x
}
# common variables
makeFactors <- function(df) {
    df <- within(df, {
        # truth
        truth <- ifelse(targ, "target", ifelse(foil, "foil", "neither"))
        truth <- txContrast(truth, levels=c("neither", "target", "foil"))
        # attn
        attn <- sumContrast(attn, levels=c("maint.", "switch"))
        # half
        half <- 1 + as.integer(slot > 1)
        half <- sumContrast(as.character(half), levels=c("1", "2"))
        # slot
        slot <- txContrast(as.character(slot), levels=c("0", "1", "2", "3"))
    })
    df
}
rev <- makeFactors(rev)
voc <- makeFactors(voc)
# experiment-specific variables
rev <- within(rev, {
    reverb <- sumContrast(reverb, levels=c("anech.", "reverb"))
    gender <- sumContrast(gender, levels=c("MF", "MM"))
})
voc <- within(voc, {
    voc_chan <- sumContrast(voc_chan, levels=c("20", "10"))
    gap_len <- sumContrast(gap_len, levels=c("long", "short"))
})
# make sure factor creation didn't generate NAs
invisible(within(rev, {
    for (var in c(reverb, gender, attn, slot, half)) stopifnot(all(!is.na(var)))
}))
invisible(within(voc, {
    for (var in c(voc_chan, gap_len, attn, slot, half)) stopifnot(all(!is.na(var)))
}))


# MODELS: REVERB
# set up formulae to be tested
formulae <- list(
    null_model=formula(press ~ truth + (1|subj)),
    full_model=formula(press ~ truth*reverb*gender*attn + attn*slot + (1|subj)),
    half_model=formula(press ~ truth*reverb*gender*attn + attn*half + (1|subj))
)
# fit models
rev_models <- mapply(function(formula_, name) {
    mod <- glmer(formula_, data=rev, family=binomial(link="probit"),
                 control=glmerControl(optCtrl=list(maxfun=25000)))
    cat(paste("reverb", name, "finished\n"))
    mod
    }, formulae, names(formulae))


# MODELS: VOCODER
# set up formulae to be tested
formulae <- list(
    null_model=formula(press ~ truth + (1|subj)),
    full_model=formula(press ~ truth*voc_chan*gap_len*attn + attn*slot*gap_len
                       + (1|subj))
)
# fit models
voc_models <- mapply(function(formula_, name) {
    mod <- glmer(formula_, data=voc, family=binomial(link="probit"),
                 control=glmerControl(optCtrl=list(maxfun=25000)))
    cat(paste("vocoder", name, "finished\n"))
    mod
    }, formulae, names(formulae))


stop()

# COEFPLOTS
library(dotwhisker)
library(ggplot2)
revplot <- dwplot(rev_models$full_model) + theme_bw()
vocplot <- dwplot(voc_models$full_model) + theme_bw()
comboplot <- dwplot(list(reverb=rev_models$full_model,
                         vocoder=voc_models$full_model)) + theme_bw()

stop()

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

