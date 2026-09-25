.PHONY: config build docker labs lab00 labsdown smoke check lab-up lab-test lab-reset lab-down experiment

config:
	$(MAKE) -C configure
	./configure/bin/configure

build:
	$(MAKE) -C configure
	$(MAKE) -C lab00/server
	$(MAKE) -C lab00/client

docker:
	docker compose build

labs:
	docker compose up -d --build

lab00:
	docker compose up -d --build server-00 client-00

labsdown:
	docker compose down -v

smoke:
	python3 scripts/smoke.py

check:
	python3 -m unittest discover -s tests
	python3 scripts/checkgetconfig.py
	cd configure && go test ./...
	cd oalib && go test ./...
	cd lab00/server && go test ./...
	cd lab00/client && go test ./...

lab-up:
	@test -n "$(LAB)" || (echo "Use LAB=00 (two digits)"; exit 1)
	docker compose up -d --build server-$(LAB) client-$(LAB)

lab-test:
	@test -n "$(LAB)" || (echo "Use LAB=00 (two digits)"; exit 1)
	python3 scripts/smoke.py --lab $(LAB)

lab-down:
	docker compose down

lab-reset:
	docker compose down -v

experiment:
	@test -n "$(LAB)" || (echo "Use LAB=01 (two digits)"; exit 1)
	python3 scripts/run_experiment.py --lab $(LAB)
