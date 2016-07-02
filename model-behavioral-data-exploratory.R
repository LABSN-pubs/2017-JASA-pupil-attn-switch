#! /usr/bin/env Rscript
# ============================================
# Script 'model-behavioral-data-exploratory.R'
# ============================================
# This script reads in behavioral data from two psychoacoustics experiments
# (vocoder/reverb) and models the conditions with mixed effects regression.
#
# Author: Dan McCloy <drmccloy@uw.edu>
# License: BSD (3-clause)

library(lme4)
library(parallel)
options(mc.cores=10)

# file paths
data_dir <- "data-behavioral"
out_dir <- "models"


################################################################################
# LOAD DATA
load(file.path(out_dir, "dfs.RData"))


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
save(models, file=file.path(out_dir, "exploratory-models.RData"))


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


################################################################################
# SAVE SUMMARIES TO FILE
invisible(mapply(function(m, n) {
    sink(file.path(out_dir, paste0(n, ".txt")))
    print(summary(m))
    sink()
}, converged, names(converged)))


################################################################################
# DIAGNOSTICS
# should we keep the model that explicitly accounts for response to foils?
anova(models$rev_full_model, models$rev_targ_model)
#                       Df    AIC    BIC  logLik deviance  Chisq Chi Df Pr(>Chisq)
# models$rev_targ_model 17 9669.4 9804.1 -4817.7   9635.4                             
# models$rev_full_model 25 9636.9 9835.0 -4793.4   9586.9 48.501      8  7.924e-08 ***
# ---
# Signif. codes:  0 ‘***’ 0.001 ‘**’ 0.01 ‘*’ 0.05 ‘.’ 0.1 ‘ ’ 1

anova(models$voc_full_model, models$voc_targ_model)
#                       Df   AIC   BIC  logLik deviance  Chisq Chi Df Pr(>Chisq)
# models$voc_targ_model 17 17953 18088 -8959.7    17919                             
# models$voc_full_model 25 17234 17432 -8592.0    17184 735.38      8  < 2.2e-16 ***
# ---
# Signif. codes:  0 ‘***’ 0.001 ‘**’ 0.01 ‘*’ 0.05 ‘.’ 0.1 ‘ ’ 1
