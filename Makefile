.PHONY: run install

PYTHON = ./env/bin/python

run:
	$(PYTHON) main.py

install:
	$(PYTHON) install -r requirements.txt
