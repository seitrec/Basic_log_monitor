"""
This module is defined to parse w3c-formatted HTTP log lines and extract what we need from them
"""

import re
import time
from collections import namedtuple

# Regexp matching every part of a w3c-formatted HTTP log line
# We expect a logline to look like this :
# 192.168.1.3 - - [20/12/2015:21:15:44 +01.000] "GET /api/browse/id" 404 1978

_HTTP_LOG_PATTERN = re.compile(r'\A(?P<remoteHost>\S+) (?P<rfc931>\S+) (?P<authUser>\S+) \[(?P<date>\S+) '
                               r'(?P<offsetGMT>[+-]\d{2}\.\d{3})] "(?P<method>\S+) (?P<request>/(?P<section>[^/]*)'
                               r'(?:/\S*)?(?P<protocol> \S+)?)" (?P<status>\d+) (?P<bytes>\d+)')
_ParsedLine = namedtuple("ParsedLine", ["section", "status", "host", "utc_ts", "traffic"])


def parse_logline(new_entry):
    """
    Parse a formatted log line to extract the information we need
    :param new_entry: (string) w3c-formatted log line
    :return unnamed: (dict) dictionary with 3 keys
        - section: the section hit, api in our example above
        - status: of the request, 404 in our example above
        - utc_ts: timestamp converted to utc, 1450642544.0 in our example above
        - host: ip of the remote Host, 192.168.1.3 in our example
        - traffic: Amount of bytes transferred, 1978 in our example
    """
    properties = _HTTP_LOG_PATTERN.match(new_entry)
    local_time_offset = time.mktime(time.localtime()) - time.mktime(time.gmtime())
    section = properties.group("section")
    status = properties.group("status")
    host = properties.group("remoteHost")
    traffic = int(properties.group("bytes"))

    local_ts = time.mktime(time.strptime(properties.group("date"), "%d/%m/%Y:%H:%M:%S"))
    offset = float(properties.group("offsetGMT")) * 3600
    utc_ts = local_ts - offset + local_time_offset

    return _ParsedLine(section, status, host, utc_ts, traffic)
