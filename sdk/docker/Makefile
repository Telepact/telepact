.PHONY: all

all:
	cp ../cli/dist/telepact_cli-*.tar.gz telepact_cli.tar.gz
	
	docker build --progress=plain --no-cache -f Dockerfile -t telepact-mock:latest .

dev:
	docker-compose up --build

test:
	bash test.sh

clean:
	rm -f telepact_cli.tar.gz
	docker-compose rm -f
	docker rmi telepact-mock