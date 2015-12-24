"""
Buffer Class, containing all the log lines during the period time frame
"""

from collections import Counter, deque


class LogsBuffer(deque):
    def __init__(self, period=2):
        deque.__init__(self)
        self.hits = Counter()
        self.statuses = Counter()
        self.host_traffic = Counter()
        self.period = period*60

    def add_entry(self, parsed_entry):
        """
        Add an entry to the buffer
        :param parsed_entry: (NamedTuple) containing the relevant information about a new entry
                                          ParsedLine(section, status, host, utc_ts, traffic)
        """
        self.append(parsed_entry)
        self.hits[parsed_entry.section] += 1
        self.statuses[parsed_entry.status] += 1
        self.host_traffic[parsed_entry.host] += parsed_entry.traffic

    def clean_old_entries(self, now):
        """
        Remove all entries that are older than the period from the buffer
        :param now: (float) now timestamp
        """
        while len(self) != 0 and self[0].utc_ts < now - self.period:
            oldest = self.popleft()
            self.hits[oldest.section] -= 1
            self.statuses[oldest.status] -= 1
            self.host_traffic[oldest.host] -= oldest.traffic

    def get_total_hits(self):
        """
        :return: (int) the number of hits in the buffer (ie during the period)
        """
        return len(self)

    def get_total_sections(self):
        """
        :return: (int) amount of sections registered in the buffer (ie hit during the period)
        """
        return len(self.hits)

    def get_popular_sections(self):
        """
        :return: (deque): Ordered list of tuples representing the most commonly hit sections (section, amount of hits)
        """
        return deque(self.hits.most_common())

    def get_statuses(self):
        """
        :return: (Counter): the Counter {status number: amount of hits)
        """
        return self.statuses

    def get_total_success(self):
        """
        :return: (int) amount of successful hits
        """
        return sum(v if k.startswith("2") else 0 for k, v in self.statuses.iteritems())

    def get_total_users(self):
        """
        :return: (int) amount of users registered in the buffer (ie that sent at least one request during the period)
        """
        return len(self.host_traffic)

    def get_user_traffic(self):
        """
        :return: (deque) Ordered list of tuples representing the users generating most trafic (user, traffic)
        """
        return deque(self.host_traffic.most_common())

    def get_total_traffic(self):
        """
        :return: (int) Total amount of Bytes transferred during the period
        """
        return sum(self.host_traffic.values())
