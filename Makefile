dev:
	uv run services/trades/src/trades/main.py

build:
	docker build -t trades:dev -f Docker/trades.dockerfile .