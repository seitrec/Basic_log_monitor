"""
This module is the Warden of the alerts informations.
It is used to check if an alert is happening, and remember about it until it recovers to a normal behavior
"""

from datetime import datetime
from DisplayHelper import format_period

_BASIC_HOURLY_ALERT_THRESHOLD = 7200


class AlertWarden:
    def __init__(self, period):
        self.in_alert_since = None
        self.hits_peak = 0
        self.alert_threshold = period * 60 * _BASIC_HOURLY_ALERT_THRESHOLD / 3600

    def update(self, buffer_hits, now):
        """
        Update the alert status and return information about the changes made
        If there is no current alert, check if there is a new one.
        If an alert is already happening, check the current number of hits
            - Update the peak if necessary
            - Recover to normal mode if necessary
        :param buffer_hits: (int) Amount of hits in the last period
        :param now: (float) Timestamp of the last line received
        :return (tuple): Information about the alert changes if a state change happened
            - message_type: (int) 0: recover, 1:alert, 2: nothing
            - data: (tuple) data to format the message
        """
        readable_now = datetime.fromtimestamp(now).strftime('%Y-%m-%d %H:%M:%S')
        if self.hits_peak < buffer_hits:
            self.hits_peak = buffer_hits
        if self.in_alert_since is None:
            if buffer_hits >= self.alert_threshold:
                self.in_alert_since = now
                return 1, (readable_now, self.hits_peak, self.alert_threshold)
        else:
            if buffer_hits < self.alert_threshold:
                duration, peak = format_period(now - self.in_alert_since), self.hits_peak
                self.in_alert_since = None
                self.hits_peak = 0
                return 0, (duration, peak, self.alert_threshold)
        return 2, ()

    def status(self):
        """
        :return (str): String giving a hint about the alert state (ok, almost alert, or alert)
        """
        return 0 if self.hits_peak < 0.9 * self.alert_threshold \
            else 1 if self.hits_peak < self.alert_threshold \
            else 2
