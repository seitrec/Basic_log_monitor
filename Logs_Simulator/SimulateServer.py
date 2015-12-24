"""
Simulate w3c-formatted HTTP access log
In order to observe some variance in the events we randomise the time between new lines in seconds as a sum of:
    - a float [0:1] generated every 60 seconds (to have high/low traffic frames compared to our 2mn monitoring buffer)
    - a float [0:0.2] generated every line (to have a randomised time every line)
"""

import argparse
import sys
import random
from time import sleep
import time
import HTTP_log_fields

_LOG_LINE_TEMPLATE = '%(remotehost)s %(rfc931)s %(authuser)s [%(date)s] "%(request)s" %(status)s %(bytes)s\n'


def add_entry(file):
    """
    Write an entry to the logFile
    :param file: (str) File handler, needs to be open for writing
    """
    log_line = {"remotehost": HTTP_log_fields.create_host(),
                "rfc931": HTTP_log_fields.create_logname(),
                "authuser": HTTP_log_fields.create_username(),
                "date": HTTP_log_fields.create_date(),
                "request": HTTP_log_fields.create_request(),
                "status": HTTP_log_fields.create_status(),
                "bytes": HTTP_log_fields.create_bytes()
                }
    file.write(_LOG_LINE_TEMPLATE % log_line)
    print _LOG_LINE_TEMPLATE % log_line
    file.flush()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-l", "--lines", default=1000, type=int,
                        help="Number of log lines to write in the output")
    parser.add_argument("-o ", "--outputfile", default="logs.txt", type=str,
                        help="Where to output the logs")
    args = parser.parse_args()

    period = random.random()
    next_period = time.mktime(time.gmtime()) + 60

    loop = range(sys.maxint) if args.lines is None else range(int(args.lines))
    with open(args.outputfile, 'w') as output_file:
        for _ in loop:
            if time.mktime(time.gmtime()) > next_period:
                next_period += 60
                period = random.random()
            add_entry(output_file)
            sleep(period + random.random() / 5)
    return 0


if __name__ == '__main__':
    sys.exit(main())
