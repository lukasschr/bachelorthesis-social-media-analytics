import subprocess
import argparse
import os

operating_system = os.environ.get('OS')
if operating_system == 'Windows':
    rclone_executable= 'rclone.exe'
elif operating_system == 'Linux' or operating_system == 'Darwin':                                   # TO TEST
    rclone_executable= 'rclone'


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Determines how the data should be synchronized', 
                                    epilog='Made with <3 by Lukas Schroeder')
    parser.add_argument('mode', help='push OR pull')
    args = parser.parse_args()

    if args.mode == 'push':
        subprocess.run([f'.rclone/{rclone_executable}', '--config', '.rclone/rclone.conf', 'sync', 'data', 'git_dbx_lfs:'], 
                       check=True)
    elif args.mode == 'pull':
        subprocess.run([f'.rclone/{rclone_executable}', '--config', '.rclone/rclone.conf', 'sync', 'git_dbx_lfs:', 'data'], 
                       check=True)
    else:
        raise Exception