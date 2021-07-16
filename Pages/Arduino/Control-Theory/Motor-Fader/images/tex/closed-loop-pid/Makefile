
.PHONY: all
all: closed-loop-pid.svg

closed-loop-pid.pdf: closed-loop-pid.tex
	pdflatex --interaction=batchmode closed-loop-pid.tex

build/closed-loop-pid-fonts.pdf: closed-loop-pid.pdf
	mkdir -p build
	gs -dNoOutputFonts -sDEVICE=pdfwrite -o build/closed-loop-pid-fonts.pdf closed-loop-pid.pdf

closed-loop-pid.svg: build/closed-loop-pid-fonts.pdf 
	inkscape build/closed-loop-pid-fonts.pdf -l closed-loop-pid.svg
