"""
IronWall Antivirus - Logger Module
Handles system event logging and audit trails
"""

import os
import json
import time
from datetime import datetime, timedelta
from enum import Enum
from typing import List, Dict, Optional, Any

class EventType(Enum):
    """Event types for system logging"""
    SCAN_STARTED = "scan_started"
    SCAN_COMPLETED = "scan_completed"
    SCAN_FAILED = "scan_failed"
    THREAT_DETECTED = "threat_detected"
    THREAT_QUARANTINED = "threat_quarantined"
    THREAT_DELETED = "threat_deleted"
    THREAT_RESTORED = "threat_restored"
    QUARANTINE_ACTION = "quarantine_action"
    PROTECTION_ALERT = "protection_alert"
    SYSTEM_EVENT = "system_event"
    UPDATE_STARTED = "update_started"
    UPDATE_COMPLETED = "update_completed"
    UPDATE_FAILED = "update_failed"
    SCAN = "scan"

class EventStatus(Enum):
    """Event status values"""
    SUCCESS = "success"
    FAILED = "failed"
    PENDING = "pending"
    RUNNING = "running"

class Logger:
    """Main logger class for IronWall events"""
    
    def __init__(self, log_file: str = "system_logs.json"):
        self.log_file = log_file
        self.logs = []
        self.load_logs()
    
    def load_logs(self):
        """Load existing logs from file"""
        try:
            if os.path.exists(self.log_file):
                with open(self.log_file, 'r', encoding='utf-8') as f:
                    self.logs = json.load(f)
        except Exception as e:
            print(f"Error loading logs: {e}")
            self.logs = []
    
    def save_logs(self):
        """Save logs to file"""
        try:
            with open(self.log_file, 'w', encoding='utf-8') as f:
                json.dump(self.logs, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Error saving logs: {e}")
    
    def log_event(self, event_type: EventType, description: str, status: str = "Success", 
                  severity: str = "Low", details: str = "", **kwargs):
        """Log a new event"""
        log_entry = {
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'event_type': event_type.value,
            'description': description,
            'status': status,
            'severity': severity,
            'details': details,
            **kwargs
        }
        self.logs.append(log_entry)
        self.save_logs()
    
    def get_logs(self, event_types: Optional[List[EventType]] = None, 
                 statuses: Optional[List[EventStatus]] = None,
                 start_date: Optional[datetime] = None,
                 end_date: Optional[datetime] = None,
                 search_query: str = "",
                 limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """Get filtered logs"""
        filtered_logs = []
        
        for log in self.logs:
            # Filter by event type
            if event_types:
                log_event_type = EventType(log.get('event_type', ''))
                if log_event_type not in event_types:
                    continue
            
            # Filter by status
            if statuses:
                log_status = log.get('status', '').lower()
                if not any(status.value == log_status for status in statuses):
                    continue
            
            # Filter by date range
            if start_date or end_date:
                try:
                    log_timestamp = datetime.strptime(log.get('timestamp', ''), '%Y-%m-%d %H:%M:%S')
                    if start_date and log_timestamp < start_date:
                        continue
                    if end_date and log_timestamp > end_date:
                        continue
                except:
                    continue
            
            # Filter by search query
            if search_query:
                search_lower = search_query.lower()
                if (search_lower not in log.get('description', '').lower() and
                    search_lower not in log.get('details', '').lower()):
                    continue
            
            filtered_logs.append(log)
        
        # Apply limit
        if limit:
            filtered_logs = filtered_logs[-limit:]
        
        return filtered_logs
    
    def get_event_type_icon(self, event_type: EventType) -> str:
        """Get icon for event type"""
        icons = {
            EventType.SCAN_STARTED: "🔍",
            EventType.SCAN_COMPLETED: "✅",
            EventType.SCAN_FAILED: "❌",
            EventType.THREAT_DETECTED: "🦠",
            EventType.THREAT_QUARANTINED: "🔒",
            EventType.THREAT_DELETED: "🗑️",
            EventType.THREAT_RESTORED: "📦",
            EventType.QUARANTINE_ACTION: "📦",
            EventType.PROTECTION_ALERT: "🚨",
            EventType.SYSTEM_EVENT: "⚙️",
            EventType.UPDATE_STARTED: "⬆️",
            EventType.UPDATE_COMPLETED: "✅",
            EventType.UPDATE_FAILED: "❌",
            EventType.SCAN: "🔍"
        }
        return icons.get(event_type, "📝")
    
    def export_logs(self, format: str = "csv") -> str:
        """Export logs to file"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"ironwall_logs_{timestamp}.{format}"
        
        if format == "csv":
            import csv
            with open(filename, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(['Timestamp', 'Event Type', 'Description', 'Status', 'Severity', 'Details'])
                for log in self.logs:
                    writer.writerow([
                        log.get('timestamp', ''),
                        log.get('event_type', ''),
                        log.get('description', ''),
                        log.get('status', ''),
                        log.get('severity', ''),
                        log.get('details', '')
                    ])
        elif format == "json":
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(self.logs, f, indent=2, ensure_ascii=False)
        
        return filename
    
    def clear_logs(self):
        """Clear all logs"""
        self.logs = []
        self.save_logs()
    
    def set_retention_policy(self, days: int):
        """Set log retention policy (keep logs for specified days)"""
        if days <= 0:
            return
        
        cutoff_date = datetime.now() - timedelta(days=days)
        self.logs = [
            log for log in self.logs
            if datetime.strptime(log.get('timestamp', ''), '%Y-%m-%d %H:%M:%S') > cutoff_date
        ]
        self.save_logs()

# Global logger instance
logger = Logger() 