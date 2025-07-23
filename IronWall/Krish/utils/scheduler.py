"""
IronWall Antivirus - Scheduler Module
Handles scheduled scan routines and automation
"""

import os
import json
import uuid
import time
import threading
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Callable
from dataclasses import dataclass, asdict, field
from enum import Enum

class ScanType(Enum):
    DAILY_QUICK = "Daily Quick Scan"
    BOOT_SCAN = "Boot Scan"
    CUSTOM_SCAN = "Custom Scan"

class ScheduleStatus(Enum):
    ENABLED = "enabled"
    DISABLED = "disabled"
    RUNNING = "running"
    MISSED = "missed"
    FAILED = "failed"

@dataclass
class ScheduledScan:
    """Data class for a scheduled scan"""
    id: str = ''
    name: str = ''
    scan_type: str = ''  # 'Daily Quick', 'Boot', 'Custom'
    enabled: bool = True
    time: str = ''  # HH:MM format
    day: str = ''  # For weekly scans: 'Monday', 'Tuesday', etc.
    repeat: str = 'Once'  # 'Once', 'Daily', 'Weekly', 'Monthly'
    custom_paths: List[str] = field(default_factory=list)
    last_run: str = ''  # ISO format timestamp
    status: str = 'Pending'  # 'Pending', 'Running', 'Success', 'Failed', 'Skipped'
    last_duration: int = 0  # seconds
    last_threats: int = 0
    missed_runs: int = 0
    created_at: str = ''
    updated_at: str = ''
    
    def __post_init__(self):
        if not self.created_at:
            self.created_at = datetime.now().isoformat()
        if not self.updated_at:
            self.updated_at = datetime.now().isoformat()

class SchedulerManager:
    """Manages scheduled scan routines"""
    
    def __init__(self, data_file: str = None):
        if data_file is None:
            data_file = os.path.join(os.path.dirname(__file__), '..', 'scheduled_scans.json')
        self.data_file = data_file
        self.schedules: List[ScheduledScan] = []
        self.scheduler_thread = None
        self.running = False
        self.scan_callback: Optional[Callable] = None
        self.load_schedules()
        
    def load_schedules(self):
        """Load scheduled scans from JSON file"""
        try:
            if os.path.exists(self.data_file):
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    sanitized = []
                    string_fields = ['id', 'name', 'scan_type', 'time', 'day', 'repeat', 'last_run', 'status', 'created_at', 'updated_at']
                    list_fields = ['custom_paths']
                    int_fields = ['last_duration', 'last_threats', 'missed_runs']
                    bool_fields = ['enabled']
                    for schedule in data:
                        for key in string_fields:
                            if key not in schedule or schedule[key] is None:
                                schedule[key] = ''
                        for key in list_fields:
                            if key not in schedule or schedule[key] is None:
                                schedule[key] = []
                        for key in int_fields:
                            if key not in schedule or schedule[key] is None:
                                schedule[key] = 0
                        for key in bool_fields:
                            if key not in schedule or schedule[key] is None:
                                schedule[key] = False
                        sanitized.append(ScheduledScan(**schedule))
                    self.schedules = sanitized
                print(f"Loaded {len(self.schedules)} scheduled scans")
            else:
                self.schedules = []
                print("No scheduled scans file found, starting fresh")
        except Exception as e:
            print(f"Error loading scheduled scans: {e}")
            self.schedules = []
    
    def save_schedules(self):
        """Save scheduled scans to JSON file"""
        try:
            data = [asdict(schedule) for schedule in self.schedules]
            with open(self.data_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            print(f"Saved {len(self.schedules)} scheduled scans")
        except Exception as e:
            print(f"Error saving scheduled scans: {e}")
    
    def add_schedule(self, name: str, scan_type: str, time: str, day: str = '', 
                    repeat: str = 'Once', custom_paths: List[str] = None, enabled: bool = True) -> str:
        """Add a new scheduled scan"""
        # Ensure all fields are not None
        name = name or ''
        scan_type = scan_type or ''
        time = time or ''
        day = day or ''
        repeat = repeat or 'Once'
        custom_paths = custom_paths if custom_paths is not None else []
        schedule_id = str(uuid.uuid4())
        schedule = ScheduledScan(
            id=schedule_id,
            name=name,
            scan_type=scan_type,
            enabled=enabled,
            time=time,
            day=day,
            repeat=repeat,
            custom_paths=custom_paths,
            last_run='',
            status='Pending',
            last_duration=0,
            last_threats=0,
            missed_runs=0,
            created_at='',
            updated_at=''
        )
        self.schedules.append(schedule)
        self.save_schedules()
        print(f"Added scheduled scan: {name} ({scan_type})")
        return schedule_id
    
    def edit_schedule(self, schedule_id: str, **kwargs) -> bool:
        """Edit an existing scheduled scan"""
        for schedule in self.schedules:
            if schedule.id == schedule_id:
                for key, value in kwargs.items():
                    if hasattr(schedule, key):
                        # Ensure no None for str/list fields
                        if key in ['id', 'name', 'scan_type', 'time', 'day', 'repeat', 'last_run', 'status', 'created_at', 'updated_at']:
                            value = value if value is not None else ''
                        if key == 'custom_paths':
                            value = value if value is not None else []
                        setattr(schedule, key, value)
                schedule.updated_at = datetime.now().isoformat()
                self.save_schedules()
                print(f"Edited scheduled scan: {schedule.name}")
                return True
        print(f"Schedule not found for editing: {schedule_id}")
        return False
    
    def delete_schedule(self, schedule_id: str) -> bool:
        """Delete a scheduled scan"""
        for i, schedule in enumerate(self.schedules):
            if schedule.id == schedule_id:
                deleted_name = schedule.name
                del self.schedules[i]
                self.save_schedules()
                print(f"Deleted scheduled scan: {deleted_name}")
                return True
        print(f"Schedule not found for deletion: {schedule_id}")
        return False
    
    def get_schedule(self, schedule_id: str) -> Optional[ScheduledScan]:
        """Get a specific scheduled scan by ID"""
        for schedule in self.schedules:
            if schedule.id == schedule_id:
                return schedule
        return None
    
    def get_all_schedules(self) -> List[ScheduledScan]:
        """Get all scheduled scans"""
        return self.schedules.copy()
    
    def get_enabled_schedules(self) -> List[ScheduledScan]:
        """Get only enabled scheduled scans"""
        return [s for s in self.schedules if s.enabled]
    
    def toggle_schedule(self, schedule_id: str) -> bool:
        """Toggle enabled/disabled status of a schedule"""
        for schedule in self.schedules:
            if schedule.id == schedule_id:
                schedule.enabled = not schedule.enabled
                schedule.updated_at = datetime.now().isoformat()
                self.save_schedules()
                status = "enabled" if schedule.enabled else "disabled"
                print(f"Schedule {status}: {schedule.name}")
                return True
        return False
    
    def mark_schedule_run(self, schedule_id: str, status: str = 'Success', 
                         duration: int = 0, threats: int = 0):
        """Mark a schedule as run with results"""
        for schedule in self.schedules:
            if schedule.id == schedule_id:
                schedule.last_run = datetime.now().isoformat()
                schedule.status = status if status is not None else ''
                schedule.last_duration = duration
                schedule.last_threats = threats
                schedule.updated_at = datetime.now().isoformat()
                self.save_schedules()
                print(f"Marked schedule run: {schedule.name} - {status}")
                return True
        return False
    
    def mark_schedule_missed(self, schedule_id: str):
        """Mark a schedule as missed"""
        for schedule in self.schedules:
            if schedule.id == schedule_id:
                schedule.missed_runs += 1
                schedule.status = 'Missed'
                schedule.updated_at = datetime.now().isoformat()
                self.save_schedules()
                print(f"Marked schedule missed: {schedule.name}")
                return True
        return False
    
    def get_due_schedules(self) -> List[ScheduledScan]:
        """Get schedules that are due to run"""
        now = datetime.now()
        due_schedules = []
        
        for schedule in self.get_enabled_schedules():
            if self._is_schedule_due(schedule, now):
                due_schedules.append(schedule)
        
        return due_schedules
    
    def _is_schedule_due(self, schedule: ScheduledScan, now: datetime) -> bool:
        """Check if a schedule is due to run"""
        try:
            # Parse schedule time
            schedule_time = datetime.strptime(schedule.time, '%H:%M').time()
            schedule_datetime = datetime.combine(now.date(), schedule_time)
            
            # Check if it's the right day
            if schedule.day:
                if now.strftime('%A') != schedule.day:
                    return False
            
            # Check if it's the right time (within 1 minute window)
            time_diff = abs((now - schedule_datetime).total_seconds())
            if time_diff > 60:  # More than 1 minute off
                return False
            
            # Check if it was already run today
            if schedule.last_run:
                last_run = datetime.fromisoformat(schedule.last_run)
                if last_run.date() == now.date():
                    return False
            
            return True
            
        except Exception as e:
            print(f"Error checking if schedule is due: {e}")
            return False
    
    def get_schedule_statistics(self) -> Dict:
        """Get statistics about scheduled scans"""
        total = len(self.schedules)
        enabled = len(self.get_enabled_schedules())
        running = len([s for s in self.schedules if s.status == 'Running'])
        success = len([s for s in self.schedules if s.status == 'Success'])
        failed = len([s for s in self.schedules if s.status == 'Failed'])
        missed = sum(s.missed_runs for s in self.schedules)
        
        # Get upcoming schedules (next 24 hours)
        upcoming = []
        now = datetime.now()
        for schedule in self.get_enabled_schedules():
            try:
                schedule_time = datetime.strptime(schedule.time, '%H:%M').time()
                schedule_datetime = datetime.combine(now.date(), schedule_time)
                
                # If time has passed today, check tomorrow
                if schedule_datetime < now:
                    schedule_datetime += timedelta(days=1)
                
                if schedule_datetime - now <= timedelta(days=1):
                    upcoming.append({
                        'id': schedule.id,
                        'name': schedule.name,
                        'type': schedule.scan_type,
                        'time': schedule.time,
                        'day': schedule.day,
                        'next_run': schedule_datetime.isoformat()
                    })
            except Exception as e:
                print(f"Error calculating upcoming schedule: {e}")
        
        return {
            'total': total,
            'enabled': enabled,
            'running': running,
            'success': success,
            'failed': failed,
            'missed': missed,
            'upcoming': upcoming
        }
    
    def set_scan_callback(self, callback: Callable):
        """Set the callback function to execute when a scan is due"""
        self.scan_callback = callback
    
    def start_scheduler(self):
        """Start the scheduler background thread"""
        if self.running:
            return
        
        self.running = True
        self.scheduler_thread = threading.Thread(target=self._scheduler_loop, daemon=True)
        self.scheduler_thread.start()
        print("Scheduler started")
    
    def stop_scheduler(self):
        """Stop the scheduler background thread"""
        self.running = False
        if self.scheduler_thread:
            self.scheduler_thread.join(timeout=5)
        print("Scheduler stopped")
    
    def _scheduler_loop(self):
        """Main scheduler loop that checks for due scans"""
        while self.running:
            try:
                due_schedules = self.get_due_schedules()
                
                for schedule in due_schedules:
                    if not self.running:
                        break
                    
                    print(f"Executing scheduled scan: {schedule.name}")
                    
                    # Mark as running
                    self.mark_schedule_run(schedule.id, 'Running')
                    
                    # Execute the scan if callback is set
                    if self.scan_callback:
                        try:
                            # Call the scan callback with schedule details
                            self.scan_callback(schedule)
                        except Exception as e:
                            print(f"Error executing scheduled scan {schedule.name}: {e}")
                            self.mark_schedule_run(schedule.id, 'Failed')
                    else:
                        print("No scan callback set, cannot execute scheduled scan")
                        self.mark_schedule_run(schedule.id, 'Failed')
                
                # Sleep for 1 minute before next check
                time.sleep(60)
                
            except Exception as e:
                print(f"Error in scheduler loop: {e}")
                time.sleep(60)  # Continue after error
    
    def create_default_schedules(self):
        """Create default scheduled scans if none exist"""
        if self.schedules:
            return
        self.add_schedule(
            name="Daily Quick Scan",
            scan_type="Daily Quick",
            time="09:00",
            repeat="Daily",
            enabled=True
        )
        print("Created default scheduled scans")
    
    def validate_schedule(self, name: str, scan_type: str, time: str, 
                         day: str = None, repeat: str = 'Once') -> tuple[bool, str]:
        """Validate schedule parameters"""
        # Check name
        if not name or len(name.strip()) == 0:
            return False, "Schedule name is required"
        
        # Check for duplicate names
        for schedule in self.schedules:
            if schedule.name.lower() == name.lower():
                return False, "Schedule name already exists"
        
        # Validate time format
        try:
            datetime.strptime(time, '%H:%M')
        except ValueError:
            return False, "Time must be in HH:MM format"
        
        # Validate day for weekly scans
        if repeat == 'Weekly' and not day:
            return False, "Day is required for weekly scans"
        
        if day and day not in ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']:
            return False, "Invalid day name"
        
        # Validate scan type
        valid_types = ['Daily Quick', 'Boot', 'Custom']
        if scan_type not in valid_types:
            return False, f"Invalid scan type. Must be one of: {', '.join(valid_types)}"
        
        return True, "Valid" 