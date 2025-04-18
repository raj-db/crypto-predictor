dev:
	uv run services/trades/src/trades/main.py

build:
	docker build -t trades:dev -f Docker/trades.dockerfile .

push:
	kind load docker-image trades:dev --name rwml-34fa

deploy: build push
