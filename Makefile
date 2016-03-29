all: web pre sub
web: makeweb cleanweb
sub: makesub cleansub
pre: makepre cleanpre

.PHONY: linkeps linkpdf cleanweb cleansub cleanall cleancommon

makeweb: bib/switching.bib manuscript.tex pandoc/latex-postprocessor.py linkpdf
	python pandoc/latex-postprocessor.py manuscript.tex McCloyEtAl-pupil-switching-manuscript.tex
	xelatex McCloyEtAl-pupil-switching-manuscript.tex
	bibtex8 McCloyEtAl-pupil-switching-manuscript.aux
	xelatex McCloyEtAl-pupil-switching-manuscript.tex
	xelatex McCloyEtAl-pupil-switching-manuscript.tex
	xelatex McCloyEtAl-pupil-switching-manuscript.tex

makesub: bib/switching.bib submission.tex pandoc/latex-postprocessor.py pandoc/latex-make-standalone.py linkeps
	python pandoc/latex-postprocessor.py -s submission.tex submission-temp.tex
	pdflatex submission-temp.tex
	bibtex8 submission-temp.aux
	python ./pandoc/latex-make-standalone.py submission-temp.tex McCloyEtAl-pupil-switching.tex
	pdflatex McCloyEtAl-pupil-switching.tex
	pdflatex McCloyEtAl-pupil-switching.tex
	pdflatex McCloyEtAl-pupil-switching.tex

makepre: bib/switching.bib prepress.tex pandoc/latex-postprocessor.py linkpdf
	python pandoc/latex-postprocessor.py prepress.tex McCloyEtAl-pupil-switching-prepress.tex
	xelatex McCloyEtAl-pupil-switching-prepress.tex
	bibtex8 McCloyEtAl-pupil-switching-prepress.aux
	xelatex McCloyEtAl-pupil-switching-prepress.tex
	xelatex McCloyEtAl-pupil-switching-prepress.tex
	xelatex McCloyEtAl-pupil-switching-prepress.tex

manuscript.tex: manuscript/manuscript.md bib/manuscript-numeric.bst pandoc/template-JASA-manuscript.tex makefigs
	ln -sf bib/manuscript-numeric.bst pupil-switching.bst
	pandoc --filter pandoc-eqnos --natbib --no-tex-ligatures --template=pandoc/template-JASA-manuscript.tex --output=manuscript.tex manuscript.md

submission.tex: manuscript.md bib/jasa-submission.bst pandoc/template-JASA-submission.tex figures/fig-1.eps figures/fig-2.eps figures/fig-3.eps
	ln -sf bib/jasa-submission.bst pupil-switching.bst
	pandoc --filter pandoc-eqnos --natbib --template=pandoc/template-JASA-submission.tex --output=submission.tex manuscript.md

prepress.tex: manuscript.md bib/jasa-submission.bst pandoc/template-JASA-prepress.tex makefigs
	ln -sf bib/jasa-submission.bst pupil-switching.bst
	pandoc --filter pandoc-eqnos --natbib --template=pandoc/template-JASA-prepress.tex --output=prepress.tex manuscript.md

bib/manuscript-numeric.bst: bib/manuscript-numeric.dbj bib/bst-patcher.py
	cd bib; tex manuscript-numeric.dbj
	cd bib; python bst-patcher.py manuscript-numeric-unpatched.bst manuscript-numeric.bst 
	cd bib; rm manuscript-numeric-unpatched.bst manuscript-numeric.log

bib/jasa-submission.bst: bib/jasa-submission.dbj bib/bst-patcher.py
	cd bib; tex jasa-submission.dbj
	cd bib; python bst-patcher.py jasa-submission-unpatched.bst jasa-submission.bst 
	cd bib; rm jasa-submission-unpatched.bst jasa-submission.log

makefigs: figures/fig-1.pdf figures/fig-placeholder.pdf

figures/fig-%.pdf: figures/fig-%.py
	cd $(<D); python $(<F)

linkeps:
	for fig in $(EPSFIGS); do ln -sf "$$fig"; done

linkpdf:
	for fig in $(PDFFIGS); do ln -sf "$$fig"; done

cleanweb: cleancommon
	rm -f fig-*.pdf *manuscript.tex
	bn="McCloyEtAl-pupil-switching-manuscript"; for ext in $(TEXEXTS); do rm -f "$$bn.$$ext"; done

cleansub: cleancommon
	rm -f *.eps *-eps-converted-to.pdf submission.tex submission-temp.tex submission-temp.pdf
	bn="submission-temp"; for ext in $(TEXEXTS); do rm -f "$$bn.$$ext"; done
	bn="McCloyEtAl-pupil-switching"; for ext in $(TEXEXTS); do rm -f "$$bn.$$ext"; done

cleanpre: cleancommon
	rm -f fig-*.pdf *prepress.tex
	bn="McCloyEtAl-pupil-switching-prepress"; for ext in $(TEXEXTS); do rm -f "$$bn.$$ext"; done

cleancommon:
	rm -f pupil-switching.bst

clean: cleanweb cleansub cleanpre
	rm -f McCloyEtAl-pupil-switching.pdf McCloyEtAl-pupil-switching-manuscript.pdf $(EPSFIGS) $(PDFFIGS)

EPSFIGS = figures/*.eps

PDFFIGS = figures/*.pdf

TEXEXTS = bbl aux ent fff log lof lol lot toc blg out pyg ttt
