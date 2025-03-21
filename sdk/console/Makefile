.PHONY: all

all:
	cp ../../LICENSE ../../NOTICE ./
	
	rm -rf src/lib/telepact
	mkdir -p src/lib/telepact
	cp -r ../../lib/ts/dist/* src/lib/telepact

	rm -rf src/lib/prettier-plugin-telepact
	mkdir -p src/lib/prettier-plugin-telepact
	cp -r ../../sdk/prettier-plugin-telepact/dist/* src/lib/prettier-plugin-telepact
	
	npm install	

dev:
	npm run dev

clean:
	rm -rf src/lib/telepact
	rm -rf src/lib/prettier-plugin-telepact
	rm -rf node_modules
	rm -rf LICENSE
	rm -rf NOTICE

test:
	npm run test