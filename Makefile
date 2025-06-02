run:
	docker build --pull --rm -f 'Dockerfile' -t 'teikotechnicalinterview:latest' '.'
	docker run -p 8080:8080 'teikotechnicalinterview:latest'