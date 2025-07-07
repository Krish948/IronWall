class IronWallMainWindow:
    def __init__(self, scanner, system_monitor, threat_db):
        self.scanner = scanner
        self.system_monitor = system_monitor
        self.threat_db = threat_db

    def run(self):
        self.display_welcome_message()
        self.start_scan()

    def display_welcome_message(self):
        print("Welcome to IronWall Antivirus!")
        print("Your system will be scanned for potential threats.")

    def start_scan(self):
        total_files = self.scanner.count_files()
        print(f"Total files to scan: {total_files}")
        estimated_time = self.scanner.estimate_scan_time(total_files)
        print(f"Estimated scan time: {estimated_time} seconds")

        for i in range(total_files):
            self.scanner.scan_file(i)
            self.display_progress(i + 1, total_files)

        print("Scan completed!")

    def display_progress(self, scanned, total):
        progress_percentage = (scanned / total) * 100
        print(f"Progress: {scanned}/{total} files scanned ({progress_percentage:.2f}%)")