.PHONY: all

all:
	cp ../../LICENSE ../../NOTICE ./
	
	rm -rf src/lib/msgpact
	mkdir -p src/lib/msgpact
	cp -r ../../lib/ts/dist/* src/lib/msgpact

	rm -rf src/lib/prettier-plugin-msgpact
	mkdir -p src/lib/prettier-plugin-msgpact
	cp -r ../../tool/prettier-plugin-msgpact/dist/* src/lib/prettier-plugin-msgpact
	
	npm install	

dev:
	npm run dev

clean:
	rm -rf src/lib/msgpact
	rm -rf src/lib/prettier-plugin-msgpact
	rm -rf node_modules
	rm -rf LICENSE
	rm -rf NOTICE

test:
	npm run test