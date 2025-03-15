.PHONY: all clean

all:
	rm -rf inc
	mkdir -p inc
	cp ../../common/*.json inc
	rm -rf dist
	mkdir -p dist
	cp ../../LICENSE ../../NOTICE dist
	npm install
	npm run build

clean:
	rm -rf inc
	rm -rf dist
	rm -rf node_modules
	rm -f dist/LICENSE dist/NOTICE