from setuptools import setup, find_packages
from urllib import request, error
import platform
import shutil
import os
import subprocess
import zipfile

import dotenv


class UnrecognizedOperatingSystem(Exception):
    """Raises when the current operating system cannot be identified"""

class RcloneDownloadFailed(Exception):
    """Raises when the ZIP archive cannot be downloaded successfully"""

class NoExecutableRcloneFound(Exception):
    """Raises when there is no rclone executable in the .rclone folder"""


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
    raise UnrecognizedOperatingSystem(
        '''The operating system could not be detected automatically! 
        Please add the following line to the .env file manually: 
        OS=your_operating_system'''
    )


def install_rclone(operating_system):

    rclone_directory = {
        'Windows': {'url': 'https://downloads.rclone.org/rclone-current-windows-amd64.zip', 
                    'executable': 'rclone.exe'},
        'Linux': {'url': 'https://downloads.rclone.org/rclone-current-linux-amd64.zip', 
                  'executable': 'rclone'},
        'Darwin': {'url': 'https://downloads.rclone.org/rclone-current-osx-amd64.zip', 
                   'executable': 'rclone'}
    } 

    def _download_and_extract(url, executable):
        # download rclone zip archive for the operating system
        try:
            request.urlretrieve(url, '.rclone/rclone.zip')
        except error.HTTPError:
            raise RcloneDownloadFailed(
                '''rclone could not be successfully downloaded from the server!
                Please download the rclone executable file manually and move the program to the .rclone folder.
                Then run this script again'''
            )
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

    def _configure(executable):
        # make rclone executable
        if operating_system == 'Linux':
            subprocess.run(['chmod', '+x', f'.rclone/{executable}'], check=True)
        # create configurations file for rclone
        subprocess.run([f'.rclone/{executable}', '--config', '.rclone/rclone.conf', 'config', 'create', 'git_lfs_ftp', 
                        'ftp', f"host={os.environ.get('FTP_HOST')}", f"user={os.environ.get('FTP_USER')}", 
                        f"pass={os.environ.get('FTP_PASS')}"], check=True)

    url = rclone_directory[operating_system]['url']
    executable = rclone_directory[operating_system]['executable']
    if not os.path.exists('.rclone'):
        os.mkdir('.rclone')
        _download_and_extract(url, executable)
        _configure(executable)
    elif (os.path.isfile(f'.rclone/{executable}') and not os.path.isfile('.rclone/rclone.conf')):
        _configure(executable)
    elif (os.path.isfile(f'.rclone/{executable}') and os.path.isfile('.rclone/rclone.conf')):
        print('rclone already installed and set up!')
        pass
    else:
        raise NoExecutableRcloneFound(
            '''No executable rclone was found in the .rclone folder!
            Please download the rclone executable file manually and move the program to the .rclone folder.
            Then run this script again'''
        )


install_rclone(operating_system)

# clean project folder structure
shutil.rmtree('src.egg-info')

# pipenv run python setup.py develop