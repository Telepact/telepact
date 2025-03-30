LIB_TAR_GZ := ../../sdk/console/dist/*.tgz
TAR_GZ := telepact-console.tgz

all: $(TAR_GZ)
	npm install
	npm run build

$(TAR_GZ):
	cp $(LIB_TAR_GZ) $(TAR_GZ)

clean:
	rm -rf dist
	rm -rf node_modules
	rm $(TAR_GZ)

test:
	npm run test