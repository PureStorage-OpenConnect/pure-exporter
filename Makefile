
default: build

.PHONY: build
build: 
	make -f Makefile.fa build && \
	       	make -f Makefile.fb build&& \
	       	make -f Makefile.mk 
