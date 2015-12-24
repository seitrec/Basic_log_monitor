"""
Generate fields used to generate pseudo-logs to fuel the log generator
"""

import time
import random
from math import floor

# Lists used to randomise the requests
# (Redundant values in the lists are there to ponder the randomising)
_METHODS = ["GET", "GET", "GET", "DELETE", "PUT", "POST"]
_PATHS = ["/pages", "/pages", "/pages/corentin", "/pages/corentin/1", "/pages/corentin/2",
         "/search/", "/search/foo", "/search/bar"
         "/portfolio/", "/portfolio/dec",
         "/api/",
         ]
_STATUSES = ["100", "200", "200", "200", "200", "301", "404", "500"]
_IP_BLOCKS = [1, 1, 1, 2, 2, 3]


def create_host():
    """
    Randomise IP addresses (just a little, we don't want too many users, in order to be able to get some stats)
    :return: (str): Randomised IP address
    """
    return "192.168.%d.%d" % (random.choice(_IP_BLOCKS), random.choice(_IP_BLOCKS))


def create_logname():
    return "-"


def create_username():
    return "-"


def create_date():
    """
    Create a properly formatted date
    :return: (str): representation of the current datetime
    """
    now = time.gmtime()
    return time.strftime("%d/%m/%Y:%H:%M:%S ", now) + get_zero_padded_utc_offset()


def create_request():
    """
    Randomise the request
    :return: (str): Concatenation of a method and a path
    """
    return " ".join([random.choice(_METHODS), random.choice(_PATHS)])


def create_protocol():
    """
    No need to randomise here since we are not especially interested
    :return: (str): standard protocol
    """
    return "HTTP/1.0"


def create_status():
    """
    Randomise from the list _STATUSES
    :return: (str): Typical request status found in an http log line
    """
    return random.choice(_STATUSES)


def create_bytes():
    """
    Fully randomise the volume of pages, even though it's not totally realistic (doesn't matter...)
    :return: (int): random integer between 100 and 3000
    """
    return random.randrange(100, 3000, 1)


def get_zero_padded_utc_offset():
    """
    Create a properly formatted UTC offset to represent the datetime
    :return: (str): Offset to UTC
    """
    nb_hours = floor((time.mktime(time.localtime())-time.mktime(time.gmtime()))/3600)
    sign = "+" if nb_hours >= 0 else "-"
    value = "0" + str(nb_hours) if nb_hours < 10 else str(nb_hours)
    return sign + value + "00"
