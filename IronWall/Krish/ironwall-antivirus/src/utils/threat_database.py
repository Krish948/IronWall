class ThreatDatabase:
    def __init__(self):
        self.threats = self.load_threats()
        self.quarantined_files = []

    def load_threats(self):
        # Load known threats from a predefined source (e.g., a file or database)
        return {
            "virus1.exe": "Virus",
            "malware2.dll": "Malware",
            "trojan3.zip": "Trojan",
        }

    def check_threat(self, file_name):
        return file_name in self.threats

    def quarantine_file(self, file_name):
        if file_name not in self.quarantined_files:
            self.quarantined_files.append(file_name)

    def get_quarantined_files(self):
        return self.quarantined_files

    def clear_quarantine(self):
        self.quarantined_files.clear()