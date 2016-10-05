from distutils.core import setup

from pmix import __version__
setup(
    name='pmix',
    version=__version__,
    author='James K. Pringle',
    author_email='jpringle@jhu.edu',
    url='http://www.pma2020.org',
    packages=[
        'pmix', 
        'pmix.test'
    ],
    license='LICENSE.txt',
    description='Smattering of Python3 tools for PMA workflow',
    long_description=open('README.txt').read(),
    install_requires=[
        'XlsxWriter>=0.7.0',
        'xlrd>=0.9.3'
    ],
)
