
default: build

.PHONY: build
build: 
	make -f Makefile.fa build-fa && \
	       	make -f Makefile.fb build-fb && \
	       	make -f Makefile.mk 
