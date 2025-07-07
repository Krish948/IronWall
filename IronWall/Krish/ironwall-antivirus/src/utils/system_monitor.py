class SystemMonitor:
    def __init__(self):
        self.cpu_usage = 0
        self.disk_usage = 0

    def update_metrics(self):
        import psutil
        self.cpu_usage = psutil.cpu_percent(interval=1)
        self.disk_usage = psutil.disk_usage('/').percent

    def get_cpu_usage(self):
        return self.cpu_usage

    def get_disk_usage(self):
        return self.disk_usage

    def estimate_scan_time(self, file_count):
        base_time = 0.1  # seconds per file
        cpu_factor = 1 + (self.cpu_usage / 100)
        disk_factor = 1 + (self.disk_usage / 100)
        estimated_time = file_count * base_time * cpu_factor * disk_factor
        return estimated_time