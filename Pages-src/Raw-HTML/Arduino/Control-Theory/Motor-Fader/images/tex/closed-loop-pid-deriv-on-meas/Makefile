
.PHONY: all
all: closed-loop-pid-deriv-on-meas.svg

closed-loop-pid-deriv-on-meas.pdf: closed-loop-pid-deriv-on-meas.tex
	pdflatex --interaction=batchmode closed-loop-pid-deriv-on-meas.tex

build/closed-loop-pid-deriv-on-meas-fonts.pdf: closed-loop-pid-deriv-on-meas.pdf
	mkdir -p build
	gs -dNoOutputFonts -sDEVICE=pdfwrite -o build/closed-loop-pid-deriv-on-meas-fonts.pdf closed-loop-pid-deriv-on-meas.pdf

closed-loop-pid-deriv-on-meas.svg: build/closed-loop-pid-deriv-on-meas-fonts.pdf 
	inkscape build/closed-loop-pid-deriv-on-meas-fonts.pdf -l closed-loop-pid-deriv-on-meas.svg
