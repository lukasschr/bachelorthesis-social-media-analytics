from email.message import EmailMessage
import pickle
import os
import ssl
import smtplib
import platform


class UnrecognizedOperatingSystem(Exception):
    """Raises when the current operating system cannot be identified"""


def safe_as_pkl(obj, filename:str, path:str):
    """Serial object.

    Object is saved as a .pkl file in the specified location.

    Args:
        obj: the object to be serialized
        filename: name of the .pkl file
        path: location
    """
    with open(f'{path}/{filename}.pkl', 'wb') as f:
        pickle.dump(obj, f)


def cache(obj, caching_token:str):
    """Serial multiple objects.

    Opens a .pkl file and appends the given object

    Args:
        obj: the object to be serailized and appended
        caching_token: path of the .pkl file
    """
    if not os.path.exists('../.cache'):
        os.mkdir('../.cache')
    with open(f'../.cache/{caching_token}.pkl', 'ab') as f:
        pickle.dump(obj, f)


def load_pkl(path):
    """Load serialized objects.

    The serialized objects within the file are de-serialized and returned as a list

    Args:
        path: path to .pkl file

    Returns:
        List of de-serialized objects
    """
    objs = []
    with open(path, 'rb') as f:
        while True:
            try:
                obj = pickle.load(f)
            except EOFError:
                break
            objs.append(obj)
    return objs


def send_notification(sender=os.environ.get('GMAIL_MAIL'), 
                      receiver=os.environ.get('DEFAULT_RECEIVER_MAIL'),
                      g_app_pass=os.environ.get('G_APP_PASS')):
    """Sends a notification via email.
    
    Sends a very simple email to a recipient account via a Gmail account. 
    Note: The sender,receiver and g_app_pass variables can be previously set in an .env file.
    Otherwise the variables must be overwritten.

    Args:
        sender: email address of the Google account
        receiver: email address of the receiver
        g_app_pass: 16 digit google app password
    """
    mail = EmailMessage()
    mail['From'] = sender
    mail['To'] = receiver
    mail['Subject'] = 'Script executed successfully!'
    with smtplib.SMTP_SSL('smtp.gmail.com', 465, context=ssl.create_default_context()) as smtp:
        smtp.login(sender, g_app_pass)
        smtp.sendmail(sender, receiver, mail.as_string())


def shutdown():
    """Shuts down the system.

    If a code runs for a long time, this function can be used to automatically shut down the system 
    after successful execution.
    WARNING: This function can only be used if the code is run with admin rights
    """
    operating_system = platform.system()
    if operating_system == 'Windows':
        os.system('shutdown /s /t 0')
    elif operating_system == 'Linux' or operating_system == 'Darwin':
        os.system('sudo shutdown now')
    else:
        raise UnrecognizedOperatingSystem