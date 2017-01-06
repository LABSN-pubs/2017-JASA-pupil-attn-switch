#! /usr/bin/env Rscript
# ================================
# Script 'model-behavioral-data.R'
# ================================
# This script reads in behavioral data from two psychoacoustics experiments
# (vocoder/reverb) and models reaction time with mixed effects regression.
#
# Author: Dan McCloy <drmccloy@uw.edu>
# License: BSD (3-clause)

library(afex)
library(parallel)

# file paths
out_dir <- "models"
log <- file.path(out_dir, "cluster-log-rt.txt")


################################################################################
# LOAD DATA
cat("loading data\n")
load(file.path(out_dir, "dfs.RData"))
# remove dataframes with target-only definition of "truth" from workspace
rm(rev_df2, voc_df2)
# subset to only hits and foil responses
rev_df_targfoil <- rev_df[with(rev_df, !is.na(reax_time) & (targ | foil)),]
voc_df_targfoil <- voc_df[with(voc_df, !is.na(reax_time) & (targ | foil)),]
rev_df_targ     <- rev_df[with(rev_df, !is.na(reax_time) & targ),]
voc_df_targ     <- voc_df[with(voc_df, !is.na(reax_time) & targ),]

################################################################################
# SET UP CLUSTER
invisible(file.remove(log))
cl <- makeForkCluster(nnodes=12, outfile=log)

################################################################################
# FIT MODELS (KENWARD-ROGER APPROXIMATIONS FOR P-VALUES)
# define models
formulae <- list(
    # reverb
    rev_full_model=formula(reax_time ~ reverb*gender*attn + (1|subj)),
    rev_targ_model=formula(reax_time ~ reverb*gender*attn + (1|subj)),
    # vocoder
    voc_full_model=formula(reax_time ~ voc_chan*gap_len*attn + (1|subj)),
    voc_targ_model=formula(reax_time ~ voc_chan*gap_len*attn + (1|subj))
)
datas <- c(list(rev_df_targfoil), list(rev_df_targ), 
           list(voc_df_targfoil), list(voc_df_targ))
stopifnot(length(datas) == length(formulae))
# fit models
cat("fitting reaction time models (Kenward-Roger)\n")
proc.time()
models <- mapply(function(formula_, name, data_source) {
    mod <- mixed(formula_, data=data_source, method="KR", check.contrasts=FALSE, 
                 cl=cl, na.action="na.omit",
                 control=lmerControl(optCtrl=list(maxfun=30000)))
    cat(paste(name, "finished\n"))
    mod
}, formulae, names(formulae), datas)
save(models, file=file.path(out_dir, "rt-models.RData"))
proc.time()


################################################################################
# STOP CLUSTER
stopCluster(cl)
