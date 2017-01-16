# Figures

Figure generation is (mostly) managed by the `Makefile`, which is called
automatically from the makefile in `../manuscript` when generating the
manuscript.

The pupillometry plots and trial schematic diagrams both contain
semi-transparent lines and/or color fills, which cannot be represented in EPS
format. Consequently, all figures are generated as SVG, and those with
transparency are converted to EPS manually using Adobe Illustrator, which
(unlike all other conversion tools I'm aware of) does not rasterize regions of
the figure involving transparency.  Instead, it appears to split the
semi-transparent shape along lines of intersection with objects it occludes,
and compute an equivalent opaque color for each sub-region so as to give the
illusion of transparency.

This limitation of EPS figures is an excellent reason to abandon EPS as the
standard vector graphics format for publications.  Tell your journal editors to
start accepting SVG and/or PDF graphics!
