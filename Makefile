RAYFORCE_GITHUB = git@github.com:singaraiona/rayforce.git
EXEC_DIR = $(shell pwd)

# For now, only supports MacOS
COMPILED_LIB_NAME = librayforce.dylib

pull_from_gh:
	@rm -rf $(EXEC_DIR)/tmp/rayforce-c && \
	echo "⬇️  Cloning rayforce repo from GitHub..."; \
	git clone $(RAYFORCE_GITHUB) $(EXEC_DIR)/tmp/rayforce-c && \
	cp -r $(EXEC_DIR)/tmp/rayforce-c/core $(EXEC_DIR)/raypy/core


shared:
	@cd $(EXEC_DIR)/tmp/rayforce-c/ && make shared && cd $(EXEC_DIR) && \
	cp $(EXEC_DIR)/tmp/rayforce-c/$(COMPILED_LIB_NAME) $(EXEC_DIR)/raypy/


lib:
	python3 setup.py build_ext --inplace


clean:
	@echo "🧹 Cleaning cache and generated files..."
	@cd $(EXEC_DIR) && rm -rf \
		raypy/_rayforce.c*.so  \
		raypy/librayforce.dylib  \
		raypy/core/ \
		tmp/ \
		build/ \
		dist/ && \
		find . -type d -name "__pycache__" -exec rm -rf {} +


all: clean pull_from_gh shared lib
