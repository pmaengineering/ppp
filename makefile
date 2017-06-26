PYTHON=./env/bin/python3
FLACK_PYTHON=/Library/Frameworks/Python.framework/Versions/3.6/bin/python3
ENV_PYTHON=python3
TEST_DIR=test/
SRC=pmix/

.PHONY: lint tags ltags test flint go_lint go_code go_doc

lint:
	${PYTHON} -m pylint --output-format=colorized --reports=n ${SRC} && \
	${PYTHON} -m pycodestyle ${SRC} && \
	${PYTHON} -m pydocstyle ${SRC}

flint:
	${FLACK_PYTHON} -m pylint --output-format=colorized --reports=n ${SRC} && \
	${FLACK_PYTHON} -m pycodestyle ${SRC} && \
	${FLACK_PYTHON} -m pydocstyle ${SRC} && \
	${FLACK_PYTHON} -m pylint --output-format=colorized --reports=n ${TEST_DIR} && \
	${FLACK_PYTHON} -m pycodestyle ${TEST_DIR} && \
	${FLACK_PYTHON} -m pydocstyle ${TEST_DIR}

go_lint:
	${FLACK_PYTHON} -m pylint --output-format=colorized --reports=n ${SRC} && \
	${FLACK_PYTHON} -m pylint --output-format=colorized --reports=n ${TEST_DIR}

go_code:
	${FLACK_PYTHON} -m pycodestyle ${SRC} && \
	${FLACK_PYTHON} -m pycodestyle ${TEST_DIR}

go_doc:
	${FLACK_PYTHON} -m pydocstyle ${SRC} && \
	${FLACK_PYTHON} -m pydocstyle ${TEST_DIR}

tags:
	ctags -R --python-kinds=-i .

ltags:
	ctags -R --python-kinds=-i ./${SRC}

test:
	${PYTHON} -m unittest discover -v
