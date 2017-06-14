from setuptools import setup, find_packages


from pmix import __version__

packages = find_packages(exclude=['test'])
packages.append('pmix.test')

setup(
    name='pmix',
    version=__version__,
    author='James K. Pringle',
    author_email='jpringle@jhu.edu',
    url='http://www.pma2020.org',
    packages=packages,
    package_dir={
        'pmix.test': 'test'
    },
    license='LICENSE.txt',
    description='Smattering of Python3 tools for PMA workflow',
    long_description=open('README.md').read(),
    install_requires=[
        'XlsxWriter>=0.7.0',
        'xlrd>=0.9.3'
    ],
)
