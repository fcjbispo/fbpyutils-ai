.PHONY: help venv install build test clean

# Detecta o sistema operacional para usar caminhos adequados
OS := $(shell uname 2>/dev/null || echo Windows_NT)

help:
	@echo "Alvos disponíveis:"
	@echo "  make venv    : Cria o ambiente virtual (.venv) se não existir"
	@echo "  make install : Instala as dependências de desenvolvimento no .venv"
	@echo "  make build   : Compila o projeto (usando hatch build)"
	@echo "  make test    : Executa os testes com pytest"
	@echo "  make clean   : Remove arquivos de build/artefatos de teste"
	@echo ""

venv:
ifeq ($(OS),Windows_NT)
	if not exist .venv (uv venv .venv)
else
	test -d .venv || uv venv .venv
endif

install: venv
ifeq ($(OS),Windows_NT)
	uv pip install --upgrade pip setuptools wheel
	uv pip install -e .[dev]
else
	uv pip install --upgrade pip setuptools wheel
	uv pip install -e .[dev]
endif

build: install
ifeq ($(OS),Windows_NT)
	.venv\Scripts\python -m hatch build
else
	.venv/bin/python -m hatch build
endif

test: install
ifeq ($(OS),Windows_NT)
	.venv\Scripts\python -m dotenv run pytest -s -vv
else
	.venv/bin/python -m dotenv run pytest -s -vv
endif

clean:
	rm -rf dist build .pytest_cache .mypy_cache *.egg-info
