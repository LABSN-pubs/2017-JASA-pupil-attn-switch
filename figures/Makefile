EPS = fig-beh-rev.eps fig-beh-voc.eps fig-beh-rev-rt.eps fig-beh-voc-rt.eps
PDF = fig-trial-rev.pdf fig-trial-voc.pdf pupil-fig-rev.pdf pupil-fig-voc.pdf

all: $(EPS) $(PDF)

fig-beh-%.eps: fig-beh-%.svg
	inkscape -E $(@F) $(<F)

%beh-rev.svg %beh-rev-rt.svg %beh-voc.svg %beh-voc-rt.svg: fig-behavioral.py
	python $(<F)
	rm -f *main*.svg *twoway*.svg *threeway*.svg

fig-trial-%.pdf: fig-trial-%.py
	python $(<F)
	echo "CONVERT TRIAL FIGURES TO EPS IN ILLUSTRATOR TO AVOID RASTERIZATION"

pupil-fig-%.pdf: fig-pupil-%.py
	python $(<F)
	echo "CONVERT PUPIL FIGURES TO EPS IN ILLUSTRATOR TO AVOID RASTERIZATION"

clean:
	rm -f fig*.eps *.svg *.pyc *.ps fig-beh*.pdf
