#!/usr/bin/python

from OpenSSL import SSL
from io import BytesIO
from datetime import datetime
import certifi, socket, pycurl
import sys, argparse

parser = argparse.ArgumentParser(description="Nagios plugins to monitor connection using pycurl and certificate expiry")
parser.add_argument("-H", "--host", required=True, help="KEMP Virtual Service ip Address")
parser.add_argument("-P","--port", default=443, required=False, help="KEMP Virtual Service port")
parser.add_argument("-s","--server_name", required=True, help="Server name or host name of the virtual host domain")
parser.add_argument("-w","--warn", type=int, required=True, help="threshold of warn expiry days")
parser.add_argument("-c","--crit", type=int, required=True, help="threshold of crit expiry days")
args = parser.parse_args()

# Store args in variable
VSHost = args.host
VSPort = args.port
serverName = args.server_name
warnThreshold = args.warn
critThreshold = args.crit

stateOk, stateWarning, stateCritical, stateUnknown = 0, 1, 2, 3

def curlChecks(ip_address, port, virtual_host):
    b_obj = BytesIO()
    crl = pycurl.Curl()
    httpsURL = 'https://%s' %(virtual_host)
    crl.setopt(crl.URL, httpsURL)
    crl.setopt(crl.WRITEDATA, b_obj)
    crl.setopt(crl.RESOLVE, ['%s:%d:%s' %(virtual_host, port, ip_address)])
    crl.perform()
    crl.close()

def certChecks(ip_address, port):
    context = SSL.Context(method=SSL.TLSv1_2_METHOD)
    context.load_verify_locations(cafile=certifi.where())

    conn = SSL.Connection(context, socket=socket.socket(socket.AF_INET, socket.SOCK_STREAM))
    conn.settimeout(5)
    conn.connect((ip_address, port))
    conn.setblocking(1)
    conn.do_handshake()
    conn.set_tlsext_host_name(ip_address.encode())

    crit, warn, message = (False, False, '')

    for (idx, cert) in enumerate(conn.get_peer_cert_chain()):
        certExpiryDate = datetime.strptime(cert.get_notAfter().decode('ascii'), '%Y%m%d%H%M%SZ')
        todayDate = datetime.today()
        expiredDays = (certExpiryDate - todayDate).days
        certHasExpired = cert.has_expired()

        if certHasExpired:
            crit = True
            expiredDate = datetime.strftime(certExpiryDate, "%d %b %Y")
            message += '%s has expired on %s.' %( cert.get_subject(),expiredDate )
        elif expiredDays <= critThreshold:
            crit = True
            message += '%s will be expired less than %d.' %( cert.get_subject(),expiredDays )
        elif expiredDays <= warnThreshold:
            warn = True
            message += '%s will be expired less than %d.' %( cert.get_subject(),expiredDays )

    return crit, warn, message

if __name__ == '__main__':
    # Run curl checks
    try:
        curlChecks(VSHost, VSPort, serverName)
    except pycurl.error as exc:
        print('CRITICAL: Curl unable to connect to %s on %s: %s' %( serverName, VSHost, exc ))
        sys.exit(stateCritical)

    # Run certificate checks
    try:
        if warnThreshold <= critThreshold:
            print('Warning threshold cannot be smaller than critical')
            sys.exit(stateUnknown)

        critExists, warnExists, errorMessage = certChecks(VSHost, VSPort)

        if critExists:
            print('CRITICAL: %s' %(errorMessage))
            sys.exit(stateCritical)
        elif warnExists:
            print('WARNING: %s' %(errorMessage))
            sys.exit(stateWarning)
        else:
            print('OK: All checks green')
            sys.exit(stateOk)
    except Exception as e:
        print('WARNING: %s' %(e))
        sys.exit(stateWarning)

