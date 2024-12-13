SRCS = $(wildcard src/*.py)
INIT = src/init.sh
DEPENDS = etc/DEPENDENCIES.txt



init:
ifneq ("$(wildcard venv)","")
	bash $(INIT)

else
	python3 -m venv venv
	source venv/bin/activate
	venv/bin/pip3 install -r $(DEPENDS)
	bash $(INIT)
endif

