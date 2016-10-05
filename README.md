# PMIX: Questionnaire Language Utilities

Formerly `qlang`, this package has been renamed and expanded to provide new 
functionality and new command-line tools.
This version requires Python 3 or later. Python 2 is not supported.

More documentation is forthcoming.

## Installation

Run:

```
pip3 install https://github.com/jkpr/pmix/zipball/master
```


## Usage

To create translation files:

python -m pmix.qlang FILE1 [FILE2 ...]

To merge translations back:

python -m pmix.qlang -m FILE1 [FILE2 ...]

When merging back, the original XLSForms must be in the same directory.

## Bugs

Submit bug reports to James Pringle at jpringleBEAR@jhu.edu minus the bear.
