import subprocess
import argparse
import os
import logging
import ftplib


class FTPConnectionFailed(Exception):
    """Raises when the FTP server is not reachable"""


FOLDERS_TO_SYNC=['data']

operating_system = os.environ.get('OS')
if operating_system == 'Windows':
    rclone_executable= 'rclone.exe'
elif operating_system == 'Linux' or operating_system == 'Darwin':                                   # TO TEST
    rclone_executable= 'rclone'


if __name__ == '__main__':
    # setup logging
    logging.basicConfig(
        format='%(levelname)s %(message)s',
        level=logging.INFO
    )

    # setup cli with argparse
    parser = argparse.ArgumentParser(description='Determines how the data should be synchronized', 
                                    epilog='Made with <3 by Lukas Schroeder')
    parser.add_argument('mode', choices=['push', 'pull'], help='')
    args = parser.parse_args()

    # make sure the FTP server is reachable
    try:
        ftplib.FTP(os.environ.get('FTP_HOST'))
        logging.info('  ~ ftp server is reachable')
    except TimeoutError:
        raise FTPConnectionFailed(
            '''A connection to the server could not be established!
            This problem should not occur. Please excuse this. 
            Please contact me immediately. Either by email or by phone'''
        )

    if args.mode == 'push':
        for folder in FOLDERS_TO_SYNC:
            logging.info(f'  ~ push {folder} to server...')
            subprocess.run([f'.rclone/{rclone_executable}', '--config', '.rclone/rclone.conf', 'sync', 
                            f'{folder}', f'git_lfs_ftp:/bachelorthesis-social-media-analytics/{folder}'])
            logging.info(f'  ~ Done.')
    elif args.mode == 'pull':
        logging.warning(f'  ~ Make sure all folders to be synchronized exist on the server!')
        for folder in FOLDERS_TO_SYNC:
            logging.info(f'  ~ pull {folder} from server...')
            subprocess.run([f'.rclone/{rclone_executable}', '--config', '.rclone/rclone.conf', 'sync',
                            f'git_lfs_ftp:/bachelorthesis-social-media-analytics/{folder}', f'{folder}'])
            logging.info(f'  ~ Done.')
    else:
        raise Exception # this exception should not occur due to 'choices'