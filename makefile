PYTHON=./env/bin/python3
SRC=pmix/

.PHONY: lint tags ltags test

lint:
	${PYTHON} -m pylint --output-format=colorized --reports=n ${SRC} && \
	${PYTHON} -m pycodestyle ${SRC} && \
	${PYTHON} -m pydocstyle ${SRC}

tags:
	ctags -R --python-kinds=-i .

ltags:
	ctags -R --python-kinds=-i ./${SRC}

test:
	${PYTHON} -m unittest discover -v
