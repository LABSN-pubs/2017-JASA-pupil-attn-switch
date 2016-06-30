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
library(lme4)
library(dotwhisker)
# library(stringi)
# library(ez)

# file paths
data_dir <- "data-behavioral"
out_dir <- "models"
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
rev_df <- read.delim(rev_fname, sep="\t", colClasses=rev_cols)
voc_df <- read.delim(voc_fname, sep="\t", colClasses=voc_cols)


################################################################################
# SET FACTOR CONTRASTS
# treatment contrasts
txContrast <- function(x, ...) {
    x <- factor(x, ...)
    contrasts(x) <- contr.treatment
    colnames(contrasts(x)) <- paste0("_", levels(x)[-1])
    x
}

# sum-to-one (deviation contrasts)
devContrast <- function(x, ...) {
    x <- factor(x, ...)
    contrasts(x) <- contr.sum
    contrasts(x) <- contrasts(x) / 2
    colnames(contrasts(x)) <- paste0("_", levels(x)[-length(levels(x))])
    x
}

# common variables
makeFactors <- function(df) {
    df <- within(df, {
        # truth
        truth <- ifelse(targ, "target", ifelse(foil, "foil", "neither"))
        truth <- txContrast(truth, levels=c("neither", "target", "foil"))
        # attn
        attn <- devContrast(attn, levels=c("maint.", "switch"))
        # slot
        slot <- slot + 1  # reset to 1-indexed instead of 0-indexed
        slot <- txContrast(as.character(slot), levels=c("1", "2", "3", "4"))
    })
    df
}
rev_df <- makeFactors(rev_df)
voc_df <- makeFactors(voc_df)

# experiment-specific variables
rev_df <- within(rev_df, {
    reverb <- devContrast(reverb, levels=c("anech.", "reverb"))
    gender <- devContrast(gender, levels=c("MF", "MM"))
})
voc_df <- within(voc_df, {
    voc_chan <- devContrast(voc_chan, levels=c("20", "10"))
    gap_len <- devContrast(gap_len, levels=c("long", "short"))
})

# redefine "truth" to be just target & non-target (don't model foils)
rev_df2 <- rev_df
voc_df2 <- voc_df
rev_df2$truth <- txContrast(rev_df2$targ, levels=c(FALSE, TRUE),
                            labels=c("non-target", "target"))
voc_df2$truth <- txContrast(voc_df2$targ, levels=c(FALSE, TRUE),
                            labels=c("non-target", "target"))

# make sure factor creation didn't generate NAs
invisible(within(rev_df, {
    for (var in c(reverb, gender, attn, slot)) stopifnot(all(!is.na(var)))
}))
invisible(within(rev_df2, {
    for (var in c(reverb, gender, attn, slot)) stopifnot(all(!is.na(var)))
}))
invisible(within(voc_df, {
    for (var in c(voc_chan, gap_len, attn, slot)) stopifnot(all(!is.na(var)))
}))
invisible(within(voc_df2, {
    for (var in c(voc_chan, gap_len, attn, slot)) stopifnot(all(!is.na(var)))
}))


################################################################################
# DEFINE MODELS
formulae <- list(
	# reverb
    rev_null_model=formula(press ~ truth + (1|subj)),
    rev_full_model=formula(press ~ truth*reverb*gender*attn + (1|subj)),
    rev_slot_model=formula(press ~ truth*reverb*gender*attn + truth*attn*slot + (1|subj)),
    rev_rdux_model=formula(press ~ truth*reverb*gender*attn + truth:attn:slot + (1|subj)),
    rev_slot_only_model=formula(press ~ truth*attn*slot + (1|subj)),
    # reverb w/o foils
    rev_targ_model=formula(press ~ truth*reverb*gender*attn + (1|subj)),
    rev_targ_slot_model=formula(press ~ truth*reverb*gender*attn + truth*attn*slot + (1|subj)),
    # vocoder
    voc_null_model=formula(press ~ truth + (1|subj)),
    voc_full_model=formula(press ~ truth*voc_chan*gap_len*attn + (1|subj)),
    voc_slot_model=formula(press ~ truth*voc_chan*gap_len*attn + truth*attn*slot*gap_len + (1|subj)),
    voc_rdux_model=formula(press ~ truth*voc_chan*gap_len*attn + truth:attn:slot:gap_len + (1|subj)),
    voc_slot_only_model=formula(press ~ truth*attn*slot*gap_len + (1|subj)),
    # vocoder w/o foils
    voc_targ_model=formula(press ~ truth*voc_chan*gap_len*attn + (1|subj)),
    voc_targ_slot_model=formula(press ~ truth*voc_chan*gap_len*attn + truth*attn*slot*gap_len + (1|subj))
)
datas <- c(rep(list(rev_df), 5), rep(list(rev_df2), 2), 
           rep(list(voc_df), 5), rep(list(voc_df2), 2))
stopifnot(length(datas) == length(formulae))


################################################################################
# FIT MODELS
cat("fitting models\n")
models <- mcmapply(function(formula_, name, data_source) {
    mod <- glmer(formula_, data=data_source, family=binomial(link="probit"),
                 control=glmerControl(optCtrl=list(maxfun=30000)))
    cat(paste(name, "finished\n"))
    mod
    }, formulae, names(formulae), datas)
save(models, file=file.path(out_dir, "all-models.RData"))


################################################################################
# SORT MODELS BY CONVERGENCE
# valid
converged <- models[sapply(models, function(i) {
    is.null(i@optinfo$conv$lme4$code)
})]

# invalid
why_nonconverged <- sapply(models, function(i) {
    ifelse(is.null(i@optinfo$conv$lme4$code), NA,
           list(i@optinfo$conv$lme4$messages))
})
why_nonconverged <- why_nonconverged[!is.na(why_nonconverged)]
sink(file.path(out_dir, "convergence-failures.txt"))
print(why_nonconverged)
sink()

# split by experiment
converged_rev <- converged[substr(names(converged), 1, 3) %in% "rev"]
converged_voc <- converged[substr(names(converged), 1, 3) %in% "voc"]


stop()
################################################################################
# COEFPLOTS
dwplot(models[c("rev_full_model", "rev_targ_model", "rev_targ_slot_model")])
dwplot(models[c("voc_full_model", "voc_targ_model", "voc_targ_slot_model")])

#plot_rev <- dwplot(converged_rev) + theme_bw()
#plot_voc <- dwplot(converged_voc) + theme_bw()
#save(plot_rev, plot_voc, file=file.path(out_dir, "coefplots.Rdata"))


################################################################################
# LEFTOVERS
# aggregate
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

