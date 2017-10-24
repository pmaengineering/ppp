#!/usr/bin/env bash
# Files have to be named: HQ.xlsx, FQ.xlsx, and SQ.xlsx.
# TODO: Dynamic suffix.

SUFFIX=_2017.10.05-v10-jef

python -m pmix.ppp -l English -f doc HQ.xlsx > HQ_EN${SUFFIX}.doc
python -m pmix.ppp -l English -p minimal -f doc HQ.xlsx > HQ_EN-minimal${SUFFIX}.doc
python -m pmix.ppp -l Français -f doc HQ.xlsx > HQ_FR${SUFFIX}.doc
python -m pmix.ppp -l Français -p minimal -f doc HQ.xlsx > HQ_FR-minimal${SUFFIX}.doc

python -m pmix.ppp -l English -f doc FQ.xlsx > FQ_EN${SUFFIX}.doc
python -m pmix.ppp -l English -p minimal -f doc FQ.xlsx > FQ_EN-minimal${SUFFIX}.doc
python -m pmix.ppp -l Français -f doc FQ.xlsx > FQ_FR${SUFFIX}.doc
python -m pmix.ppp -l Français -p minimal -f doc FQ.xlsx > FQ_FR-minimal${SUFFIX}.doc

python -m pmix.ppp -l English -f doc SQ.xlsx > SQ_EN${SUFFIX}.doc
python -m pmix.ppp -l English -p minimal -f doc SQ.xlsx > SQ_EN-minimal${SUFFIX}.doc
python -m pmix.ppp -l Français -f doc SQ.xlsx > SQ_FR${SUFFIX}.doc
python -m pmix.ppp -l Français -p minimal -f doc SQ.xlsx > SQ_FR-minimal${SUFFIX}.doc
