"""
IronWall Antivirus - Ransomware Shield Module
Monitor encryption activity and auto-backup protected files before modification
"""

import os
import shutil
import hashlib
import json
import threading
import time
from typing import Dict, List, Optional, Any, Set
from datetime import datetime, timedelta
import psutil
import re
from pathlib import Path
import logging

class RansomwareShield:
    def __init__(self, backup_dir: str = None, protected_dirs: List[str] = None):
        self.backup_dir = backup_dir or os.path.join(os.path.dirname(__file__), '..', '..', 'backups')
        self.protected_dirs = protected_dirs or [
            os.path.expanduser('~/Documents'),
            os.path.expanduser('~/Desktop'),
            os.path.expanduser('~/Pictures'),
            os.path.expanduser('~/Videos'),
            os.path.expanduser('~/Music'),
            os.path.expanduser('~/Downloads')
        ]
        
        # Create backup directory
        os.makedirs(self.backup_dir, exist_ok=True)
        
        # Monitoring state
        self.monitoring = False
        self.monitor_thread = None
        
        # File monitoring
        self.file_hashes = {}
        self.file_backups = {}
        self.suspicious_activities = []
        self.blocked_operations = []
        
        # Ransomware detection patterns
        self.encryption_patterns = {
            'file_extensions': [
                '.encrypted', '.locked', '.crypto', '.crypt', '.cryptolocker',
                '.wannacry', '.petya', '.locky', '.cerber', '.cryptowall',
                '.teslacrypt', '.cryptobit', '.cryptodefense', '.cryptoshield',
                '.encrypt', '.decrypt', '.ransom', '.bitcoin', '.payment',
                '.wallet', '.encrypted_files', '.decrypt_files', '.pay_ransom'
            ],
            'process_names': [
                'cryptolocker', 'wannacry', 'petya', 'locky', 'cerber',
                'cryptowall', 'teslacrypt', 'cryptobit', 'cryptodefense',
                'cryptoshield', 'encrypt', 'decrypt', 'ransom', 'bitcoin',
                'payment', 'wallet', 'encrypted_files', 'decrypt_files'
            ],
            'file_content_patterns': [
                r'encrypt', r'decrypt', r'ransom', r'bitcoin', r'payment',
                r'wallet', r'encrypted', r'locked', r'crypto', r'crypt',
                r'pay_ransom', r'decrypt_files', r'encrypted_files'
            ],
            'suspicious_operations': [
                'mass_file_creation', 'mass_file_modification', 'mass_file_deletion',
                'file_encryption', 'file_renaming', 'file_moving'
            ]
        }
        
        # Protection settings
        self.protection_settings = {
            'auto_backup': True,
            'backup_interval': 300,  # 5 minutes
            'max_backup_size': 1024 * 1024 * 1024,  # 1GB
            'block_suspicious': True,
            'alert_on_detection': True,
            'monitor_file_changes': True,
            'monitor_process_activity': True,
            'protected_file_types': [
                '.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx',
                '.pdf', '.txt', '.rtf', '.odt', '.ods', '.odp',
                '.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff',
                '.mp3', '.mp4', '.avi', '.mov', '.wmv', '.flv',
                '.zip', '.rar', '.7z', '.tar', '.gz'
            ]
        }
        
        # Initialize logging
        self.logger = self._setup_logging()
        
        # Load existing file hashes
        self._load_file_hashes()
        
        # Start monitoring
        self.start_monitoring()
    
    def _setup_logging(self) -> logging.Logger:
        """Setup logging for ransomware shield"""
        logger = logging.getLogger('IronWall_RansomwareShield')
        logger.setLevel(logging.DEBUG)
        
        # Create handlers
        log_file = os.path.join(self.backup_dir, 'ransomware_shield.log')
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.DEBUG)
        
        # Create formatter
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(formatter)
        
        # Add handler to logger
        logger.addHandler(file_handler)
        
        return logger
    
    def _load_file_hashes(self):
        """Load existing file hashes from backup"""
        try:
            hash_file = os.path.join(self.backup_dir, 'file_hashes.json')
            if os.path.exists(hash_file):
                with open(hash_file, 'r') as f:
                    self.file_hashes = json.load(f)
                print(f"Ransomware Shield: Loaded {len(self.file_hashes)} file hashes")
        except Exception as e:
            print(f"Ransomware Shield: Error loading file hashes: {e}")
    
    def _save_file_hashes(self):
        """Save file hashes to backup"""
        try:
            hash_file = os.path.join(self.backup_dir, 'file_hashes.json')
            with open(hash_file, 'w') as f:
                json.dump(self.file_hashes, f, indent=2)
        except Exception as e:
            print(f"Ransomware Shield: Error saving file hashes: {e}")
    
    def start_monitoring(self):
        """Start ransomware monitoring"""
        if not self.monitoring:
            self.monitoring = True
            self.monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
            self.monitor_thread.start()
            print("Ransomware Shield: Started monitoring")
    
    def stop_monitoring(self):
        """Stop ransomware monitoring"""
        self.monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=1)
            print("Ransomware Shield: Stopped monitoring")
    
    def _monitor_loop(self):
        """Main monitoring loop"""
        while self.monitoring:
            try:
                # Monitor file changes
                if self.protection_settings['monitor_file_changes']:
                    self._monitor_file_changes()
                
                # Monitor process activity
                if self.protection_settings['monitor_process_activity']:
                    self._monitor_process_activity()
                
                # Create periodic backups
                if self.protection_settings['auto_backup']:
                    self._create_periodic_backups()
                
                # Sleep before next check
                time.sleep(10)
                
            except Exception as e:
                self.logger.error(f"Error in monitoring loop: {e}")
                time.sleep(30)
    
    def _monitor_file_changes(self):
        """Monitor file changes in protected directories"""
        try:
            for protected_dir in self.protected_dirs:
                if os.path.exists(protected_dir):
                    self._scan_directory(protected_dir)
                    
        except Exception as e:
            self.logger.error(f"Error monitoring file changes: {e}")
    
    def _scan_directory(self, directory: str):
        """Scan directory for file changes"""
        try:
            for root, dirs, files in os.walk(directory):
                for file in files:
                    file_path = os.path.join(root, file)
                    
                    # Check if file is protected
                    if self._is_protected_file(file_path):
                        self._check_file_integrity(file_path)
                        
        except Exception as e:
            self.logger.error(f"Error scanning directory {directory}: {e}")
    
    def _is_protected_file(self, file_path: str) -> bool:
        """Check if file should be protected"""
        try:
            file_ext = os.path.splitext(file_path)[1].lower()
            
            # Check if file type is protected
            if file_ext in self.protection_settings['protected_file_types']:
                return True
            
            # Check file size (protect files under 100MB)
            file_size = os.path.getsize(file_path)
            if file_size < 100 * 1024 * 1024:  # 100MB
                return True
            
            return False
            
        except Exception:
            return False
    
    def _check_file_integrity(self, file_path: str):
        """Check file integrity and detect changes"""
        try:
            if not os.path.exists(file_path):
                return
            
            # Calculate current file hash
            current_hash = self._calculate_file_hash(file_path)
            
            # Check if file hash has changed
            if file_path in self.file_hashes:
                original_hash = self.file_hashes[file_path]['hash']
                
                if current_hash != original_hash:
                    # File has been modified
                    self._handle_file_modification(file_path, original_hash, current_hash)
            else:
                # New file, add to hash database
                self.file_hashes[file_path] = {
                    'hash': current_hash,
                    'size': os.path.getsize(file_path),
                    'modified_time': os.path.getmtime(file_path),
                    'first_seen': datetime.now().isoformat()
                }
                
        except Exception as e:
            self.logger.error(f"Error checking file integrity {file_path}: {e}")
    
    def _calculate_file_hash(self, file_path: str) -> str:
        """Calculate MD5 hash of file"""
        try:
            with open(file_path, 'rb') as f:
                return hashlib.md5(f.read()).hexdigest()
        except Exception:
            return ""
    
    def _handle_file_modification(self, file_path: str, original_hash: str, current_hash: str):
        """Handle file modification"""
        try:
            # Check if modification is suspicious
            if self._is_suspicious_modification(file_path):
                self._handle_suspicious_modification(file_path, original_hash, current_hash)
            else:
                # Normal modification, update hash
                self.file_hashes[file_path]['hash'] = current_hash
                self.file_hashes[file_path]['modified_time'] = os.path.getmtime(file_path)
                
        except Exception as e:
            self.logger.error(f"Error handling file modification {file_path}: {e}")
    
    def _is_suspicious_modification(self, file_path: str) -> bool:
        """Check if file modification is suspicious"""
        try:
            file_name = os.path.basename(file_path).lower()
            file_ext = os.path.splitext(file_path)[1].lower()
            
            # Check for suspicious file extensions
            for pattern in self.encryption_patterns['file_extensions']:
                if pattern in file_name or file_ext == pattern:
                    return True
            
            # Check for suspicious content patterns
            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read(4096)  # Read first 4KB
                    
                for pattern in self.encryption_patterns['file_content_patterns']:
                    if re.search(pattern, content, re.IGNORECASE):
                        return True
            except:
                pass
            
            # Check for rapid modifications
            if file_path in self.file_hashes:
                last_modified = self.file_hashes[file_path].get('modified_time', 0)
                current_time = time.time()
                
                if current_time - last_modified < 60:  # Modified within last minute
                    return True
            
            return False
            
        except Exception:
            return False
    
    def _handle_suspicious_modification(self, file_path: str, original_hash: str, current_hash: str):
        """Handle suspicious file modification"""
        try:
            # Create backup of original file
            backup_path = self._create_file_backup(file_path, original_hash)
            
            # Log suspicious activity
            suspicious_activity = {
                'timestamp': datetime.now().isoformat(),
                'file_path': file_path,
                'original_hash': original_hash,
                'current_hash': current_hash,
                'backup_path': backup_path,
                'activity_type': 'suspicious_modification',
                'severity': 'high'
            }
            
            self.suspicious_activities.append(suspicious_activity)
            
            # Block the operation if enabled
            if self.protection_settings['block_suspicious']:
                self._block_file_operation(file_path)
            
            # Alert if enabled
            if self.protection_settings['alert_on_detection']:
                self._send_alert(suspicious_activity)
            
            self.logger.warning(f"Suspicious file modification detected: {file_path}")
            
        except Exception as e:
            self.logger.error(f"Error handling suspicious modification {file_path}: {e}")
    
    def _create_file_backup(self, file_path: str, original_hash: str) -> str:
        """Create backup of file"""
        try:
            # Create backup directory structure
            backup_time = datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_subdir = os.path.join(self.backup_dir, backup_time)
            os.makedirs(backup_subdir, exist_ok=True)
            
            # Create backup filename
            file_name = os.path.basename(file_path)
            backup_name = f"{original_hash}_{file_name}"
            backup_path = os.path.join(backup_subdir, backup_name)
            
            # Copy file to backup
            shutil.copy2(file_path, backup_path)
            
            # Store backup information
            self.file_backups[file_path] = {
                'backup_path': backup_path,
                'original_hash': original_hash,
                'backup_time': backup_time,
                'file_size': os.path.getsize(backup_path)
            }
            
            return backup_path
            
        except Exception as e:
            self.logger.error(f"Error creating file backup {file_path}: {e}")
            return ""
    
    def _block_file_operation(self, file_path: str):
        """Block file operation"""
        try:
            # Try to restore file from backup
            if file_path in self.file_backups:
                backup_path = self.file_backups[file_path]['backup_path']
                if os.path.exists(backup_path):
                    shutil.copy2(backup_path, file_path)
                    print(f"Ransomware Shield: Restored {file_path} from backup")
            
            # Log blocked operation
            blocked_operation = {
                'timestamp': datetime.now().isoformat(),
                'file_path': file_path,
                'operation': 'modification',
                'action': 'blocked_and_restored'
            }
            
            self.blocked_operations.append(blocked_operation)
            
        except Exception as e:
            self.logger.error(f"Error blocking file operation {file_path}: {e}")
    
    def _send_alert(self, activity: Dict[str, Any]):
        """Send alert about suspicious activity"""
        try:
            alert_message = f"""
RANSOMWARE SHIELD ALERT
=======================
Time: {activity['timestamp']}
File: {activity['file_path']}
Activity: {activity['activity_type']}
Severity: {activity['severity']}
Backup: {activity.get('backup_path', 'N/A')}
            """
            
            print(alert_message)
            self.logger.warning(alert_message)
            
        except Exception as e:
            self.logger.error(f"Error sending alert: {e}")
    
    def _monitor_process_activity(self):
        """Monitor process activity for suspicious behavior"""
        try:
            for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
                try:
                    proc_info = proc.info
                    process_name = proc_info['name'].lower()
                    
                    # Check for suspicious process names
                    for pattern in self.encryption_patterns['process_names']:
                        if pattern in process_name:
                            self._handle_suspicious_process(proc_info)
                            break
                    
                    # Check for suspicious command line
                    cmdline = ' '.join(proc_info['cmdline']) if proc_info['cmdline'] else ''
                    for pattern in self.encryption_patterns['file_content_patterns']:
                        if re.search(pattern, cmdline, re.IGNORECASE):
                            self._handle_suspicious_process(proc_info)
                            break
                            
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
                    
        except Exception as e:
            self.logger.error(f"Error monitoring process activity: {e}")
    
    def _handle_suspicious_process(self, proc_info: Dict[str, Any]):
        """Handle suspicious process"""
        try:
            suspicious_activity = {
                'timestamp': datetime.now().isoformat(),
                'process_name': proc_info['name'],
                'process_id': proc_info['pid'],
                'command_line': ' '.join(proc_info['cmdline']) if proc_info['cmdline'] else '',
                'activity_type': 'suspicious_process',
                'severity': 'high'
            }
            
            self.suspicious_activities.append(suspicious_activity)
            
            # Block the process if enabled
            if self.protection_settings['block_suspicious']:
                self._block_suspicious_process(proc_info['pid'])
            
            # Alert if enabled
            if self.protection_settings['alert_on_detection']:
                self._send_alert(suspicious_activity)
            
            self.logger.warning(f"Suspicious process detected: {proc_info['name']} (PID: {proc_info['pid']})")
            
        except Exception as e:
            self.logger.error(f"Error handling suspicious process: {e}")
    
    def _block_suspicious_process(self, pid: int):
        """Block suspicious process"""
        try:
            process = psutil.Process(pid)
            process.terminate()
            
            # Log blocked operation
            blocked_operation = {
                'timestamp': datetime.now().isoformat(),
                'process_id': pid,
                'process_name': process.name(),
                'operation': 'termination',
                'action': 'blocked'
            }
            
            self.blocked_operations.append(blocked_operation)
            
            print(f"Ransomware Shield: Terminated suspicious process {pid}")
            
        except Exception as e:
            self.logger.error(f"Error blocking suspicious process {pid}: {e}")
    
    def _create_periodic_backups(self):
        """Create periodic backups of important files"""
        try:
            current_time = time.time()
            
            for file_path, file_info in self.file_hashes.items():
                if os.path.exists(file_path):
                    last_backup = file_info.get('last_backup', 0)
                    
                    # Create backup if enough time has passed
                    if current_time - last_backup > self.protection_settings['backup_interval']:
                        self._create_file_backup(file_path, file_info['hash'])
                        file_info['last_backup'] = current_time
            
            # Save updated hashes
            self._save_file_hashes()
            
        except Exception as e:
            self.logger.error(f"Error creating periodic backups: {e}")
    
    def add_protected_directory(self, directory: str):
        """Add directory to protected list"""
        if directory not in self.protected_dirs:
            self.protected_dirs.append(directory)
            print(f"Ransomware Shield: Added {directory} to protected directories")
    
    def remove_protected_directory(self, directory: str):
        """Remove directory from protected list"""
        if directory in self.protected_dirs:
            self.protected_dirs.remove(directory)
            print(f"Ransomware Shield: Removed {directory} from protected directories")
    
    def get_protection_stats(self) -> Dict[str, Any]:
        """Get ransomware protection statistics"""
        return {
            'monitoring_active': self.monitoring,
            'protected_directories': len(self.protected_dirs),
            'protected_files': len(self.file_hashes),
            'file_backups': len(self.file_backups),
            'suspicious_activities': len(self.suspicious_activities),
            'blocked_operations': len(self.blocked_operations),
            'backup_directory': self.backup_dir,
            'last_update': datetime.now().isoformat()
        }
    
    def get_suspicious_activities(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Get suspicious activities"""
        return self.suspicious_activities[-limit:]
    
    def get_blocked_operations(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Get blocked operations"""
        return self.blocked_operations[-limit:]
    
    def restore_file(self, file_path: str) -> bool:
        """Restore file from backup"""
        try:
            if file_path in self.file_backups:
                backup_path = self.file_backups[file_path]['backup_path']
                if os.path.exists(backup_path):
                    shutil.copy2(backup_path, file_path)
                    print(f"Ransomware Shield: Restored {file_path} from backup")
                    return True
                else:
                    print(f"Ransomware Shield: Backup not found for {file_path}")
                    return False
            else:
                print(f"Ransomware Shield: No backup found for {file_path}")
                return False
                
        except Exception as e:
            self.logger.error(f"Error restoring file {file_path}: {e}")
            return False
    
    def clear_logs(self):
        """Clear all logs"""
        self.suspicious_activities.clear()
        self.blocked_operations.clear()
        print("Ransomware Shield: All logs cleared")
    
    def cleanup_old_backups(self, days: int = 30):
        """Clean up old backups"""
        try:
            cutoff_time = time.time() - (days * 24 * 3600)
            removed_count = 0
            
            for backup_info in self.file_backups.values():
                backup_path = backup_info['backup_path']
                if os.path.exists(backup_path):
                    backup_time = os.path.getmtime(backup_path)
                    if backup_time < cutoff_time:
                        os.remove(backup_path)
                        removed_count += 1
            
            print(f"Ransomware Shield: Cleaned up {removed_count} old backups")
            
        except Exception as e:
            self.logger.error(f"Error cleaning up old backups: {e}") 