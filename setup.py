"""Setup for Pypi"""
from setuptools import setup, find_packages


packages = find_packages(exclude=['test'])
packages.append('ppp.test')

setup(
    name='odk_ppp',  # ppp was already taken
    version='1.1.1',
    author='Joe Flack',
    author_email='jflack@jhu.edu',
    url='http://www.pma2020.org',
    packages=packages,
    package_dir={
        'ppp': 'ppp',
        'ppp.test': 'test'
    },
    package_data={
        'ppp': [
            'templates/*.html',
            'templates/content/*.html',
            'templates/content/group/*.html',
            'templates/content/prompt/*.html',
            'templates/content/prompt/inputs/*.html',
            'templates/content/repeat/*.html',
            'templates/content/table/*.html'
        ],
        'ppp.test': ['files/*.xlsx']
    },

    license='LICENSE.txt',
    description='Converts ODK XlsForm Excel files into readable formats.',
    long_description=open('README.md').read(),
    install_requires=[
        'xlrd>=0.9.3',
        'Jinja2>=2.9.6'
    ]
)
