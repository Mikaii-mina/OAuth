.PHONY: config build docker labs lab00 labsdown

config:
	$(MAKE) -C configure
	./configure/bin/configure

build:
	$(MAKE) -C configure
	$(MAKE) -C lab00/server
	$(MAKE) -C lab00/client

docker:
	docker compose build

labs lab00:
	docker compose up -d --build

labsdown:
	docker compose down -v
