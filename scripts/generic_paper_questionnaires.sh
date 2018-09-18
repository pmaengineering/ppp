#!/usr/bin/env bash
# Files have to be named: HQ.xlsx, FQ.xlsx, and SQ.xlsx.
# TODO: Dynamic suffix.

SUFFIX=_2017.10.05-v10-jef

python3 -m ppp -l English -f doc HQ.xlsx > HQ_EN${SUFFIX}.doc
python3 -m ppp -l English -p standard -f doc HQ.xlsx > HQ_EN-standard${SUFFIX}.doc
python3 -m ppp -l Français -f doc HQ.xlsx > HQ_FR${SUFFIX}.doc
python3 -m ppp -l Français -p standard -f doc HQ.xlsx > HQ_FR-standard${SUFFIX}.doc

python3 -m ppp -l English -f doc FQ.xlsx > FQ_EN${SUFFIX}.doc
python3 -m ppp -l English -p standard -f doc FQ.xlsx > FQ_EN-standard${SUFFIX}.doc
python3 -m ppp -l Français -f doc FQ.xlsx > FQ_FR${SUFFIX}.doc
python3 -m ppp -l Français -p standard -f doc FQ.xlsx > FQ_FR-standard${SUFFIX}.doc

python3 -m ppp -l English -f doc SQ.xlsx > SQ_EN${SUFFIX}.doc
python3 -m ppp -l English -p standard -f doc SQ.xlsx > SQ_EN-standard${SUFFIX}.doc
python3 -m ppp -l Français -f doc SQ.xlsx > SQ_FR${SUFFIX}.doc
python3 -m ppp -l Français -p standard -f doc SQ.xlsx > SQ_FR-standard${SUFFIX}.doc
