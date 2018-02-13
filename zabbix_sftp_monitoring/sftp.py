#!/usr/bin/python

import argparse
import tempfile
import os
import pysftp

####################### Put all the function here ################################

def gen_name():
    return tempfile.NamedTemporaryFile(dir="/tmp", prefix="test-", delete=False)

def gen_file(file, size_in_mb):
    with open(file, "wb") as out:
        out.seek( size_in_mb * 1024 * 1024)
        out.write('0')

test_file = gen_name().name

### Default values
default = {
    "port": 22,
    "local_file": test_file,
    "remote_file": "./" + os.path.basename(test_file),
    "file_size": 10,
}

####################### END OF FUNCTION BLOCK #####################################

parser = argparse.ArgumentParser(description = "Do sftp login, upload and delete file")
parser.add_argument("-H", "--host", required=True, help="hostname or ip address of the remote sftp server")
parser.add_argument("-P", "--port", default=default["port"] , help="port of the remote sftp server")
parser.add_argument("-u", "--user", required=True, help="username for sftp authentication")
parser.add_argument("-p", "--password", required=True, help="password for specified user")
parser.add_argument("-l", "--local_file" , default=default["local_file"], help="path to local file")
parser.add_argument("-r", "--remote_file", default=default["remote_file"], help="path to remote location")
parser.add_argument("-s", "--file_size", default=default["file_size"], help="file size for sftp upload/download test in MB")

args = parser.parse_args()

# Store args in variable
sftp_host = args.host
sftp_port = args.port
sftp_user = args.user
sftp_pass = args.password
sftp_local_file = args.local_file
sftp_remote_file = args.remote_file
sftp_file_size = args.file_size

################################ START MAIN PROGRAM ################################

gen_file(sftp_local_file, sftp_file_size)

cnopts = pysftp.CnOpts()
cnopts.hostkeys = None

try:
    with pysftp.Connection(sftp_host, port=sftp_port, username=sftp_user, password=sftp_pass, cnopts=cnopts) as sftp:
        # Test upload
        sftp.put(sftp_local_file)

        # Test download
        sftp.get(sftp_remote_file, sftp_local_file + "_from_remote")

        # Cleanup remote test file
        sftp.remove(sftp_remote_file)
        os.remove(sftp_local_file + "_from_remote")
        print "sftp test success"
except:
    print "sftp test failed"

# Cleanup local test file
os.remove(sftp_local_file)
