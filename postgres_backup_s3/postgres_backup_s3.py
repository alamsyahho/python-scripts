#!/usr/bin/python

import time
import subprocess
import math, os, sys, shutil
import tarfile
import boto
from boto.s3.key import Key
from datetime import datetime, date, timedelta
from filechunkio import FileChunkIO
from contextlib import closing

##########################################################################################
# SET VARIABLE
##########################################################################################

# S3 config
s3_access_key = "RandomAccessKey"
s3_secret_key = "RandomSecretKey"
s3_bucket = "YourBucketName"

backup_name = 'YourBackupName'
backup_path = '/var/tmp/backup'
db_user = 'postgres'
db_name = 'database_name'

##########################################################################################
# FUNCTION
##########################################################################################

def _out(tag, *msgs):
    s = ''

    if not msgs:
        return

    for msg in msgs:
        s += str(msg)

    out = "[%s] %s: %s" % (datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S'), tag, s)
    print out

def _info(*msgs):
    _out('INFO', *msgs)

def _warn(*msgs):
    _out('WARN', *msgs)

def _error(*msgs):
    _out('ERROR', *msgs)

def _die(*msgs):
    _out('FATAL', *msgs)
    if not xb_exit_code: _exit_code(XB_EXIT_BY_DEATH)
    raise Exception(str(msgs))

def _debug(*msgs):
    if xb_opt_debug: _out("** DEBUG **", *msgs)

def _pg_dump(db, destination):
    shutil.rmtree(backup_path, ignore_errors= True)
    if not os.path.exists(backup_path):
        os.makedirs(backup_path)

    _fnull = open(os.devnull, 'w')
    subprocess.call(['pg_dump', '-U', db_user, '-d', db_name, '-f', destination], stdout=_fnull, stderr=subprocess.STDOUT)

def _compress_backup(source, destination):
    with closing(tarfile.open(source, "w:bz2")) as tar:
        tar.add(destination)

def _upload_s3(aws_access_key_id, aws_secret_access_key, file, bucket):
    try:
        size = os.stat(file).st_size
    except:
        # Not all file objects implement fileno(),
        # so we fall back on this
        file.seek(0, os.SEEK_END)
        size = file.tell()

    conn = boto.connect_s3(aws_access_key_id, aws_secret_access_key)
    bucket = conn.get_bucket(bucket, validate=True)
    k = Key(bucket)

    mp = bucket.initiate_multipart_upload(s3_dir + os.path.basename(file))

    chunk_size = 52428800
    chunk_count = int(math.ceil(size / float(chunk_size)))

    for i in range(chunk_count):
        offset = chunk_size * i
        bytes = min(chunk_size, size - offset)
        with FileChunkIO(file, 'r', offset=offset, bytes=bytes) as fp:
            mp.upload_part_from_file(fp, part_num= i + 1)

    mp.complete_upload()

##########################################################################################
# START BACKUP PROCESS
##########################################################################################

backup_sql = backup_path + '/' + backup_name + '.sql'
backup_compressed =  backup_path + '/' + backup_name + '.tar.bz2'
s3_dir = '/db/' + date.today().year.__str__() + '/' + date.today().month.__str__() + '/' + date.today().day.__str__() + '/' + backup_name + '/'

_info('Backup database %s to %s' %(db_name, backup_sql))
_pg_dump(db_name, backup_sql)

_info('Compressing backup to %s' % backup_compressed)
_compress_backup(backup_compressed, backup_sql)

_info('Uploading file to ' + s3_bucket + s3_dir)
_upload_s3(s3_access_key, s3_secret_key, backup_compressed, s3_bucket)
