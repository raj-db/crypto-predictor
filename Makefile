dev:
	uv run services/trades/src/trades/main.py
	

build:
	docker build -t trades:dev -f Docker/trades.dockerfile .

push:
	kind load docker-image trades:dev --name rwml-34fa

deploy: build push
	kubectl delete -f deployments/dev/trades/trades.yaml
	kubectl apply -f deployments/dev/trades/trades.yaml

lint:
	ruff check . --fix
