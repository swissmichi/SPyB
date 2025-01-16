SHELL := /bin/bash
SRCS = $(wildcard src/*.py)
INIT = src/init.sh
PYDEPENDS = ./etc/pyDEPENDENCIES.txt
CONFIG = ./etc/config.conf
VENV = ./.venv
VENVACTIVATE = $(VENV)/bin/activate
PIP3 = $(VENV)/bin/pip3
PYTHON = $(VENV)/bin/python3
MAIN = ./src/main.py

install:
ifneq ("$(wildcard venv)","")
	@echo "SPyB is already installed."

else
	@printf "{\n\n}" >> $(CONFIG)
	@echo "Checking shell dependencies"
	@source ./src/checkshdepends.sh
	@echo "Creating a python virtual environment and installing dependencies"
	@python3 -m venv $(VENV)
	@source $(VENVACTIVATE)
	@$(PIP3) install -r $(PYDEPENDS)
	
endif

uninstall:
	@echo "Uninstalling python virtual environment and config files"
	@rm -rf $(VENV)
	@rm -f $(CONFIG)

resetenv:
	@rm -rf $(VENV)
	@echo "Resetting the python virtual environment and reinstalling dependencies"
	@python3 -m venv $(VENV)
	@source $(VENVACTIVATE)
	@$(PIP3) install -r $(PYDEPENDS)

updatelibs:
	@$(PIP3) install -r $(PYDEPENDS)
config:
	@echo "TODO"

configdefaults:
	@rm $(CONFIG)
	@printf "{\n\n}" >> $(CONFIG)
	@echo "Reset configuration back to defaults"

run:
	@$(PYTHON) $(MAIN)