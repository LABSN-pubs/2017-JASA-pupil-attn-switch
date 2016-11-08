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
biblio-style: bibstyle
bibliography: bib/switching
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
represented as in Equation @eq-mod-one

(@eq-mod-one)  $\Phi^{-1}(y_{ij}) = \beta_0 + \beta_1 T_i + \beta_2 F_i + \beta_3 A_i + \beta_4 R_i + \beta_5 G_i + \beta_6 A_i R_i + \beta_7 A_i G_i + \beta_8 R_i G_i + \beta_9 A_i R_i G_i + \beta_10 T_i A_i + \beta_11 T_i R_i + \beta_12 T_i G_i + \beta_13 T_i A_i R_i + \beta_14 T_i A_i G_i + \beta_15 T_i R_i G_i + \beta_16 T_i A_i R_i G_i + \beta_17 F_i A_i + \beta_18 F_i R_i + \beta_19 F_i G_i + \beta_20 F_i A_i R_i + \beta_21 F_i A_i G_i + \beta_22 F_i R_i G_i + \beta_23 F_i A_i R_i G_i + S_{0j} + \epsilon_{ij}$

where $\beta$ terms are the coefficients to be estimated, $T_i$ is the binary
indicator of target presence, $F_i$ is the binary indicator of foil presence,
$A_i$ represents the difference between maintain- and switch-attention trials,
$R_i$ represents the difference between anechoic and reverberant trials, $G_i$
represents the difference between trials with matching and mismatching talker
genders, $S_{0j}$ is the random intercept for subject $j$, and $\epsilon_{ij}$
is the error term.  $\beta_0$ is the grand intercept, $\beta$ terms subscripted
1 through 9 model response bias, and the remaining $\beta$ terms model the
effect of experimental manipulations on response to target and foil items.

Table: Coding of indicator variables in the statistical model for Experiment 1.\label{tab-one}

**Variable**   **Coding**    **Indicator**  **Coef. name**  **Value**
-------------- ------------- -------------- --------------- -----------------------------------------------------------------------------------------------------
`truth`        Treatment     $T_i$          `target`        1 if target present, 0 otherwise
                             $F_i$          `foil`          1 if foil present, 0 otherwise
`attn`         Deviation     $A_i$          `maint.`        0.5 if maintain-attention trial, −0.5 if switch-attention trial
`reverb`       Deviation     $R_i$          `anech.`        0.5 if anechoic trial, −0.5 if reverberant trial
`gender`       Deviation     $G_i$          `MF`            0.5 if mismatched-gender trial, −0.5 if matched-gender trial

This model is implemented in `R` as `formula(press ~ truth * reverb * gender *
attn + (1|subj))`, where `press` is a binary indicator of whether the listener
pressed the response button; `truth` is a treatment-coded factor variable
indicating whether a target, foil, or neither was present in the timing slot
(with “neither” as baseline); `reverb` is a binary indicator of whether the
trial was anechoic or reverberant; `gender` is a binary indicator of whether
target and masker voices were both male (“match”) or male target and female
masker (“mismatch”); and `attn` is a binary indicator of whether listeners were
cued to maintain or switch attention between talkers at the mid-trial gap; and
`subj` is an indicator variable for the identity of the listener.  Deviation
coding was used with all three of the experimental manipulations (`attn`,
`reverb`, and `gender`).

Table: Summary of model of listener sensitivity for Experiment 1

\begin{landscape}
\begin{tabular}{ @{}l S[round-mode=places,round-precision=2] S[round-mode=places,round-precision=2] S[round-mode=places,round-precision=2] S[round-mode=places,round-precision=3,table-format=>1.3e2] l c l c S[round-mode=places,round-precision=2] c S[round-mode=places,round-precision=3,table-format=>1.3e2] l }
\toprule
	\multicolumn{6}{c}{\bfseries Model summary}                                                                                                  & & \multicolumn{6}{c}{\bfseries Likelihood ratio tests}                                                                                                                                                       \\ \cmidrule{1-6}\cmidrule{8-13}
	                      & \multicolumn{1}{c}{Estimate} & \multicolumn{1}{c}{SE} & \multicolumn{1}{c}{Wald $z$} & \multicolumn{1}{c}{$p$} &     & &                                           & Model DF            & \multicolumn{1}{c}{$\Chi^2$}           & \multicolumn{1}{c}{$\Chi^2$ DF} & \multicolumn{1}{c}{$p$}                &                      \\ \cmidrule{2-6}\cmidrule{9-13}
	\bfseries{Baseline response levels}                  &                        &                              &                         &     & &                                           &                     &                                        &                                 &                                        &                      \\
	(Intercept)           & -1.84487                     & 3.6409999999999998E-2  & -50.67                       & < 2e-16                 & *** & &                                           &                     &                                        &                                 &                                        &                      \\
	target                & 2.9882200000000001           & 3.1329999999999997E-2  & 95.38                        & < 2e-16                 & *** & & truth                                     & 23                  & 15831.0098                             & 2                               & < 2.2e-16                              & ***                  \\
	foil                  & 0.20899000000000001          & 4.3650000000000001E-2  & 4.79                         & 1.68E-6                 & *** & &                                           &                     &                                        &                                 &                                        &                      \\ \midrule
	\textbf{Bias}         &                              &                        &                              &                         &     & &                                           &                     &                                        &                                 &                                        &                      \\
	anech                 & -6.4130000000000006E-2       & 4.8259999999999997E-2  & -1.33                        & 0.18387000000000001     &     & & reverb                                    & 24                  & 1.7674000000000001                     & 1                               & 0.18370300000000001                    &                      \\
	MF                    & -2.7820000000000001E-2       & 4.8259999999999997E-2  & -0.57999999999999996         & 0.56435000000000002     &     & & gender                                    & 24                  & 0.33250000000000002                    & 1                               & 0.56420000000000003                    &                      \\
	maint                 & -0.12399                     & 4.827E-2               & -2.57                        & 1.0200000000000001E-2   & *   & & attn                                      & 24                  & 6.6296999999999997                     & 1                               & 1.0029E-2                              & *                    \\
	anech:MF              & 7.1360000000000007E-2        & 9.6490000000000006E-2  & 0.74                         & 0.45956999999999998     &     & & reverb:gender                             & 24                  & 0.54669999999999996                    & 1                               & 0.45964899999999997                    &                      \\
	anech:maint           & -0.11957                     & 9.6519999999999995E-2  & -1.24                        & 0.21540000000000001     &     & & reverb:attn                               & 24                  & 1.5347                                 & 1                               & 0.21541299999999999                    &                      \\
	MF:maint              & 9.6000000000000002E-2        & 9.6509999999999999E-2  & 0.99                         & 0.31990000000000002     &     & & gender:attn                               & 24                  & 0.99009999999999998                    & 1                               & 0.31970999999999999                    &                      \\
	anech:MF:maint        & 0.10349999999999999          & 0.19309999999999999    & 0.54                         & 0.59199000000000002     &     & & reverb:gender:attn                        & 24                  & 0.28749999999999998                    & 1                               & 0.59185100000000002                    &                      \\ \midrule
	\textbf{Sensitivity}  &                              &                        &                              &                         &     & &                                           &                     &                                        &                                 &                                        &                      \\
	target:anech          & 0.19162999999999999          & 6.2260000000000003E-2  & 3.08                         & 2.0799999999999998E-3   & **  & & \multirow{2}{*}{truth:reverb}             & \multirow{2}{*}{23} & \multirow{2}{*}{\tablenum{13.5388}}               & \multirow{2}{*}{2}              & \multirow{2}{*}{\tablenum{1.1479999999999999E-3}} & \multirow{2}{*}{**}  \\
	foil:anech            & -4.3459999999999999E-2       & 8.7230000000000002E-2  & -0.5                         & 0.61829999999999996     &     & &                                           &                     &                                        &                                 &                                        &                      \\ \cmidrule{2-13}
	target:MF             & 0.15112999999999999          & 6.2260000000000003E-2  & 2.4300000000000002           & 1.521E-2                & *   & & \multirow{2}{*}{truth:gender}             & \multirow{2}{*}{23} & \multirow{2}{*}{\tablenum{19.7987}}               & \multirow{2}{*}{2}              & \multirow{2}{*}{\tablenum{5.0210000000000002E-5}} & \multirow{2}{*}{***} \\
	foil:MF               & -0.20177                     & 8.7239999999999998E-2  & -2.31                        & 2.0729999999999998E-2   & *   & &                                           &                     &                                        &                                 &                                        &                      \\ \cmidrule{2-13}
	target:maint          & 0.32596000000000003          & 6.2269999999999999E-2  & 5.23                         & 1.6500000000000001E-7   & *** & & \multirow{2}{*}{truth:attn}               & \multirow{2}{*}{23} & \multirow{2}{*}{\tablenum{27.9634}}               & \multirow{2}{*}{2}              & \multirow{2}{*}{\tablenum{8.4689999999999999E-7}} & \multirow{2}{*}{***} \\
	foil:maint            & 0.24589                      & 8.7230000000000002E-2  & 2.82                         & 4.8199999999999996E-3   & **  & &                                           &                     &                                        &                                 &                                        &                      \\ \cmidrule{2-13}
	target:anech:MF       & -0.26063999999999998         & 0.12449                & -2.09                        & 3.6290000000000003E-2   & *   & & \multirow{2}{*}{truth:reverb:gender}      & \multirow{2}{*}{23} & \multirow{2}{*}{\tablenum{11.2568}}               & \multirow{2}{*}{2}              & \multirow{2}{*}{\tablenum{3.594E-3}}              & \multirow{2}{*}{**}  \\
	foil:anech:MF         & 0.25575999999999999          & 0.17433999999999999    & 1.47                         & 0.14235999999999999     &     & &                                           &                     &                                        &                                 &                                        &                      \\ \cmidrule{2-13}
	target:anech:maint    & -1.0630000000000001E-2       & 0.12451                & -0.09                        & 0.93194999999999995     &     & & \multirow{2}{*}{truth:reverb:attn}        & \multirow{2}{*}{23} & \multirow{2}{*}{\tablenum{5.0315000000000003}}    & \multirow{2}{*}{2}              & \multirow{2}{*}{\tablenum{8.0800999999999998E-2}} &                      \\
	foil:anech:maint      & 0.34648000000000001          & 0.17444999999999999    & 1.99                         & 4.7019999999999999E-2   & *   & &                                           &                     &                                        &                                 &                                        &                      \\ \cmidrule{2-13}
	target:MF:maint       & 2.9899999999999999E-2        & 0.12452000000000001    & 0.24                         & 0.81020999999999999     &     & & \multirow{2}{*}{truth:gender:attn}        & \multirow{2}{*}{23} & \multirow{2}{*}{\tablenum{5.9200000000000003E-2}} & \multirow{2}{*}{2}              & \multirow{2}{*}{\tablenum{0.97082900000000005}}   &                      \\
	foil:MF:maint         & 1.167E-2                     & 0.17443                & 7.0000000000000007E-2        & 0.94665999999999995     &     & &                                           &                     &                                        &                                 &                                        &                      \\ \cmidrule{2-13}
	target:anech:MF:maint & -0.39857                     & 0.24903                & -1.6                         & 0.10949                 &     & & \multirow{2}{*}{truth:reverb:gender:attn} & \multirow{2}{*}{23} & \multirow{2}{*}{\tablenum{2.6375000000000002}}    & \multirow{2}{*}{2}              & \multirow{2}{*}{\tablenum{0.26747100000000001}}   &                      \\
	foil:anech:MF:maint   & -0.32568000000000003         & 0.34899999999999998    & -0.93                        & 0.35072999999999999     &     & &                                           &                     &                                        &                                 &                                        &                      \\ \bottomrule
\end{tabular}
\end{landscape}

<!-- **** -->

## Experiment 2

# Post-hoc analyses

## Experiment 1

## Experiment 2
