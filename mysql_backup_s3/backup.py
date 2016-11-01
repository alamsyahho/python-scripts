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

backup_name = 'your_apps'
backupdir = '/tmp/backup'
today = date.today()
dayofweek = today.isoweekday()
day_name = today.strftime("%A")

if dayofweek == '7':
    fullbackup_day = today.day.__str__()
    fullbackup_month = today.month.__str__()
    fullbackup_year = today.year.__str__()
    backupdir_full = backupdir/full
    compress_target = backupdir_full
    compress_result = compress_target+'.tar.bz2'
else:
    fullbackup_day = ((date.today() - timedelta(days=dayofweek))).day.__str__()
    fullbackup_month = ((date.today() - timedelta(days=dayofweek))).month.__str__()
    fullbackup_year = ((date.today() - timedelta(days=dayofweek))).year.__str__()
    backupdir_full = backupdir + "/full"
    backupdir_inc = backupdir + "/incremental_" + dayofweek.__str__()
    backupdir_baseinc = backupdir + "/incremental_" + ((date.today() - timedelta(days=1))).isoweekday().__str__()
    compress_target = backupdir_inc
    compress_result = compress_target+'.tar.bz2'

if dayofweek == '1':
    backupdir_base = backupdir_full
else:
    backupdir_base = backupdir_baseinc

s3_dir = '/db/' + fullbackup_year + '/' + fullbackup_month + '/' + fullbackup_day + '/' + backup_name + '/'

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

def _full_backup(targetdir):
    _info("clean up backup folder targetdir")
    shutil.rmtree(targetdir, ignore_errors= True)
    if not os.path.exists(targetdir):
        os.makedirs(targetdir)
    _info("running full backup")
    _fnull = open(os.devnull, 'w')
    subprocess.call(['/usr/bin/innobackupex', '--slave-info', '--no-timestamp', targetdir], stdout=_fnull, stderr=subprocess.STDOUT)

def _incremental_backup(basedir, targetdir):
    if not os.path.exists(backupdir_full):
        _error("no full backup has been done before...")
        sys.exit(1)

    _fnull = open(os.devnull, 'w')
    if not os.path.exists(targetdir):
        subprocess.call(['/usr/bin/innobackupex', '--slave-info', '--no-timestamp', '--incremental', '--incremental-basedir=%s' % basedir, targetdir], stdout=_fnull, stderr=subprocess.STDOUT)
    else:
        _error(targetdir + ' exists...')
        _error(os.path.basename(targetdir) + ' backup is done before')
        sys.exit(1)

def _compress_backup(file, target):
    with closing(tarfile.open(file, "w:bz2")) as tar:
        tar.add(target)

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

if dayofweek == '7':
    _info('Running full backup')
    _full_backup(backupdir_full)
else:
    _info('Running incremental backup')
    _incremental_backup(backupdir_base, backupdir_inc)

_info('Compressing backup before upload')
_compress_backup(compress_result, compress_target)

_info('Uploading file to ' + s3_bucket + s3_dir)
_upload_s3(s3_access_key, s3_secret_key, compress_result, s3_bucket)
