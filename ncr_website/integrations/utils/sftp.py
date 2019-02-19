"""Module to handle FTP uploads and downloads."""
import pysftp
import time
from celery.utils.log import get_task_logger


logger = get_task_logger(__name__)


def sftp_upload_file(host=None,
                     port=None,
                     user=None,
                     password=None,
                     local_path=None,
                     remote_path=None):
    """Upload file.
    :param str host: the address to the FTP host
    :param int port: the port of the FTP host
    :param str user: the FTP-user
    :param str password: the FTP-user password
    :param str local_path: the local path and filename to copy
    :param str remote_path: the remote destination path
    :returns: None
    """

    cnopts = pysftp.CnOpts()

    # Disable host key checking
    cnopts.hostkeys = None

    # Open connection
    sftp = pysftp.Connection(host=host,
                             username=user,
                             password=password,
                             port=port,
                             cnopts=cnopts,
                             log=False, )

    # Uploading should be fast so set a short timeout
    sftp.timeout = 60

    # Upload file
    try:
        sftp.put(localpath=local_path,
                 remotepath=remote_path,
                 confirm=False)
    except Exception as e:
        logger.critical("Error {} while uploading file {}".format(
            e,
            local_path
        ))

    # Close and cleanup connection
    sftp.close()


def sftp_download_file(host=None,
                       port=None,
                       user=None,
                       password=None,
                       remote_path=None,
                       look_for=None,
                       timeout=None,):
    """Download file.
    :param str host: the address to the FTP host
    :param int port: the port of the FTP host
    :param str user: the FTP-user
    :param str password: the FTP-user password
    :param str remote_path: the remote destination path
    :param str look_for: the name of the file to look for on the server
    :param float timeout: how long to wait before closing the function
    :returns: (str) Name of file found on server
    """

    cnopts = pysftp.CnOpts()

    # Disable host key checking
    cnopts.hostkeys = None

    # Disable host key checking
    file_name = False

    # Open connection
    sftp = pysftp.Connection(host=host,
                             username=user,
                             password=password,
                             port=port,
                             cnopts=cnopts,
                             log=False, )

    # Used to track how long a download takes
    PREV_TIME = time.time()

    # Loop through all files in dir and look
    # for the one we just uploaded
    while True:

        # Calculate time since the connection was started
        dt = time.time() - PREV_TIME

        # Break loop after four minutes
        if dt > timeout:
            raise FileNotFoundError

        # Log how long has lapsed since the last rating
        if int(round(dt, 0)) % 2 == 0:
            logger.info('Lapsed time: ' + str(dt))

        # File name has been set by downloading
        # the file, break out of loop
        if file_name:
            break

        for attr in sftp.listdir_attr(remote_path):
            file = attr.filename[19:28]

            if file == look_for:
                file_name = attr.filename
                sftp.get(remote_path + '/' + file_name)

                logger.info('Found file')

                break

    # Close and cleanup connection
    sftp.close()

    return file_name
