run:
	docker build --pull --rm -f 'Dockerfile' -t 'teikotechnicalinterview:latest' '.'
	docker run -p 38080:38080 'teikotechnicalinterview:latest'