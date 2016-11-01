# Nagios plugin to check redis queue

Python plugins for nagios to check number of normal or delayed queue in redis server

Requirements:
1. python module redis
2. python module argparse

### Usage

    # ./check_redis_queue.py --help
    usage: test.py [-h] [-H HOST] [-P PORT] [-p PASSWORD] [-w WARN] [-c CRIT]
                   {normal,delayed} key_name

    Nagios plugins to monitor redis queue

    positional arguments:
      {normal,delayed}      normal | delayed
      key_name              name of redis key to search

    optional arguments:
      -h, --help            show this help message and exit
      -H HOST, --host HOST  redis hostname or ip address
      -P PORT, --port PORT  redis port
      -p PASSWORD, --password PASSWORD
                            redis password
      -w WARN, --warn WARN  threshold of warn queue
      -c CRIT, --crit CRIT  threshold of crit queue

### Example

Check redis normal queue

    ./check_redis_queue.py -H 10.20.1.221 -P 17380 -w 1 -c 2 normal redis-low
    CRITICAL: 4 queues

Check redis delayed queue

    ./check_redis_queue.py -H 10.20.1.221 -P 17380 -w 1 -c 2 delayed redis-low
    OK: 0 queues
