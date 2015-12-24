import argparse
from logging import getLogger
import sys
import time
from Tailer import Tailer
from Parser import parse_logline
from Buffer import LogsBuffer
from Warden import AlertWarden
from DisplayHelper import get_formatted_stats, format_alert_message, format_alert_status
from datetime import datetime

logger = getLogger(__name__)


def main():
    parser = argparse.ArgumentParser(description="Monitor a log file of HTTP Access")
    parser.add_argument("-l", "--logpath", default="logs.txt", type=str,
                        help="The path to the access log file we wish to monitor")
    parser.add_argument("-s", "--summary", default="alerts.txt", type=str,
                        help="File where to write events we need to archive")
    parser.add_argument("-p", "--period", default=2, type=int,
                        help="Time frame (int, in minutes) of the monitoring statistics")
    parser.add_argument("-r", "--refresh", default=10, type=int,
                        help="Refresh rate (int, in seconds) for the console output of monitoring statistics")
    args = parser.parse_args()

    tailed_file = Tailer(args.logpath, .5)
    monitor_buffer = LogsBuffer(args.period)
    alert_warden = AlertWarden(args.period)
    next_display = time.mktime(time.gmtime()) + 10

    with open(args.summary, 'a') as alert_logs:
        for newline in tailed_file.read():
            now = time.mktime(time.gmtime())
            readable_now = datetime.fromtimestamp(now).strftime('%H:%M:%S')
            try:
                parsed_line = parse_logline(newline)
                monitor_buffer.clean_old_entries(now)
                monitor_buffer.add_entry(parsed_line)
            except AttributeError as e:
                logger.warning("Exception %s was thrown while parsing: %s", (e, newline))
                pass
            message_type, data = alert_warden.update(monitor_buffer.get_total_hits(), now)
            alert_state = format_alert_message(message_type, data)
            if alert_state:
                alert_logs.write(alert_state)
                alert_logs.flush()
                print(alert_state)

            if now > next_display:
                print get_formatted_stats(readable_now, format_alert_status(alert_warden.status()),
                                          monitor_buffer.get_total_hits(),
                                          monitor_buffer.get_total_sections(),
                                          monitor_buffer.get_popular_sections(),
                                          monitor_buffer.get_statuses(),
                                          monitor_buffer.get_total_success(),
                                          monitor_buffer.get_total_users(),
                                          monitor_buffer.get_user_traffic(),
                                          monitor_buffer.get_total_traffic()
                                          )
                next_display += 10


if __name__ == '__main__':
    sys.exit(main())
