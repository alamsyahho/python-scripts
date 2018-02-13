# Zabbix plugin to monitor sftp servers

Python plugins for zabbix sftp connection monitoring

Requirements: python module pysftp
```
# pip install pysftp
```

### Usage
```
# python sftp.py -h
usage: sftp.py [-h] -H HOST [-P PORT] -u USER -p PASSWORD [-l LOCAL_FILE]
               [-r REMOTE_FILE] [-s FILE_SIZE]

Do sftp login, upload and delete file

optional arguments:
  -h, --help            show this help message and exit
  -H HOST, --host HOST  hostname or ip address of the remote sftp server
  -P PORT, --port PORT  port of the remote sftp server
  -u USER, --user USER  username for sftp authentication
  -p PASSWORD, --password PASSWORD
                        password for specified user
  -l LOCAL_FILE, --local_file LOCAL_FILE
                        path to local file
  -r REMOTE_FILE, --remote_file REMOTE_FILE
                        path to remote location
  -s FILE_SIZE, --file_size FILE_SIZE
                        file size for sftp upload/download test in MB

```
### Example
```
# python sftp.py -H 1.1.1.1 -u zabbix -p sftppassword
sftp test success

# # python sftp.py -H 2.2.2.2 -u zabbix -p sftppassword
sftp test failed
```
