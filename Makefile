dev:
	uv run services/${service}/src/${service}/main.py
	

build:
	docker build -t ${service}:dev -f Docker/${service}.dockerfile .

push:
	kind load docker-image ${service}:dev --name rwml-34fa

deploy: build push
	kubectl delete -f deployments/dev/${service}/${service}.yaml --ignore-not-found
	kubectl apply -f deployments/dev/${service}/${service}.yaml

lint:
	ruff check . --fix
