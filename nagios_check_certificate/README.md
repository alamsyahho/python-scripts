# Nagios plugin to check https endpoints

Python plugins for nagios to monitor https endpoint with 2 main features:
1. This plugins will monitor if https connection is self-signed or whether certificate chain is broken using pycurl
2. Additionally it will also monitor the domain ssl certificate expiry date and also its chain or root certificate expiry. Most of the monitoring plugins only monitor for the main domain without checking whether the chain certificate is expired or not

Requirements:
1. pyopenssl
2. pycurl
3. argparse
4. certifi

### Usage

    # python3.7 checkCertExpiry.py -h
      usage: checkCertExpiry.py [-h] -H HOST [-P PORT] -s SERVER_NAME -w WARN -c
                                CRIT

      Nagios plugins to monitor connection using pycurl and certificate expiry

      optional arguments:
        -h, --help            show this help message and exit
        -H HOST, --host HOST  KEMP Virtual Service ip Address
        -P PORT, --port PORT  KEMP Virtual Service port
        -s SERVER_NAME, --server_name SERVER_NAME
                              Server name or host name of the virtual host domain
        -w WARN, --warn WARN  threshold of warn expiry days
        -c CRIT, --crit CRIT  threshold of crit expiry days

### Example

Check if certificate expiry is within warning or critical threshold

    # python3.7 checkCertExpiry.py -H 10.40.0.24 -s www.mydomain.com -w 30 -c 10
    WARNING: <X509Name object '/C=US/ST=Nevada/L=Las Vegas/O=My Orgs, Inc./CN=*.mydomain.com'> will be expired less than 24.

    # python3.7 checkCertExpiry.py -H 10.40.0.24 -s www.mydomain.com -w 30 -c 10
    CRITICAL: Curl unable to connect to www.mydomain.com on 10.40.0.24: (60, "SSL: no alternative certificate subject name matches target host name 'www.mydomain.com'")
