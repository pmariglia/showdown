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

# Used to install poke-engine for specific generations
# This assumes that the poke-engine project is in the same directory as foul-play
gen1:
	pip uninstall -y poke-engine && pip install -v --force-reinstall --no-cache-dir ../poke-engine/poke-engine-py --config-settings="build-args=--features poke-engine/gen1 --no-default-features"

gen2:
	pip uninstall -y poke-engine && pip install -v --force-reinstall --no-cache-dir ../poke-engine/poke-engine-py --config-settings="build-args=--features poke-engine/gen2 --no-default-features"

gen3:
	pip uninstall -y poke-engine && pip install -v --force-reinstall --no-cache-dir ../poke-engine/poke-engine-py --config-settings="build-args=--features poke-engine/gen3 --no-default-features"

gen4:
	pip uninstall -y poke-engine && pip install -v --force-reinstall --no-cache-dir ../poke-engine/poke-engine-py --config-settings="build-args=--features poke-engine/gen4 --no-default-features"

gen5:
	pip uninstall -y poke-engine && pip install -v --force-reinstall --no-cache-dir ../poke-engine/poke-engine-py --config-settings="build-args=--features poke-engine/gen5 --no-default-features"

gen6:
	pip uninstall -y poke-engine && pip install -v --force-reinstall --no-cache-dir ../poke-engine/poke-engine-py --config-settings="build-args=--features poke-engine/gen6 --no-default-features"

gen7:
	pip uninstall -y poke-engine && pip install -v --force-reinstall --no-cache-dir ../poke-engine/poke-engine-py --config-settings="build-args=--features poke-engine/gen7 --no-default-features"

gen8:
	pip uninstall -y poke-engine && pip install -v --force-reinstall --no-cache-dir ../poke-engine/poke-engine-py --config-settings="build-args=--features poke-engine/gen8 --no-default-features"

gen9:
	pip uninstall -y poke-engine && pip install -v --force-reinstall --no-cache-dir ../poke-engine/poke-engine-py --config-settings="build-args=--features poke-engine/terastallization --no-default-features"
