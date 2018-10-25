SRC=ppp/

.PHONY: lint tags ltags test all lintall codestyle docstyle lintsrc \
linttest doctest doc docs code linters_all codesrc codetest docsrc \
doctest paper build dist pypi-push-test pypi-push pypi-test pip-test pypi \
pip demo remove-previous-build git-hash install upgrade-once upgrade \
uninstall reinstall install-internal-dependencies upgrade-latest \
upgrade-stable install-latest-internal-dependencies install-latest \
install-stable

# Batched Commands
# - Code & Style Linters
all: linters_all testall
lint: lintsrc codesrc docsrc
linters_all: doc code lintall

# Pylint Only
PYLINT_BASE =python3 -m pylint --output-format=colorized --reports=n
lintall: lintsrc linttest
lintsrc:
	${PYLINT_BASE} ${SRC}
linttest:
	${PYLINT_BASE} test/

# PyCodeStyle Only
PYCODESTYLE_BASE=python3 -m pycodestyle
codestyle: codestylesrc codestyletest
codesrc: codestylesrc
codetest: codestyletest
code: codestyle
codestylesrc:
	${PYCODESTYLE_BASE} ${SRC}
codestyletest:
	 ${PYCODESTYLE_BASE} test/

# PyDocStyle Only
PYDOCSTYLE_BASE=python3 -m pydocstyle
docstyle: docstylesrc docstyletest
docsrc: docstylesrc
doctest: docstyletest
docs: docstyle
docstylesrc:
	${PYDOCSTYLE_BASE} ${SRC}
docstyletest:
	${PYDOCSTYLE_BASE} test/
codetest:
	python -m pycodestyle test/
codeall: code codetest
doc: docstyle

# Testing
test:
	python3 -m unittest discover -v
testdoc:
	python3 -m test.test --doctests-only
testall: test testdoc
test-survey-cto: #TODO: run a single unit test
	python3 -m unittest discover -v
DEMO_IN=test/files/multiple_file_language_option_conversion
DEMO_OUT=~/Desktop/ppp-demo
demo:
	mkdir ${DEMO_OUT}
	for file in ${DEMO_IN}/*.xlsx; do \
		cp $$file ${DEMO_OUT}; \
	done
	python3 -m ppp ${DEMO_OUT}/*.xlsx --format doc html \
	--preset standard detailed \
	--language English Français

# Package Management
remove-previous-build:
	rm -rf ./dist; 
	rm -rf ./build; 
	rm -rf ./*.egg-info
build: remove-previous-build
	python3 setup.py sdist bdist_wheel
dist: build
pypi-push-test: build
	twine upload --repository-url https://test.pypi.org/legacy/ dist/*
pypi-push:
	twine upload --repository-url https://upload.pypi.org/legacy/ dist/*; \
	make remove-previous-build
pypi-test: pypi-push-test
pip-test: pypi-push-test
pypi: pypi-push
pip: pypi-push

## Dependency Management
# For some reason, if something has been uploaded to pip very recently, you
# need to --upgrade using --no-cache-dir.
git-hash:
	git rev-parse --verify HEAD
install-internal-dependencies:
	pip install git+https://github.com/PMA-2020/pmix@master --upgrade
install-latest-internal-dependencies:
	pip install git+https://github.com/PMA-2020/pmix@develop --upgrade
install:
	make install-internal-dependencies; \
	pip install -r requirements-unlocked.txt --no-cache-dir; \
	pip freeze > requirements.txt
#	make upgrade-once
#upgrade-once:
#	pip install -r requirements-unlocked.txt --no-cache-dir --upgrade; \
#	pip freeze > requirements.txt
upgrade:
	make install-latest-internal-dependencies; \
	pip freeze > requirements.txt
#	make upgrade-once; \
#	make upgrade-once
uninstall:
	workon ppp-web; \
	bash -c "pip uninstall -y -r <(pip freeze)"
reinstall:
	make uninstall; \
	make install; \
#	make upgrade
install-latest: install
install-stable:
	make install-internal-dependencies; \
	pip install -r requirements-unlocked.txt --no-cache-dir; \
	pip freeze > requirements.txt
upgrade-latest: install-latest-internal-dependencies
upgrade-stable: install-internal-dependencies

# Scripts
paper:
	sh ./scripts/generic_paper_questionnaires.sh
