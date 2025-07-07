class IronWallScanner:
    def __init__(self, threat_database):
        self.threat_database = threat_database
        self.quarantined_files = []

    def count_files(self, directory):
        total_files = 0
        for dirpath, dirnames, filenames in os.walk(directory):
            total_files += len(filenames)
        return total_files

    def estimate_scan_time(self, total_files):
        # Assuming an average of 0.5 seconds per file
        return total_files * 0.5

    def scan_file(self, file_path):
        # Simulate scanning a file for threats
        if self.threat_database.is_threat(file_path):
            self.quarantined_files.append(file_path)
            return True  # Threat found
        return False  # No threat found

    def scan_directory(self, directory):
        total_files = self.count_files(directory)
        estimated_time = self.estimate_scan_time(total_files)
        print(f"Scanning {total_files} files. Estimated time: {estimated_time} seconds.")

        scanned_files = 0
        for dirpath, dirnames, filenames in os.walk(directory):
            for filename in filenames:
                file_path = os.path.join(dirpath, filename)
                threat_found = self.scan_file(file_path)
                scanned_files += 1
                print(f"Scanning {file_path}... {'Threat found!' if threat_found else 'No threat.'}")

        print(f"Scan complete. {scanned_files} files scanned. Quarantined files: {len(self.quarantined_files)}")