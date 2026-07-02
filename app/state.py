import time


class AppState:
    def __init__(self):
        self.scanned_count = 0
        self.alert_count = 0
        self.last_alert_link = "None"
        self.quota_remaining = 0
        self.ai_threshold = 35
        self.start_time = time.time()

    def record_scan(self):
        self.scanned_count += 1

    def record_alert(self, link):
        self.alert_count += 1
        self.last_alert_link = link

    def uptime(self):
        elapsed = int(time.time() - self.start_time)
        hours, remainder = divmod(elapsed, 3600)
        minutes, seconds = divmod(remainder, 60)
        return hours, minutes, seconds
