PYTHON_JKP=./env/bin/python3
PYTHON_JEF=python3
TEST_DIR=test/
SRC=pmaapi/

.PHONY: lint tags ltags test flint go_lint go_code go_doc server serve

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

go_lint:
	${PYTHON_JEF} -m pylint --output-format=colorized --reports=n ${SRC} && \
	${PYTHON_JEF} -m pylint --output-format=colorized --reports=n ${TEST_DIR}

go_code:
	${PYTHON_JEF} -m pycodestyle ${SRC} && \
	${PYTHON_JEF} -m pycodestyle ${TEST_DIR}

go_doc:
	${PYTHON_JEF} -m pydocstyle ${SRC} && \
	${PYTHON_JEF} -m pydocstyle ${TEST_DIR}

tags:
	ctags -R --python-kinds=-i .

ltags:
	ctags -R --python-kinds=-i ./${SRC}

test:
	${PYTHON_JKP} -m unittest discover -v

server:
	gunicorn pmaapi.__main__:APP

serve:
	gunicorn pmaapi.__main__:APP
