PYTHON=./env/bin/python3
SRC=./pmix/
TEST=./test/


.PHONY: lint tags ltags test all lint_all codestyle docstyle server serve lint_src lint_test doctest doc docs code linters_all code_src code_test doc_src doc_test paper

# Batched Commands
all: linters_all test_all
lint: lint_src code_src doc_src
linters_all: doc code lint_all

# Pylint Only
PYLINT_BASE =${PYTHON} -m pylint --output-format=colorized --reports=n
lint_all: lint_src lint_test
lint_src:
	${PYLINT_BASE} ${SRC}
lint_test:
	${PYLINT_BASE} ${TEST}

# PyCodeStyle Only
PYCODESTYLE_BASE=${PYTHON} -m pycodestyle
codestyle: codestyle_src codestyle_test
code_src: codestyle_src
code_test: codestyle_test
code: codestyle
codestyle_src:
	${PYCODESTYLE_BASE} ${SRC}
codestyle_test:
	 ${PYCODESTYLE_BASE} ${TEST}

# PyDocStyle Only
PYDOCSTYLE_BASE=${PYTHON} -m pydocstyle
docstyle: docstyle_src docstyle_test
doc_src: docstyle_src
doc_test: docstyle_test
doc: docstyle
docs: docstyle
docstyle_src:
	${PYDOCSTYLE_BASE} ${SRC}
docstyle_test:
	${PYDOCSTYLE_BASE} ${TEST}

# Text Editor Commands
TAGS_BASE=ctags -R --python-kinds=-i
tags:
	${TAGS_BASE} .
ltags:
	${TAGS_BASE} ${SRC}

codetest:
	${CODE_TEST}

codeall: code codetest


# PYDOCSTYLE
doc:
	${DOC_SRC}


# TESTING
TEST_FEATURE_FILE=BFR5-Household-Questionnaire-v8-jef
test:
	${PYTHON} -m unittest discover -v

test_feature:
	${PYTHON} -m pmix.ppp test/files/${TEST_FEATURE_FILE}.xlsx -l English -f html -p minimal > output/${TEST_FEATURE_FILE}.html

test_feature_doc:
	${PYTHON} -m pmix.ppp test/files/${TEST_FEATURE_FILE}.xlsx -l English -f doc -p minimal > output/${TEST_FEATURE_FILE}.doc
	open output/${TEST_FEATURE_FILE}.doc

testdoc:
	${PYTHON} -m test.test --doctests-only

test_all: test testdoc


# SERVER MANAGEMENT
ssh:
	ssh root@192.155.80.11


# CTAGS
tags:
	ctags -R --python-kinds=-i .

ltags:
	ctags -R --python-kinds=-i ./${CODE_SRC}


# Application Management
serve:server
server:
	gunicorn pmaapi.__main__:APP

# Scripts
paper:
	sh ./scripts/generic_paper_questionnaires.sh
