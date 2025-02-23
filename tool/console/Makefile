.PHONY: all

all:
	cp ../../LICENSE ../../NOTICE ./
	rm -rf src/lib/uapi
	mkdir -p src/lib/uapi
	cp -r ../../lib/ts/dist/* src/lib/uapi
	npm install	
