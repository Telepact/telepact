.PHONY: all

all:
	cp ../cli/dist/msgpact_cli-*.tar.gz msgpact_cli.tar.gz
	
	docker build --progress=plain --no-cache -f Dockerfile -t msgpact-mock:latest .

dev:
	docker-compose up --build

test:
	bash test.sh

clean:
	rm -f msgpact_cli.tar.gz
	docker-compose rm -f
	docker rmi msgpact-mock