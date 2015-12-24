"""
Tracks new lines in a file
The new lines are returned by the read method, as a generator
(Credit goes to Jeff Bauer, that described this method on StackOverflow, I had a hard time finding a way:
http://stackoverflow.com/questions/5419888/reading-from-a-frequently-updated-file)
"""

import time


class Tailer:
    def __init__(self, tailed_file_path, refresh_rate=1.0):
        """
        Construct the tailer
        :param tailed_file_path (string): Path to the file that we want to follow
        :param refresh_rate (float): Time to wait when no new line is found (since we don't need extreme reactivity)
        """
        self.tailed_file_path = tailed_file_path
        self.refresh_rate = refresh_rate
        self.proceed = True

    def read(self):
        """
        Pseudo-infinite loop that yields any new line written in the file at self.tailed_file_path
        :return unnamed (generator): containing all lines written in the monitored file since the method was called
        """
        with open(self.tailed_file_path, 'r') as tailed_file:
            tailed_file.seek(0, 2)
            while self.proceed:
                line = tailed_file.readline()
                if not line:
                    time.sleep(self.refresh_rate)
                else:
                    yield line.strip("\n")

    def stop(self):
        """
        Stop the file tailing
        """
        self.proceed = False
