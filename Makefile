run:
	docker build --pull --rm -f 'Dockerfile' -t 'teikotechnicalinterview:latest' '.'
	docker run -p 38080:38080 'teikotechnicalinterview:latest'

run-and-push-image:
	docker build --pull --rm -f 'Dockerfile' -t 'teikotechnicalinterview:latest' '.'
	docker tag 'teikotechnicalinterview:latest' leopoldmarx/teiko-technical-interview:latest
	docker push leopoldmarx/teiko-technical-interview:latest
	docker run -p 38080:38080 'teikotechnicalinterview:latest'