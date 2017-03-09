EXTS = bbl aux ent fff log lof lol lot toc blg out pyg ttt

.PHONY: link_bib link_figs link_subm_template cleantex clean upload

submission: link_subm_template _subm cleantex

manuscript.tex: manuscript.md bib/jasa-submission.bst template.tex
	pandoc --natbib --number-sections --no-tex-ligatures \
	--template=template.tex --output=manuscript.tex manuscript.md

_subm: manuscript.tex link_bib link_figs
	python pandoc/latex-postprocessor.py manuscript.tex cleanms.tex
	pdflatex cleanms.tex
	bibtex cleanms.aux
	python pandoc/latex-make-standalone.py cleanms.tex submission.tex
	python pandoc/latex-suppress-figures.py submission.tex \
	submission-no-figs.tex
	pdflatex submission.tex
	pdflatex submission.tex
	pdflatex submission.tex

supplement:
	pandoc --filter pandoc-citeproc --no-tex-ligatures --latex-engine=xelatex \
	--template=pandoc/template-supplement.tex  --number-sections \
	--output=supplement.pdf supplement.md

response:
	pandoc --no-tex-ligatures --latex-engine=xelatex --number-sections \
	--template=pandoc/template-plain.tex \
	--output=review/response-to-reviewers.pdf \
	review/response-to-reviewers.md

coverletter:
	pandoc --no-tex-ligatures --latex-engine=xelatex \
	--template=pandoc/template-ilabs-letterhead.tex \
	--output=cover-letter/cover-letter.pdf cover-letter/cover-letter.md

link_subm_template:
	ln -sf pandoc/template-JASA-submission.tex template.tex

link_figs:
	cd ../figures && $(MAKE)
	for fig in ../figures/*.eps; do ln -sf "$$fig"; done

link_bib:
	ln -sf bib/jasa-submission.bst bibstyle.bst

cleantex:
	rm -f *.eps *-eps-converted-to.pdf
	rm -f bibstyle.bst template.tex manuscript.tex
	for ext in $(EXTS); do rm -f "submission.$$ext"; done
	for ext in tex $(EXTS); do rm -f "manuscript-prepress.$$ext"; done
	for ext in tex pdf $(EXTS); do rm -f "cleanms.$$ext"; done

cleanfigs:
	cd ../figures && $(MAKE) clean

clean: cleantex
	rm -f manuscript.pdf manuscript.tex submission.pdf submission.tex \
	submission-no-figs.tex manuscript-prepress.pdf

upload:
	mkdir -p upload
	cp submission-no-figs.tex upload/Manuscript.tex
	cp submission.pdf upload/ManuscriptWithInlineFigures.pdf
	cp supplement.pdf upload/SuppPub1.pdf
	cp review/response-to-reviewers.pdf upload/Rebuttal.pdf
	cp ../figures/fig-trial-rev.eps upload/Figure1.eps
	cp ../figures/fig-beh-rev.eps upload/Figure2.eps
	cp ../figures/fig-beh-rev-rt.eps upload/Figure3.eps
	cp ../figures/pupil-fig-rev.eps upload/Figure4.eps
	cp ../figures/fig-trial-voc.eps upload/Figure5.eps
	cp ../figures/fig-beh-voc.eps upload/Figure6.eps
	cp ../figures/fig-beh-voc-rt.eps upload/Figure7.eps
	cp ../figures/pupil-fig-voc.eps upload/Figure8.eps
