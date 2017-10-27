# PMIX: Questionnaire Language Utilities

A mixed bag of PMA2020 utilities. There are several functionalities all based
on working with spreadsheets. The main features are the following:

* _analytics_
* _borrow_
* _cascade_
* _ppp_
* _workbook_
* _xlsform_

Formerly `qlang`, this package has been renamed and expanded to provide new
functionality and new command-line tools. The command line tools are described after installation.

This version requires Python 3 or later. Python 2 is not supported.


## Installation

Run:

```
python3 -m pip install https://github.com/jkpr/pmix/zipball/master
```

## Analytics

Usage

```
python3 -m pmix.analytics FILE1 [FILE2 ...]
```

creates a JSON file describing the prompts and fields for analytics.

## Borrow

This module is called with

```
python3 -m pmix.borrow
```

and it does two things. Without the `-m` argument, it simply creates a
translation dictionary. The source string is in the first column, and the
target languages are in the subsequent columns. With the `-m` argument,
it creates a translation dictionary and then merges those translations into
the file specified by `-m`.

#### Examples

1) Without `-m`,

```
python3 -m pmix.borrow FILE1 [FILE2 ...]
```

creates a translation dictionary from `FILE1 [FILE2 ...]`.

2) With `-m`,

```
python3 -m pmix.borrow -m TARGET FILE1 [FILE2 ...]
```

creates a translation dictionary from `FILE1 [FILE2 ...]` and then merges into `TARGET`.

In both examples, a default output filename is used, but one can be specified with the `-o` argument.

The resultant file with merged translations has the following possible highlighting:

* Orange if the source and the translation are the same.
* Blue if the new translation changes the old translation.
* Green if the translation is not found in the TranslationDict, but there is a pre-existing translation.
* Red if translation is not found and there is no pre-existing translation.
* No highlight if the translation is the same as the pre-existing translation.

## Cascade

Usage

```
python3 -m pmix.cascade FILE
```

creates a new Excel spreadsheet after converting geographic identifiers from wide format to tall format.

## PPP

`@joeflack4` to add

## Workbook

There following features are offered:

1. Convert a worksheet to CSV with UTF-8 encoding and UNIX-style newlines.

```
python3 -m pmix.workbook FILE -c SHEET
```

2. Remove all trailing and leading whitespace from all text cells

```
python3 -m pmix.workbook FILE -w
```

## Xlsform

Use the numbering mini-language and create question numbers for an ODK survey.

```
python3 -m pmix.xlsform FILE -n
```

The program then looks for a column entitled "N" in the "survey" worksheet. It creates numbers based off of the
directives there and adds them to label columns.

## Bugs

Submit bug reports to James Pringle at jpringleBEAR@jhu.edu minus the bear.
