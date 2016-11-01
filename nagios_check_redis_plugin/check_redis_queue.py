#!/usr/bin/python

import subprocess
import os, sys
import redis
import argparse

state_ok=0
state_warning=1
state_critical=2
state_unknown=3

parser = argparse.ArgumentParser(description="Nagios plugins to monitor redis queue")
parser.add_argument("queue_type", choices=['normal', 'delayed'], help="normal | delayed")
parser.add_argument("key_name", help="name of redis key to search")
parser.add_argument("-H", "--host", help="redis hostname or ip address")
parser.add_argument("-P","--port", help="redis port")
parser.add_argument("-p","--password", help="redis password")
parser.add_argument("-w","--warn", type=int, help="threshold of warn queue")
parser.add_argument("-c","--crit", type=int, help="threshold of crit queue")
args = parser.parse_args()

# Store args in variable
redis_host = args.host
redis_port = args.port
redis_pass = args.password
queue_type = args.queue_type
queue_name = args.key_name
warn_queue = args.warn
crit_queue = args.crit

r = redis.StrictRedis(host=redis_host, port=redis_port, password=redis_pass, db=0)

try:
    r.ping()
except redis.ConnectionError:
    print "CRITICAL: Could not connect to Redis at %r:%r: Connection refused" % (redis_host, redis_port)
    sys.exit(state_critical)

if queue_type == "normal":
    normal_queue_name = 'queues:' + args.key_name
    count = r.llen(normal_queue_name)
elif queue_type == "delayed":
    delayed_queue_name = 'queues:' + args.key_name + ':delayed'
    count = r.zcount(delayed_queue_name,"-inf","+inf")

if ( warn_queue is not None and crit_queue is not None ):

    # Delay thresholds are set
    if ( warn_queue is None or crit_queue is  None):
        print "Both warning and critical thresholds must be set"
        sys.exit(state_unknown)

    if not warn_queue >= 0:
        print "Warning threshold must be a valid integer greater than 0"
        sys.exit(state_unknown)

    if not crit_queue >= 0:
        print "Critical threshold must be a valid integer greater than 0"
        sys.exit(state_unknown)

    if warn_queue >= crit_queue:
        print "Warning threshold cannot be greater than critical"
        sys.exit(state_unknown)

    if count >= crit_queue:
        print "CRITICAL: %d queues" % count
        sys.exit(state_unknown)
    elif count >= warn_queue:
        print "WARNING: %d queues" % count
        sys.exit(state_unknown)
    else:
        print "OK: %d queues" % count
        sys.exit(state_ok)

else:
    # Without thresholds
    print "OK: %d queues" % count
    sys.exit(state_ok)
