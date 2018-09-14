PYTHON=python3
SRC=./pmix/
TEST=./test/

.PHONY: lint tags ltags test all lintall codestyle docstyle lintsrc \
linttest doctest doc docs code linters_all codesrc codetest docsrc \
doctest paper build dist pypi-push-test pypi-push pypi-test pip-test pypi \
pip demo

# Batched Commands
# - Code & Style Linters
all: linters_all testall
lint: lintsrc codesrc docsrc
linters_all: doc code lintall

# Pylint Only
PYLINT_BASE =${PYTHON} -m pylint --output-format=colorized --reports=n
lintall: lintsrc linttest
lintsrc:
	${PYLINT_BASE} ${SRC}
linttest:
	${PYLINT_BASE} ${TEST}

# PyCodeStyle Only
PYCODESTYLE_BASE=${PYTHON} -m pycodestyle
codestyle: codestylesrc codestyletest
codesrc: codestylesrc
codetest: codestyletest
code: codestyle
codestylesrc:
	${PYCODESTYLE_BASE} ${SRC}
codestyletest:
	 ${PYCODESTYLE_BASE} ${TEST}

# PyDocStyle Only
PYDOCSTYLE_BASE=${PYTHON} -m pydocstyle
docstyle: docstylesrc docstyletest
docsrc: docstylesrc
doctest: docstyletest
docs: docstyle
docstylesrc:
	${PYDOCSTYLE_BASE} ${SRC}
docstyletest:
	${PYDOCSTYLE_BASE} ${TEST}
codetest:
	${CODE-test}
codeall: code codetest
doc: docstyle
doc:
	${DOC_SRC}

# Testing
test:
	${PYTHON} -m unittest discover -v
testdoc:
	${PYTHON} -m test.test --doctests-only
testall: test testdoc
test-survey-cto: #TODO: run a single unit test
	${PYTHON} -m unittest discover -v
DEMO_IN=test/files/multiple_file_language_option_conversion
DEMO_OUT=~/Desktop/ppp-demo
demo:
	mkdir ${DEMO_OUT}
	for file in ${DEMO_IN}/*.xlsx; do \
		cp $$file ${DEMO_OUT}; \
	done
	python3 -m ppp ${DEMO_OUT}/*.xlsx -f doc html -p minimal full -l English Français


# Package Management
build:
	rm -rf ./dist && rm -rf ./build && ${PYTHON} setup.py sdist bdist_wheel
dist: build
pypi-push-test:
	make build && twine upload --repository-url https://test.pypi.org/legacy/ dist/*
pypi-push:
	make build && twine upload --repository-url https://upload.pypi.org/legacy/ dist/*
pypi-test: pypi-push-test
pip-test: pypi-push-test
pypi: pypi-push
pip: pypi-push

# Scripts
paper:
	sh ./scripts/generic_paper_questionnaires.sh
