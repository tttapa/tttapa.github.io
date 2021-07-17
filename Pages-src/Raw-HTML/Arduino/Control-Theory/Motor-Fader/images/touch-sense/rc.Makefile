.PHONY: all
all: rc.svg

rc.svg: rc.py 
	python3 rc.py