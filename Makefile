# -.- Makefile -.-

PY = python3
NAME = cf
SRC_FILE = $(NAME).py
SETTINGS_FILE = settings.yaml
SETTINGS_FILE_DIR = .
EXEC_SRC = dist/$(NAME)
EXEC_DEST = /usr/local/bin/$(NAME)
MAKEFILE_PATH = $(abspath $(lastword $(MAKEFILE_LIST)))
MAKEFILE_DIR = $(dir $(MAKEFILE_PATH))

.PHONY: ccreate create copy clean

ccreate: create copy

create: $(SRC_FILE)
	@echo Building executable from $(SRC_FILE)
	@echo
	$(PY) -m PyInstaller \
		--clean \
		--add-data="$(MAKEFILE_DIR)$(SETTINGS_FILE):$(SETTINGS_FILE_DIR)" \
		--onefile \
		$(SRC_FILE)
	@echo done.

copy:
	@echo Copying executable to $(EXEC_DEST)
	sudo cp $(EXEC_SRC) $(EXEC_DEST)
	@echo done.

clean:
	rm *.spec
	rm -r build
	rm -r dist
	rm -r __pycache__