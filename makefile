PYTHON=./env/bin/python3
SRC=pmix/

.PHONY: lint tags

lint:
	${PYTHON} -m pylint ${SRC} 	&& \
	${PYTHON} -m pycodestyle ${SRC} && \
	${PYTHON} -m pydocstyle ${SRC}

tags:
	ctags -R --python-kinds=-i .

