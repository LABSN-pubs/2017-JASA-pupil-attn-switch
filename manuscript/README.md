# JASA manuscript
Here we build submittable `.tex` and `.pdf` documents for *The Journal of the
Acoustical Society of America*, from [Markdown][md] source files.  The
`Makefile` uses [pandoc][pd] to convert the markdown source to both a PDF with
inline figures (for reviewer use) and a standalone LaTeX source file with
integrated bibliography and *without* figures (*JASA* requires that figures be
submitted separately and replaced by “[INSERT FIGURE XX ABOUT HERE]” in the
text).  The submittable LaTeX output also pushes all tables to the end of the
document, and appends a list of figure captions.

### Makefile directives

- `make submission` (the default) builds both a submittable standalone LaTeX
source file (`submission-no-figs.tex`) and a compiled PDF (`submission.pdf`),
as described above. Also generates `submission.tex`, the file from which the
PDF was created.
- `make supplement` to make the PDF of supplementary information from
`supplement.md`
- `make coverletter` (supply files `pandoc/author-signature.pdf` and
`pandoc/letterhead-banner.pdf` before using)
- `make response` (response to reviewers; use as needed)
- `make clean` (delete all generated files except figures)
- `make cleanfig` (delete generated figures)

[md]: https://daringfireball.net/projects/markdown/
[pd]: http://pandoc.org/
