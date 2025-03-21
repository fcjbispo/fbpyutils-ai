.PHONY: help venv install build test clean

# Detecta o sistema operacional para usar caminhos adequados
OS := $(shell uname 2>/dev/null || echo Windows_NT)

help:
    @echo "Alvos disponíveis:"
    @echo "  make venv    : Cria o ambiente virtual (.venv) se não existir"
    @echo "  make install : Instala as dependências de desenvolvimento no .venv"
    @echo "  make build   : Compila o projeto (usando uv build)"
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
    .venv\Scripts\uv sync --extra dev
else
    .venv/bin/uv sync --extra dev
endif

build: install
ifeq ($(OS),Windows_NT)
    .venv\Scripts\uv build
else
    .venv/bin/uv build
endif

test: install
ifeq ($(OS),Windows_NT)
    .venv\Scripts\uv run pytest -s -vv
else
    .venv/bin/uv run pytest -s -vv
endif

clean:
    rm -rf dist build .pytest_cache .mypy_cache *.egg-info