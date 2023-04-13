import shutil
from setuptools import setup, find_packages

# pipenv run python setup.py develop
setup(
    name='src',
    version='0.1',
    author='Lukas Schroeder',
    url='https://github.com/lukasschr/bachelorthesis-social-media-analytics',
    packages=find_packages()
)

shutil.rmtree('src.egg-info')