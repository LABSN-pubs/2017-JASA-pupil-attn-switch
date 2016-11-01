EPS = fig-beh-rev.eps fig-beh-voc.eps fig-beh-rev-rt.eps fig-beh-voc-rt.eps \
fig-placeholder.eps  # fig-trial-rev.eps fig-trial-voc.eps

.SECONDARY:

all: $(EPS) ;

fig-beh-%.eps: fig-beh-%.svg
	inkscape -E $(@F) $(<F)

%beh-rev.svg %beh-rev-rt.svg %beh-voc.svg %beh-voc-rt.svg: fig-behavioral.py
	python $(<F)
	rm -f *main*.svg *twoway*.svg *threeway*.svg

# fig-trial-%.eps: fig-trial-%.ps
# 	ps2eps -f $(<F)

fig-trial-%.pdf: fig-trial-%.py
	python $(<F)
	echo "CONVERT TRIAL FIGURES TO EPS IN ILLUSTRATOR TO AVOID RASTERIZATION"

fig-placeholder.eps: fig-placeholder.py
	python $(<F)

pupil-fig-%.pdf: fig-pupil-%.py
	python $(<F)
	echo "CONVERT PUPIL FIGURES TO EPS IN ILLUSTRATOR TO AVOID RASTERIZATION"

pdfs:
	for fig in fig-beh*.eps; do inkscape -A $$(basename $$fig eps)pdf $$fig; done

clean:
	rm -f fig*.eps *.svg *.pyc *.ps fig-beh*.pdf
