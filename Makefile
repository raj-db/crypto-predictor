#Runs the trades services as a standalone python app (Not Dockerized)
dev:
	uv run services/${service}/src/${service}/main.py
	
#################################################################
##development
#################################################################	

build-for-dev:
	docker build -t ${service}:dev -f Docker/${service}.dockerfile .

push-for-dev:
	kind load docker-image ${service}:dev --name rwml-34fa

deploy-for-dev: build-for-dev push-for-dev
	kubectl delete -f deployments/dev/${service}/${service}.yaml --ignore-not-found=true
	kubectl apply -f deployments/dev/${service}/${service}.yaml

lint:
	ruff check . --fix

#################################################################
##production
#################################################################

build-and-push-for-prod:
	docker buildx build --platform linux/amd64 -t ghcr.io/${service}:prod -f Docker/${service}.dockerfile . --push





