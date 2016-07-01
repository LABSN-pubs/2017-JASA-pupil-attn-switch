#! /usr/bin/env Rscript
# ================================
# Script 'model-behavioral-data.R'
# ================================
# This script reads in behavioral data from two psychoacoustics experiments
# (vocoder/reverb) and models the conditions with mixed effects regression.
#
# Author: Dan McCloy <drmccloy@uw.edu>
# License: BSD (3-clause)

library(afex)
library(parallel)
options(mc.cores=10)

# file paths
data_dir <- "data-behavioral"
out_dir <- "models"
log <- file.path(out_dir, "cluster-log.txt")


################################################################################
# LOAD DATA
load(file.path(out_dir, "dfs.RData"))
# remove dataframes with target-only definition of "truth" from workspace
rm(rev_df2, voc_df2)


################################################################################
# SET UP CLUSTER
file.remove(log)
cl <- makeForkCluster(nnodes=10, outfile=log)

################################################################################
# REVERB EXPERIMENT
form <- formula(press ~ truth*reverb*gender*attn + (1|subj))
rev_mod <- mixed(form, data=rev_df, family=binomial(link="probit"),
                 method="LRT", check.contrasts=FALSE, cl=cl,
                 control=glmerControl(optCtrl=list(maxfun=30000)))


################################################################################
# VOCODER EXPERIMENT
form <- formula(press ~ truth*voc_chan*gap_len*attn + (1|subj))
voc_mod <- mixed(form, data=voc_df, family=binomial(link="probit"),
                 method="LRT", check.contrasts=FALSE, cl=cl,
                 control=glmerControl(optCtrl=list(maxfun=30000)))

save(rev_mod, voc_mod, file=file.path(out_dir, "afex_models.RData"))

################################################################################
# DEFINE MODELS
# formulae <- list(
#     # reverb
#     rev_full_model=formula(press ~ truth*reverb*gender*attn + (1|subj)),
#     # vocoder
#     voc_full_model=formula(press ~ truth*voc_chan*gap_len*attn + (1|subj))
# )
# datas <- c(list(rev_df), list(voc_df))
# stopifnot(length(datas) == length(formulae))


################################################################################
# FIT MODELS
# afex_models <- mapply(function(formula_, name, data_source) {
#     mod <- mixed(formula_, data=data_source, family=binomial(link="probit"),
#                  method="LRT", check.contrasts=FALSE, cl=cl,
#                  #args.test=list(nsim=10, cl=cl, seed=1234),
#                  control=glmerControl(optCtrl=list(maxfun=30000)))
#     cat(paste(name, "finished\n"))
#     mod
# }, formulae, names(formulae), datas)
# save(afex_models, file=file.path(out_dir, "afex-models.RData"))


################################################################################
# STOP CLUSTER
stopCluster(cl)
