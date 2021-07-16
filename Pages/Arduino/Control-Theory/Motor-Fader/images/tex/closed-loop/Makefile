
.PHONY: all
all: closed-loop.svg

closed-loop.pdf: closed-loop.tex
	pdflatex --interaction=batchmode closed-loop.tex

build/closed-loop-fonts.pdf: closed-loop.pdf
	mkdir -p build
	gs -dNoOutputFonts -sDEVICE=pdfwrite -o build/closed-loop-fonts.pdf closed-loop.pdf

closed-loop.svg: build/closed-loop-fonts.pdf 
	inkscape build/closed-loop-fonts.pdf -l closed-loop.svg
