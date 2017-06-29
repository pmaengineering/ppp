SRC=pmix/

PYTHON_JKP=./env/bin/python3
PYTHON_JEF=python3
TEST_DIR=test/


.PHONY: lint tags ltags test flint lint_all codestyle docstyle server serve lint_src lint_test fest doctest docfest

targets:
	echo 'Targets: lint tags ltags test flint lint_all codestyle docstyle server serve lint_src lint_test fest doctest docfest'

lint:
	${PYTHON_JKP} -m pylint --output-format=colorized --reports=n ${SRC} && \
	${PYTHON_JKP} -m pycodestyle ${SRC} && \
	${PYTHON_JKP} -m pydocstyle ${SRC}

flint:
	${PYTHON_JEF} -m pylint --output-format=colorized --reports=n ${SRC} && \
	${PYTHON_JEF} -m pycodestyle ${SRC} && \
	${PYTHON_JEF} -m pydocstyle ${SRC} && \
	${PYTHON_JEF} -m pylint --output-format=colorized --reports=n ${TEST_DIR} && \
	${PYTHON_JEF} -m pycodestyle ${TEST_DIR} && \
	${PYTHON_JEF} -m pydocstyle ${TEST_DIR}

lint_all:
	${PYTHON_JEF} -m pylint --output-format=colorized --reports=n ${SRC} && \
	${PYTHON_JEF} -m pylint --output-format=colorized --reports=n ${TEST_DIR}

lint_src:
	${PYTHON_JEF} -m pylint --output-format=colorized --reports=n ${SRC}

lint_test:
	${PYTHON_JEF} -m pylint --output-format=colorized --reports=n ${TEST_DIR}

codestyle:
	${PYTHON_JEF} -m pycodestyle ${SRC} && \
	${PYTHON_JEF} -m pycodestyle ${TEST_DIR}

docstyle:
	${PYTHON_JEF} -m pydocstyle ${SRC} && \
	${PYTHON_JEF} -m pydocstyle ${TEST_DIR}

tags:
	ctags -R --python-kinds=-i .

ltags:
	ctags -R --python-kinds=-i ./${SRC}

test:
	${PYTHON_JKP} -m unittest discover -v

fest:
	${PYTHON_JEF} -m unittest discover -v

doctest:
	${PYTHON_JEF} -m test.test_ppp --doctests-only

docfest:
	${PYTHON_JEF} -m test.test_ppp --doctests-only

server:
	gunicorn pmaapi.__main__:APP

serve:
	gunicorn pmaapi.__main__:APP
