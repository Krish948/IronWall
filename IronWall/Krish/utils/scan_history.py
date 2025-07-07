import os
import json
from typing import List, Dict

SCAN_HISTORY_FILE = os.path.join(os.path.dirname(__file__), '..', 'scan_history.json')


def load_scan_history() -> List[Dict]:
    """Load the scan history from the JSON file."""
    if not os.path.exists(SCAN_HISTORY_FILE):
        return []
    try:
        with open(SCAN_HISTORY_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception:
        return []


def save_scan_history(history: List[Dict]):
    """Save the scan history to the JSON file."""
    try:
        with open(SCAN_HISTORY_FILE, 'w', encoding='utf-8') as f:
            json.dump(history, f, indent=2)
    except Exception:
        pass


def add_threat_to_history(threat: Dict):
    """Add a new threat to the scan history log."""
    history = load_scan_history()
    history.append(threat)
    save_scan_history(history)


def add_scan_record(scan_record: Dict):
    """Add a new scan record to the scan history."""
    history = load_scan_history()
    history.append(scan_record)
    save_scan_history(history)


def clear_scan_history():
    """Clear all scan history."""
    save_scan_history([]) 