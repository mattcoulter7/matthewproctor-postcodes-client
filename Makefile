default: help
ifeq ($(OS),Windows_NT)
SHELL := C:/Progra~1/Git/bin/bash.exe
else
SHELL := /bin/bash
endif


.PHONY: help
help: # Show help for each of the Makefile recipes.
	@grep -E '^[a-zA-Z0-9 -]+:.*#'  Makefile | sort | while read -r l; do printf "\033[1;32m$$(echo $$l | cut -f 1 -d':')\033[00m:$$(echo $$l | cut -f 2- -d'#')\n"; done


.PHONY: install
install: # Install required dependencies on bare metal.
	uv sync --refresh


.PHONY: format
format: # Run the formatter on bare metal.
	uv run ruff format .
	uv run ruff check --fix .


.PHONY: lint
lint: # Run the linter on bare metal.
	uv run ruff format --check .
	uv run ruff check .


.PHONY: test
test: # Run unit tests on bare metal.
	uv run pytest -vv
