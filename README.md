========================================
Qlang: Questionnaire Language Utilities
========================================

This version requires Python 3 or later. Python 2 is not supported.

------------
Installation
------------

Run:

pip3 install https://github.com/jkpr/qlang/zipball/master


-----
Usage
-----

To create translation files:

python -m qlang.qlang FILE1 [FILE2 ...]

To merge translations back:

python -m qlang.qlang -m FILE1 [FILE2 ...]

When merging back, the original XLSForms must be in the same directory.

----
Bugs
----

Submit bug reports to James Pringle at jpringleBEAR@jhu.edu minus the bear.
