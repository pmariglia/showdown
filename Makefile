docker:
	docker build . -t foul-play:latest --build-arg GEN=$(GEN)

clean_logs:
	rm logs/*

test:
	pytest tests

fmt:
	ruff format

lint:
	ruff check --fix

poke_engine:
	pip uninstall -y poke-engine && pip install -v --force-reinstall --no-cache-dir poke-engine --config-settings="build-args=--features poke-engine/$(GEN) --no-default-features"

# This assumes that the pmariglia/poke-engine repository is in the same directory as foul-play
poke_engine_local:
	pip uninstall -y poke-engine && pip install -v --force-reinstall --no-cache-dir ../poke-engine/poke-engine-py --config-settings="build-args=--features poke-engine/$(GEN) --no-default-features"
