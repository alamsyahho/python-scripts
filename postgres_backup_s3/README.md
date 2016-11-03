# Postgres Backup to Amazon S3 bucket

Python script to run pg_dump, compress then upload the compressed file to amazon s3 bucket

Requirements:

1. pg_dump binary
2. python module boto
3. python module filechunkio

Update this 3 config to suits your s3 key and bucket settings:

    s3_access_key = "RandomAccessKey"
    s3_secret_key = "RandomSecretKey"
    s3_bucket = "YourBucketName"
