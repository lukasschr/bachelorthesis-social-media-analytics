from setuptools import setup, find_packages
from urllib import request
import platform
import shutil
import os
import subprocess
import zipfile

import dotenv


class UnrecognizedOperatingSystem(Exception):
    """Raises when the current operating system cannot be identified"""


setup(
    name='src',
    version='0.1',
    author='Lukas Schroeder',
    url='https://github.com/lukasschr/bachelorthesis-social-media-analytics',
    packages=find_packages()
)


# Identify operating system and store information in .env variable
dotenv_file = dotenv.find_dotenv()
dotenv.load_dotenv(dotenv_file)
operating_system = platform.system()
if operating_system == 'Windows':
    dotenv.set_key(dotenv_file, 'OS', 'Windows')
elif operating_system == 'Linux':
    dotenv.set_key(dotenv_file, 'OS', 'Linux')
elif operating_system == 'Darwin':
    dotenv.set_key(dotenv_file, 'OS', 'Darwin')
else:
    raise UnrecognizedOperatingSystem


def install_rclone(url, executable):
    os.mkdir('.rclone')
    # download rclone zip archive for the operating system
    request.urlretrieve(url, '.rclone/rclone.zip')
    # extract rclone executable
    with zipfile.ZipFile('.rclone/rclone.zip', 'r') as zip_ref:
        for file in zip_ref.namelist():
            if file.endswith(executable):
                path_to_executable = file
                zip_ref.extract(file, '.rclone')
                break
    # clean project folder structure
    shutil.move(f'.rclone/{path_to_executable}', '.rclone')
    shutil.rmtree(f'.rclone/{os.path.dirname(path_to_executable)}')
    os.remove('.rclone/rclone.zip')
    # create configurations file for rclone
    subprocess.run([f'.rclone/{executable}', '--config', '.rclone/rclone.conf', 'config', 'create', 'git_dbx_lfs', 'dropbox', 
                    f"client_id={os.environ.get('CLIENT_ID')}", f"client_secret={os.environ.get('CLIENT_SECRET')}"], check=True)


# --- RCLONE INSTALLATION & SETUP ---
if not os.path.exists('.rclone'):
    if operating_system == 'Windows':
        install_rclone(url='https://downloads.rclone.org/rclone-current-windows-amd64.zip',
                       executable='rclone.exe')
    elif operating_system == 'Linux' or operating_system == 'Darwin':                               # TO TEST
        install_rclone(url='https://downloads.rclone.org/rclone-current-linux-amd64.zip',
                       executable='rclone')


# clean project folder structure
shutil.rmtree('src.egg-info')

# pipenv run python setup.py develop