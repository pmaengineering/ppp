PYTHON=./env/bin/python3
SRC=pmix/

.PHONY: lint

lint:
	${PYTHON} -m pylint ${SRC} 	&& \
	${PYTHON} -m pycodestyle ${SRC} && \
	${PYTHON} -m pydocstyle ${SRC}

