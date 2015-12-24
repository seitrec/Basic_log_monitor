"""
"""

import math

_STATS_TEMPLATE = """\
========================%(time)s========================\n
%(summary)s\n
              MOST POPULAR SECTIONS\n
%(popular)s\n
                STATUSES SUMMARY\n
%(status)s\n
                 INTENSIVE USERS\n
%(users)s\n
========================================================\n
"""

_HTTP_CODES_HEADERS = {"1": "information", "2": "success", "3": "redirection", "4": "client_error", "5": "server_error"}
_POPULAR_SECTION_TEMPLATE = "/%s is popular with %s/%s (%2d%%)"
_STATUS_SUM_TEMPLATE = "%2d%% %s requests"
_USER_TRAFFIC_TEMPLATE = "%2d%% of our traffic is with %s"
_SUMMARY_TEMPLATE = "%s - %s Users - %s/%s successful hits - %sB of traffic"

_IS_SUFFIXES = {0: "", 1: "K", 2: "M", 3: "G", 4: "T", 5: "P"}

_ALERT_TEMPLATE = "%s: The traffic exceeded the fixed Threshold with a value of %s out of %s.\n"
_RECOVERY_TEMPLATE = "The traffic returned to a reasonable level. Alert lasted %s and peaked at %s out of %s.\n"
_ALERT_MESSAGES = {0: _RECOVERY_TEMPLATE, 1: _ALERT_TEMPLATE}

_STATUS_OK_TEMPLATE = "Low Traffic"
_STATUS_HIGH_TEMPLATE = "HIGH TRAFFIC"
_STATUS_DANGER_TEMPLATE = "ALERT TRAFFIC"
_ALERT_STATUSES = {0: _STATUS_OK_TEMPLATE, 1: _STATUS_HIGH_TEMPLATE, 2: _STATUS_DANGER_TEMPLATE}


def format_period(seconds):
    """
    Convert a number of seconds into a readable information
    :param seconds: (int) number of seconds to convert
    :return (str): %H:%M:%S
    """
    m, s = divmod(seconds, 60)
    h, m = divmod(m, 60)
    return "%d:%2d:%2d" % (h, m, s)


def format_IS(bytes):
    """
    Convert a integer into a string representation in the IS system (using K, M, G, T, P prefixes)
    :param bytes: (int) The int to be represented
    :return: (str) representation of byte
    """
    magnitude = int(math.log(bytes, 10))
    group = int(magnitude / 3)
    return str(int(bytes / (10 ** (3 * group)))) + _IS_SUFFIXES[group]


def get_formatted_popular(popular_sections, total_hits, total_sections):
    """
    Yield strings describing the most popular sections, selecting the ones that accumulate more than "their part"
    of the traffic (ie more than 100*total/n(sections) %)
    :params: identical to ones described below in get_formatted_stats
    :return: (str generator) Strings describing the most popular sections
    """
    popularity_threshold = float(total_hits) / total_sections
    while len(popular_sections) != 0 and popular_sections[0][1] >= popularity_threshold:
        section = popular_sections.popleft()
        yield _POPULAR_SECTION_TEMPLATE % (section[0], section[1],
                                           total_hits, (100. * section[1]) / total_hits)


def get_formatted_statuses(statuses, total_hits):
    """
    :params: identical to ones described below in get_formatted_stats
    :return: (str generator) Strings describing the statuses repartition
    """
    for i in _HTTP_CODES_HEADERS:
        status_total = sum(v if k.startswith(i) else 0 for k, v in statuses.iteritems())
        yield _STATUS_SUM_TEMPLATE % (100. * status_total / total_hits, _HTTP_CODES_HEADERS[i])


def get_formatted_user_traffic(intensive_users, total_traffic, total_users):
    """
    Yield strings describing the most intense users, selecting the ones that accumulate more than "their part"
    of the traffic (ie more than 100*total/n(users) %)
    :params: identical to ones described below in get_formatted_stats
    :return: (str generator) Strings describing the most intense users
    """
    traffic_threshold = float(total_traffic) / total_users
    while len(intensive_users) != 0 and intensive_users[0][1] >= traffic_threshold:
        user = intensive_users.popleft()
        yield _USER_TRAFFIC_TEMPLATE % ((100. * user[1]) / total_traffic, user[0])


def get_formatted_summary(alert_status, total_users, total_success, total_hits, total_traffic):
    """
    Create a string giving the essential summarised information about the traffic as a whole
    :params: identical to ones described below in get_formatted_stats
    :return: (str) Strings describing the traffic as a whole
    """
    return _SUMMARY_TEMPLATE % (alert_status, total_users, total_success, total_hits, format_IS(total_traffic))


def get_formatted_stats(readable_now, alert_status, total_hits, total_sections, popular_sections, statuses,
                        total_success, total_users, intensive_users, total_traffic):
    """

    :param readable_now: (str) readable information about the time: %H:%M:%S
    :param alert_status: (str) quick information about the alert state
    :param total_hits: (int) the number of hits in the buffer (ie during the period)
    :param total_sections: (int) amount of sections registered in the buffer (ie hit during the period)
    :param popular_sections: (deque): Ordered list of tuples representing the most commonly hit sections (section, amount of hits)
    :param statuses: (Counter): the Counter {status number: amount of hits)
    :param total_success: (int) amount of successful hits
    :param total_users: (int) amount of users registered in the buffer (ie that sent at least one request during the period)
    :param intensive_users: (deque) Ordered list of tuples representing the users generating most trafic (user, traffic)
    :param total_traffic: (int) Total amount of Bytes transferred during the period
    :return:
    """
    return _STATS_TEMPLATE % \
           {"time": readable_now,
            "summary": get_formatted_summary(alert_status, total_users, total_success, total_hits, total_traffic),
            "popular": "\n".join([section for section
                                  in get_formatted_popular(popular_sections, total_hits, total_sections)]),
            "status": "\n".join([status for status
                                 in get_formatted_statuses(statuses, total_hits)]),
            "users": "\n".join([user for user
                                in get_formatted_user_traffic(intensive_users, total_traffic, total_users)]),
            }


def format_alert_message(message_type, data):
    """
    Render as a string information about a new alert or recovery event
    :param message_type: (int) the type of message to display (0:recovery or 1:alert)
    :param data: (tuple) Data required to format the message:
        - if message_type = 1:
            data[0] = readable_now: (str) readable information about the time: %H:%M:%S
            data[1] = hits_peak: (int) during an alert, the highest amount or entries in the buffer
            data[2] = alert_threshold: (int) the threshold determining an alert
        - if message_type = 0:
            data[0] = duration: (int) duration of the alert
            data[1] = peak: (int) during an alert, the highest amount or entries in the buffer
            data[2] = alert_threshold: (int) the threshold determining an alert
        - if message_type = 2:
            data is then empty
    :return: (str) message to display to inform of an alert or recovery
    """
    return _ALERT_MESSAGES[message_type] % data if message_type != 2 else ""


def format_alert_status(status):
    """
    Display a status message corresponding to the alert status level
    :param status: (int) represents the alert status level
    :return: (str): "Low Traffic", "HIGH TRAFFIC" or "ALERT TRAFFIC"
    """
    return _ALERT_STATUSES[status]
