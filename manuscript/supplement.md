---
title: Supplementary material for “Pupillometry shows the effort of auditory attention switching”
author:
- name: Daniel R. McCloy
- name: Bonnie K. Lau
- name: Eric Larson
- name: Katherine A. I. Pratt
- name: Adrian K. C. Lee
  email: akclee@uw.edu
  affiliation:
  - Institute for Learning and Brain Sciences, University of Washington, 1715 NE Columbia Rd., Box 357988, Seattle, WA, 98195-7988
documentclass: article
classoption: oneside
fontsize: 12pt
geometry:
- letterpaper
- margin=1in
header: Supplement to McCloy et al, Pupillometry and attention switching, JASA
bibliography: bib/switching.bib
csl: bib/jasa-numeric.csl
---

# Repository
Code and data for these experiments are available publicly at
https://github.com/LABSN-pubs/2017-JASA-pupil-attn-switch

# Statistical model specification

In both experiments, separate models were constructed for listener sensitivity
and for reaction time to target/foil items.  Listener sensitivity was modeled
with generalized linear mixed-effects regression with a probit link function,
using packages `afex`[@afex] (version 0.16.1) and `lme4`[@BatesEtAl2015]
(version 1.1.12) in the `R` statistical computing environment.[@R3.3.1]
Reaction time was modeled with linear mixed-effects regression using the same
software.

## Experiment 1

The model for listener sensitivity was constructed to predict probability of
button press at each timing slot.  Binary fixed-effect predictors specified the
trial  parameters (maintain/switch, anechoic/reverberant, and talker gender
match/mismatch), and also included  a categorical indicator variable encoding
whether a target, foil, or neither was present in the timing slot.  A random
intercept was also estimated for each listener.  Mathematically, this model is
represented as in Equation @eq-mod-one:

(@eq-mod-one)  $\Phi^{-1}(y_{ij}) = \beta_0 + \beta_1 T_i + \beta_2 F_i + \beta_3 R_i + \beta_4 G_i + \beta_5 A_i + \beta_6 R_i G_i + \beta_7 R_i A_i + \beta_8 G_i A_i + \beta_9 R_i G_i A_i + \beta_{10} T_i R_i + \beta_{11} T_i G_i + \beta_{12} T_i A_i + \beta_{13} T_i R_i G_i + \beta_{14} T_i R_i A_i + \beta_{15} T_i G_i A_i + \beta_{16} T_i R_i G_i A_i + \beta_{17} F_i R_i + \beta_{18} F_i G_i + \beta_{19} F_i A_i + \beta_{20} F_i R_i G_i + \beta_{21} F_i R_i A_i + \beta_{22} F_i G_i A_i + \beta_{23} F_i R_i G_i A_i + S_{0j} + \epsilon_{ij}$

where $\beta$ terms are the coefficients to be estimated, $T_i$ is the binary
indicator of target presence, $F_i$ is the binary indicator of foil presence,
$R_i$ represents the difference between anechoic and reverberant trials, $G_i$
represents the difference between trials with matching and mismatching talker
genders, $A_i$ represents the difference between maintain- and switch-attention
trials, $S_{0j}$ is the random intercept for subject $j$, and $\epsilon_{ij}$
is the error term.  $\beta_0$ is the grand intercept, $\beta$ terms subscripted
1 through 9 model response bias, and the remaining $\beta$ terms model the
effect of experimental manipulations on response to target and foil items.

Table: Coding of indicator variables in the statistical model for Experiment 1.\label{tab-vars-one}

 **Term**       **Variable**    **Coding**  **Value**
-------------- -------------- ------------- ----------------------------------------------------------------
 $T_i$, $F_i$     `truth`      Treatment    $T_i=1$ if target present, $F_i=1$ if foil present, each 0 otherwise
 $A_i$            `attn`       Deviation    0.5 if maintain-attention trial, −0.5 if switch-attention trial
 $R_i$            `reverb`     Deviation    0.5 if anechoic trial, −0.5 if reverberant trial
 $G_i$            `gender`     Deviation    0.5 if mismatched-gender trial, −0.5 if matched-gender trial

This model is implemented in `R` as `formula(press ~ truth * reverb * gender *
attn + (1|subj))`, where `press` is a binary indicator of whether the listener
pressed the response button; `truth` is a treatment-coded factor variable
indicating whether a target, foil, or neither was present in the timing slot
(with “neither” as baseline); `reverb` is a binary indicator of whether the
trial was anechoic or reverberant; `gender` is a binary indicator of whether
target and masker voices were both male (“MM”) or male target and female masker
(“MF”); `attn` is a binary indicator of whether listeners were cued to maintain
or switch attention between talkers at the mid-trial gap; and `subj` is an
indicator variable for the identity of the listener.  Deviation coding was used
with all three of the experimental manipulations (`attn`, `reverb`, and
`gender`).

\include{exp-one-table}

## Experiment 2

As in Experiment 1, the model for listener sensitivity was constructed to
predict probability of button press at each timing slot.  Binary fixed-effect
predictors specified the trial  parameters (maintain/switch, 10/20 channel
vocoding, and 200/600 ms mid-trial switch gap duration), and also included a
categorical indicator variable encoding whether a target, foil, or neither was
present in the timing slot.  A random intercept was also estimated for each
listener.  Mathematically, this model is represented as in Equation
@eq-mod-two:

(@eq-mod-two)  $\Phi^{-1}(y_{ij}) = \beta_0 + \beta_1 T_i + \beta_2 F_i + \beta_3 V_i + \beta_4 G_i + \beta_5 A_i + \beta_6 V_i G_i + \beta_7 V_i A_i + \beta_8 G_i A_i + \beta_9 V_i G_i A_i + \beta_{10} T_i V_i + \beta_{11} T_i G_i + \beta_{12} T_i A_i + \beta_{13} T_i V_i G_i + \beta_{14} T_i V_i A_i + \beta_{15} T_i G_i A_i + \beta_{16} T_i V_i G_i A_i + \beta_{17} F_i V_i + \beta_{18} F_i G_i + \beta_{19} F_i A_i + \beta_{20} F_i V_i G_i + \beta_{21} F_i V_i A_i + \beta_{22} F_i G_i A_i + \beta_{23} F_i V_i G_i A_i + S_{0j} + \epsilon_{ij}$

where $\beta$ terms are the coefficients to be estimated, $T_i$ is the binary
indicator of target presence, $F_i$ is the binary indicator of foil presence,
$V_i$ represents the difference between 20- and 10-channel vocoder trials, $G_i$
represents the difference between trials with matching and mismatching talker
genders, $A_i$ represents the difference between maintain- and switch-attention
trials, $S_{0j}$ is the random intercept for subject $j$, and $\epsilon_{ij}$
is the error term.  $\beta_0$ is the grand intercept, $\beta$ terms subscripted
1 through 9 model response bias, and the remaining $\beta$ terms model the
effect of experimental manipulations on response to target and foil items.

Table: Coding of indicator variables in the statistical model for Experiment 2.\label{tab-vars-two}

 **Term**       **Variable**    **Coding**  **Value**
-------------- -------------- ------------- ----------------------------------------------------------------
 $T_i$, $F_i$     `truth`      Treatment    $T_i=1$ if target present, $F_i=1$ if foil present, each 0 otherwise
 $A_i$            `attn`       Deviation    0.5 if maintain-attention trial, −0.5 if switch-attention trial
 $V_i$            `voc_chan`   Deviation    0.5 if 20-channel trial, −0.5 if 10-channel trial
 $G_i$            `gap_len`    Deviation    0.5 if long-gap trial, −0.5 if short-gap trial

This model is implemented in `R` as `formula(press ~ truth * voc_chan * gap_len *
attn + (1|subj))`, where `press` is a binary indicator of whether the listener
pressed the response button; `truth` is a treatment-coded factor variable
indicating whether a target, foil, or neither was present in the timing slot
(with “neither” as baseline); `voc_chan` is a binary indicator of whether the
trial was processed with 10- or 20-channel noise vocoding; `gap_len` is a
binary indicator of mid-trial gap duration (200 or 600 ms); `attn` is a binary
indicator of whether listeners were cued to maintain or switch attention
between talkers at the mid-trial gap; and `subj` is an indicator variable for
the identity of the listener.  Deviation coding was used with all three of the
experimental manipulations (`attn`, `voc_chan`, and `gap_len`).

# References
\setlength{\parindent}{-0.25in}
\setlength{\leftskip}{0.25in}
\noindent
