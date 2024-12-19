SHELL := /bin/bash
SRCS = $(wildcard src/*.py)
INIT = src/init.sh
PYDEPENDS = ./etc/pyDEPENDENCIES.txt



init:
ifneq ("$(wildcard venv)","")
	@echo "No need to init"

else
	@echo "Checking shell dependencies"
	@source ./src/checkshdepends.sh
	@echo "Creating a python virtual environment and installing dependencies"
	@python3 -m venv venv
	@source ./venv/bin/activate
	@./venv/bin/pip3 install -r $(PYDEPENDS)
	
endif

