EPS = fig-trial-rev.eps fig-trial-voc.eps fig-beh-rev.eps fig-beh-voc.eps \
fig-beh-rev-rt.eps fig-beh-voc-rt.eps fig-placeholder.eps

all: $(EPS)

fig-trial-%.eps: fig-trial-%.ps
	ps2eps -f $(<F)

fig-trial-%.ps: fig-trial-%.py
	python $(<F)

fig-beh-%.eps: fig-beh-%.svg
	inkscape -E $(@F) $(<F)

%beh-rev.svg %beh-rev-rt.svg %beh-voc.svg %beh-voc-rt.svg: fig-behavioral.py
	python $(<F)
	rm -f *main*.svg *twoway*.svg *threeway*.svg

fig-placeholder.eps: fig-placeholder.py
	python $(<F)

pupil-fig-%.pdf: fig-pupil-%.py
	python $(<F)
	echo "UPDATE PUPIL FIGURES IN ILLUSTRATOR TO AVOID RASTERIZATION"

clean:
	rm -f fig*.eps *.svg *.ps
