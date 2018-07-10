"""Setup for Pypi"""
from setuptools import setup, find_packages


packages = find_packages(exclude=['test'])

setup(
    name='odk_ppp',  # ppp was already taken
    version='1.1.4',
    author='Joe Flack',
    author_email='jflack@jhu.edu',
    url='http://www.pma2020.org',
    packages=packages,
    package_dir={
        'ppp': 'ppp'
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
        ]
    },
    license='LICENSE.txt',
    description='Converts XlsForm Excel files (ODK, SurveyCTO, etc) into '
                'readable formats.',
    long_description=open('README.md').read(),
    install_requires=[
        'xlrd>=0.9.3',
        'Jinja2>=2.9.6'
        'pmix==0.2.2'
    ]
)
