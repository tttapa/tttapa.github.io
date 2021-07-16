
.PHONY: all
all: closed-loop-pid-time.svg

closed-loop-pid-time.pdf: closed-loop-pid-time.tex
	pdflatex --interaction=batchmode closed-loop-pid-time.tex

build/closed-loop-pid-time-fonts.pdf: closed-loop-pid-time.pdf
	mkdir -p build
	gs -dNoOutputFonts -sDEVICE=pdfwrite -o build/closed-loop-pid-time-fonts.pdf closed-loop-pid-time.pdf

closed-loop-pid-time.svg: build/closed-loop-pid-time-fonts.pdf 
	inkscape build/closed-loop-pid-time-fonts.pdf -l closed-loop-pid-time.svg
