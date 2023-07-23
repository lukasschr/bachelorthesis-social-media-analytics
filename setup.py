from setuptools import setup, find_packages
import shutil

setup(
    name='src',
    version='1.0',
    author='Lukas Schroeder',
    url='https://github.com/lukasschr/bachelorthesis-social-media-analytics',
    packages=find_packages()
)

# clean project folder structure
shutil.rmtree('src.egg-info')

# pipenv run python setup.py develop