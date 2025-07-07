"""
IronWall Antivirus - Restore Point Creator Module
Create system restore points before critical actions
"""

import os
import subprocess
import json
import time
from typing import Dict, List, Optional, Any
from datetime import datetime
import platform
import threading

class RestorePointCreator:
    def __init__(self, restore_points_dir: str = None):
        self.restore_points_dir = restore_points_dir or os.path.join(os.path.dirname(__file__), '..', '..', 'restore_points')
        
        # Create restore points directory
        os.makedirs(self.restore_points_dir, exist_ok=True)
        
        # Restore points database
        self.restore_points_db = os.path.join(self.restore_points_dir, 'restore_points.json')
        self.restore_points = self._load_restore_points()
        
        # System information
        self.system_info = self._get_system_info()
        
        # Restore point settings
        self.settings = {
            'auto_create': True,
            'max_restore_points': 10,
            'min_disk_space': 1024 * 1024 * 1024,  # 1GB
            'description_template': 'IronWall Antivirus - {action} - {timestamp}',
            'critical_actions': [
                'system_scan', 'quarantine_operation', 'file_restoration',
                'registry_modification', 'service_installation', 'driver_installation'
            ]
        }
        
        # Windows-specific settings
        if platform.system() == 'Windows':
            self.settings.update({
                'use_windows_restore': True,
                'vss_enabled': self._check_vss_service(),
                'restore_point_type': 'MODIFY_SETTINGS'
            })
        else:
            self.settings.update({
                'use_windows_restore': False,
                'vss_enabled': False,
                'restore_point_type': 'CUSTOM'
            })
    
    def _load_restore_points(self) -> List[Dict[str, Any]]:
        """Load restore points from database"""
        try:
            if os.path.exists(self.restore_points_db):
                with open(self.restore_points_db, 'r') as f:
                    return json.load(f)
            else:
                return []
        except Exception as e:
            print(f"Restore Point Creator: Error loading restore points: {e}")
            return []
    
    def _save_restore_points(self):
        """Save restore points to database"""
        try:
            with open(self.restore_points_db, 'w') as f:
                json.dump(self.restore_points, f, indent=2)
        except Exception as e:
            print(f"Restore Point Creator: Error saving restore points: {e}")
    
    def _get_system_info(self) -> Dict[str, Any]:
        """Get system information"""
        try:
            return {
                'platform': platform.system(),
                'platform_version': platform.version(),
                'architecture': platform.architecture()[0],
                'processor': platform.processor(),
                'hostname': platform.node(),
                'python_version': platform.python_version(),
                'timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            print(f"Restore Point Creator: Error getting system info: {e}")
            return {}
    
    def _check_vss_service(self) -> bool:
        """Check if Volume Shadow Copy Service is available (Windows)"""
        if platform.system() != 'Windows':
            return False
        
        try:
            # Check if VSS service is running
            result = subprocess.run(
                ['sc', 'query', 'VSS'],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            return 'RUNNING' in result.stdout
            
        except Exception:
            return False
    
    def create_restore_point(self, action: str, description: str = None) -> Optional[str]:
        """Create a system restore point"""
        try:
            # Check if we should create restore point
            if not self.settings['auto_create']:
                return None
            
            # Check available disk space
            if not self._check_disk_space():
                print("Restore Point Creator: Insufficient disk space for restore point")
                return None
            
            # Generate description
            if description is None:
                description = self.settings['description_template'].format(
                    action=action,
                    timestamp=datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                )
            
            # Create restore point based on platform
            if platform.system() == 'Windows' and self.settings['use_windows_restore']:
                restore_point_id = self._create_windows_restore_point(description)
            else:
                restore_point_id = self._create_custom_restore_point(action, description)
            
            if restore_point_id:
                # Add to database
                restore_point_info = {
                    'id': restore_point_id,
                    'action': action,
                    'description': description,
                    'created_at': datetime.now().isoformat(),
                    'system_info': self.system_info,
                    'type': 'windows' if platform.system() == 'Windows' else 'custom'
                }
                
                self.restore_points.append(restore_point_info)
                self._save_restore_points()
                
                # Clean up old restore points
                self._cleanup_old_restore_points()
                
                print(f"Restore Point Creator: Created restore point {restore_point_id}")
                return restore_point_id
            else:
                print("Restore Point Creator: Failed to create restore point")
                return None
                
        except Exception as e:
            print(f"Restore Point Creator: Error creating restore point: {e}")
            return None
    
    def _create_windows_restore_point(self, description: str) -> Optional[str]:
        """Create Windows system restore point using VSS"""
        try:
            if not self.settings['vss_enabled']:
                print("Restore Point Creator: VSS service not available")
                return None
            
            # Create restore point using PowerShell
            powershell_script = f"""
$restorePoint = New-Object -ComObject SystemRestore.RestorePoint
$restorePoint.Description = "{description}"
$restorePoint.RestorePointType = {self._get_restore_point_type()}
$restorePoint.EventType = "BEGIN_SYSTEM_CHANGE"
$restorePoint.Create()
            """
            
            result = subprocess.run(
                ['powershell', '-Command', powershell_script],
                capture_output=True,
                text=True,
                timeout=60
            )
            
            if result.returncode == 0:
                # Extract restore point ID from output
                lines = result.stdout.split('\n')
                for line in lines:
                    if 'Restore Point ID:' in line:
                        return line.split(':')[1].strip()
                
                # If we can't extract ID, generate one
                return f"RP_{int(time.time())}"
            else:
                print(f"Restore Point Creator: PowerShell error: {result.stderr}")
                return None
                
        except Exception as e:
            print(f"Restore Point Creator: Error creating Windows restore point: {e}")
            return None
    
    def _create_custom_restore_point(self, action: str, description: str) -> str:
        """Create custom restore point (non-Windows or fallback)"""
        try:
            restore_point_id = f"RP_{int(time.time())}"
            restore_point_dir = os.path.join(self.restore_points_dir, restore_point_id)
            
            # Create restore point directory
            os.makedirs(restore_point_dir, exist_ok=True)
            
            # Save system state information
            system_state = {
                'action': action,
                'description': description,
                'created_at': datetime.now().isoformat(),
                'system_info': self.system_info,
                'critical_files': self._get_critical_files(),
                'registry_backup': self._backup_registry() if platform.system() == 'Windows' else None
            }
            
            # Save system state
            state_file = os.path.join(restore_point_dir, 'system_state.json')
            with open(state_file, 'w') as f:
                json.dump(system_state, f, indent=2)
            
            return restore_point_id
            
        except Exception as e:
            print(f"Restore Point Creator: Error creating custom restore point: {e}")
            return None
    
    def _get_restore_point_type(self) -> int:
        """Get Windows restore point type"""
        restore_point_types = {
            'APPLICATION_INSTALL': 0,
            'APPLICATION_UNINSTALL': 1,
            'DEVICE_DRIVER_INSTALL': 10,
            'MODIFY_SETTINGS': 12,
            'CANCELLED_OPERATION': 13,
            'FIRSTRUN': 90,
            'BACKUP_RECOVERY': 14,
            'CHECKPOINT': 7,
            'DESKTOP_SETTING': 15,
            'ACCESSIBILITY_SETTING': 16,
            'OE_SETTING': 17,
            'APPLICATION_RUN': 18,
            'RESTORE': 19,
            'UNKNOWN': 20,
            'MAXVALUE': 100
        }
        
        return restore_point_types.get(self.settings['restore_point_type'], 12)
    
    def _get_critical_files(self) -> List[Dict[str, Any]]:
        """Get list of critical system files"""
        critical_files = []
        
        try:
            # Windows critical files
            if platform.system() == 'Windows':
                critical_paths = [
                    os.path.join(os.environ.get('WINDIR', 'C:\\Windows'), 'System32'),
                    os.path.join(os.environ.get('WINDIR', 'C:\\Windows'), 'SysWOW64'),
                    os.path.join(os.environ.get('WINDIR', 'C:\\Windows'), 'System32\\drivers'),
                    os.path.join(os.environ.get('WINDIR', 'C:\\Windows'), 'System32\\config')
                ]
                
                for path in critical_paths:
                    if os.path.exists(path):
                        for root, dirs, files in os.walk(path):
                            for file in files[:100]:  # Limit to first 100 files per directory
                                file_path = os.path.join(root, file)
                                try:
                                    file_info = {
                                        'path': file_path,
                                        'size': os.path.getsize(file_path),
                                        'modified': os.path.getmtime(file_path),
                                        'hash': self._calculate_file_hash(file_path)
                                    }
                                    critical_files.append(file_info)
                                except:
                                    continue
            else:
                # Unix-like systems
                critical_paths = [
                    '/etc',
                    '/boot',
                    '/usr/bin',
                    '/usr/sbin'
                ]
                
                for path in critical_paths:
                    if os.path.exists(path):
                        for root, dirs, files in os.walk(path):
                            for file in files[:100]:
                                file_path = os.path.join(root, file)
                                try:
                                    file_info = {
                                        'path': file_path,
                                        'size': os.path.getsize(file_path),
                                        'modified': os.path.getmtime(file_path),
                                        'hash': self._calculate_file_hash(file_path)
                                    }
                                    critical_files.append(file_info)
                                except:
                                    continue
                    
        except Exception as e:
            print(f"Restore Point Creator: Error getting critical files: {e}")
        
        return critical_files
    
    def _calculate_file_hash(self, file_path: str) -> str:
        """Calculate MD5 hash of file"""
        try:
            import hashlib
            with open(file_path, 'rb') as f:
                return hashlib.md5(f.read()).hexdigest()
        except:
            return ""
    
    def _backup_registry(self) -> Optional[str]:
        """Backup Windows registry (if possible)"""
        if platform.system() != 'Windows':
            return None
        
        try:
            # Export critical registry keys
            registry_backup = {}
            critical_keys = [
                r'HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows\CurrentVersion\Run',
                r'HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows\CurrentVersion\RunOnce',
                r'HKEY_CURRENT_USER\SOFTWARE\Microsoft\Windows\CurrentVersion\Run',
                r'HKEY_CURRENT_USER\SOFTWARE\Microsoft\Windows\CurrentVersion\RunOnce'
            ]
            
            for key in critical_keys:
                try:
                    result = subprocess.run(
                        ['reg', 'export', key, 'temp.reg'],
                        capture_output=True,
                        text=True,
                        timeout=30
                    )
                    
                    if result.returncode == 0:
                        registry_backup[key] = result.stdout
                    
                    # Clean up temp file
                    if os.path.exists('temp.reg'):
                        os.remove('temp.reg')
                        
                except Exception:
                    continue
            
            return registry_backup if registry_backup else None
            
        except Exception as e:
            print(f"Restore Point Creator: Error backing up registry: {e}")
            return None
    
    def _check_disk_space(self) -> bool:
        """Check if there's enough disk space for restore point"""
        try:
            import shutil
            total, used, free = shutil.disk_usage(self.restore_points_dir)
            return free >= self.settings['min_disk_space']
        except Exception:
            return True  # Assume enough space if we can't check
    
    def _cleanup_old_restore_points(self):
        """Clean up old restore points"""
        try:
            max_points = self.settings['max_restore_points']
            
            if len(self.restore_points) > max_points:
                # Remove oldest restore points
                old_points = self.restore_points[:-max_points]
                
                for point in old_points:
                    self._delete_restore_point(point['id'])
                
                # Update database
                self.restore_points = self.restore_points[-max_points:]
                self._save_restore_points()
                
                print(f"Restore Point Creator: Cleaned up {len(old_points)} old restore points")
                
        except Exception as e:
            print(f"Restore Point Creator: Error cleaning up restore points: {e}")
    
    def _delete_restore_point(self, restore_point_id: str):
        """Delete a restore point"""
        try:
            # Delete Windows restore point
            if platform.system() == 'Windows' and self.settings['use_windows_restore']:
                powershell_script = f"""
$restorePoint = Get-ComputerRestorePoint | Where-Object {{ $_.Description -like "*{restore_point_id}*" }}
if ($restorePoint) {{
    Remove-ComputerRestorePoint -RestorePoint $restorePoint.SequenceNumber
}}
                """
                
                subprocess.run(
                    ['powershell', '-Command', powershell_script],
                    capture_output=True,
                    timeout=30
                )
            
            # Delete custom restore point directory
            restore_point_dir = os.path.join(self.restore_points_dir, restore_point_id)
            if os.path.exists(restore_point_dir):
                import shutil
                shutil.rmtree(restore_point_dir)
                
        except Exception as e:
            print(f"Restore Point Creator: Error deleting restore point {restore_point_id}: {e}")
    
    def list_restore_points(self) -> List[Dict[str, Any]]:
        """List all available restore points"""
        return self.restore_points.copy()
    
    def get_restore_point_info(self, restore_point_id: str) -> Optional[Dict[str, Any]]:
        """Get information about a specific restore point"""
        for point in self.restore_points:
            if point['id'] == restore_point_id:
                return point
        return None
    
    def restore_system(self, restore_point_id: str) -> bool:
        """Restore system to a specific restore point"""
        try:
            restore_point = self.get_restore_point_info(restore_point_id)
            if not restore_point:
                print(f"Restore Point Creator: Restore point {restore_point_id} not found")
                return False
            
            print(f"Restore Point Creator: Restoring system to {restore_point_id}")
            
            # Restore based on type
            if restore_point['type'] == 'windows':
                return self._restore_windows_system(restore_point_id)
            else:
                return self._restore_custom_system(restore_point_id)
                
        except Exception as e:
            print(f"Restore Point Creator: Error restoring system: {e}")
            return False
    
    def _restore_windows_system(self, restore_point_id: str) -> bool:
        """Restore Windows system using system restore"""
        try:
            powershell_script = f"""
$restorePoint = Get-ComputerRestorePoint | Where-Object {{ $_.Description -like "*{restore_point_id}*" }}
if ($restorePoint) {{
    Restore-Computer -RestorePoint $restorePoint.SequenceNumber -Confirm:$false
    return $true
}} else {{
    return $false
}}
            """
            
            result = subprocess.run(
                ['powershell', '-Command', powershell_script],
                capture_output=True,
                timeout=60
            )
            
            return result.returncode == 0
            
        except Exception as e:
            print(f"Restore Point Creator: Error restoring Windows system: {e}")
            return False
    
    def _restore_custom_system(self, restore_point_id: str) -> bool:
        """Restore custom system state"""
        try:
            restore_point_dir = os.path.join(self.restore_points_dir, restore_point_id)
            state_file = os.path.join(restore_point_dir, 'system_state.json')
            
            if not os.path.exists(state_file):
                print(f"Restore Point Creator: System state file not found for {restore_point_id}")
                return False
            
            with open(state_file, 'r') as f:
                system_state = json.load(f)
            
            # Restore registry (Windows only)
            if platform.system() == 'Windows' and system_state.get('registry_backup'):
                self._restore_registry(system_state['registry_backup'])
            
            print(f"Restore Point Creator: Custom restore completed for {restore_point_id}")
            return True
            
        except Exception as e:
            print(f"Restore Point Creator: Error restoring custom system: {e}")
            return False
    
    def _restore_registry(self, registry_backup: Dict[str, str]):
        """Restore Windows registry from backup"""
        try:
            for key, value in registry_backup.items():
                # Create temporary .reg file
                temp_reg_file = f"temp_restore_{int(time.time())}.reg"
                with open(temp_reg_file, 'w') as f:
                    f.write(value)
                
                # Import registry
                subprocess.run(
                    ['reg', 'import', temp_reg_file],
                    capture_output=True,
                    timeout=30
                )
                
                # Clean up
                if os.path.exists(temp_reg_file):
                    os.remove(temp_reg_file)
                    
        except Exception as e:
            print(f"Restore Point Creator: Error restoring registry: {e}")
    
    def get_restore_point_stats(self) -> Dict[str, Any]:
        """Get restore point statistics"""
        return {
            'total_restore_points': len(self.restore_points),
            'max_restore_points': self.settings['max_restore_points'],
            'auto_create_enabled': self.settings['auto_create'],
            'vss_enabled': self.settings['vss_enabled'],
            'use_windows_restore': self.settings['use_windows_restore'],
            'restore_points_directory': self.restore_points_dir,
            'last_update': datetime.now().isoformat()
        }
    
    def delete_restore_point(self, restore_point_id: str) -> bool:
        """Delete a specific restore point"""
        try:
            # Remove from database
            self.restore_points = [p for p in self.restore_points if p['id'] != restore_point_id]
            self._save_restore_points()
            
            # Delete actual restore point
            self._delete_restore_point(restore_point_id)
            
            print(f"Restore Point Creator: Deleted restore point {restore_point_id}")
            return True
            
        except Exception as e:
            print(f"Restore Point Creator: Error deleting restore point {restore_point_id}: {e}")
            return False
    
    def clear_all_restore_points(self):
        """Clear all restore points"""
        try:
            # Delete all restore points
            for point in self.restore_points:
                self._delete_restore_point(point['id'])
            
            # Clear database
            self.restore_points.clear()
            self._save_restore_points()
            
            print("Restore Point Creator: Cleared all restore points")
            
        except Exception as e:
            print(f"Restore Point Creator: Error clearing restore points: {e}") 