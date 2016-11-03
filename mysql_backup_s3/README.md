# MySQL Backup to Amazon S3 bucket

Simple python script to perform full and incremental backup then upload the backup to S3 bucket

Requirements:

1. percona-xtrabackup
2. python module boto
3. python module filechunkio

Update this 3 config to suits your s3 key and bucket settings:

    s3_access_key = "RandomAccessKey"
    s3_secret_key = "RandomSecretKey"
    s3_bucket = "YourBucketName"

Please note that full backup will only be done on Sunday. Without full backup, incremental backup scripts will fail
