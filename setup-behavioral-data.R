#! /usr/bin/env Rscript
# ================================
# Script 'setup-behavioral-data.R'
# ================================
# This script reads in behavioral data from two psychoacoustics experiments
# (vocoder/reverb) and sets up the data frames for mixed effects modelling.
#
# Author: Dan McCloy <drmccloy@uw.edu>
# License: BSD (3-clause)

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
# SAVE
save(rev_df, rev_df2, voc_df, voc_df2, file=file.path(out_dir, "dfs.RData"))
