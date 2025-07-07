"""
IronWall Antivirus - Quarantine Utility
Safe isolation and management of detected threats
"""

import os
import shutil
import json
import hashlib
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from pathlib import Path

class QuarantineManager:
    def __init__(self, quarantine_dir: str = "quarantine"):
        self.quarantine_dir = quarantine_dir
        self.quarantine_db_file = os.path.join(quarantine_dir, "quarantine_db.json")
        self.quarantined_files: Dict[str, Dict] = {}
        
        # Create quarantine directory if it doesn't exist
        try:
            os.makedirs(quarantine_dir, exist_ok=True)
        except Exception as e:
            print(f"Error creating quarantine directory: {e}")
        
        # Load existing quarantine database
        self.load_quarantine_db()
    
    def load_quarantine_db(self):
        """Load quarantine database from file"""
        try:
            if os.path.exists(self.quarantine_db_file):
                with open(self.quarantine_db_file, 'r') as f:
                    self.quarantined_files = json.load(f)
                print(f"Loaded quarantine database with {len(self.quarantined_files)} files")
            else:
                self.quarantined_files = {}
        except Exception as e:
            print(f"Error loading quarantine database: {e}")
            self.quarantined_files = {}
        return self.quarantined_files
    
    def save_quarantine_db(self):
        """Save quarantine database to file"""
        try:
            with open(self.quarantine_db_file, 'w') as f:
                json.dump(self.quarantined_files, f, indent=2)
        except Exception as e:
            print(f"Error saving quarantine database: {e}")
    
    def quarantine_file(self, file_path: str, threat_type: str, severity: str = "Moderate", 
                       signature: str = "", risk_level: str = "Medium", description: str = "", 
                       origin: str = "Scan", original_hash: str = "") -> bool:
        """Quarantine a file by moving it to quarantine directory with enhanced metadata"""
        try:
            if not os.path.exists(file_path):
                print(f"File not found: {file_path}")
                return False
            
            # Generate unique quarantine filename
            file_name = os.path.basename(file_path)
            file_ext = os.path.splitext(file_name)[1]
            quarantine_name = f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{hashlib.md5(file_path.encode()).hexdigest()[:8]}{file_ext}"
            quarantine_path = os.path.join(self.quarantine_dir, quarantine_name)
            
            # Move file to quarantine
            shutil.move(file_path, quarantine_path)
            
            # Calculate file hashes
            md5_hash, sha256_hash = self._calculate_file_hashes(quarantine_path)
            
            # Get file statistics
            file_stat = os.stat(quarantine_path)
            creation_date = datetime.fromtimestamp(file_stat.st_ctime).strftime('%Y-%m-%d %H:%M:%S')
            
            # Generate unique ID
            file_id = hashlib.md5((quarantine_name + str(file_stat.st_ctime)).encode()).hexdigest()
            
            # Record in quarantine database with enhanced metadata
            self.quarantined_files[quarantine_name] = {
                'id': file_id,
                'file_name': file_name,
                'quarantine_name': quarantine_name,
                'original_path': file_path,
                'quarantine_path': quarantine_path,
                'threat_type': threat_type,
                'severity': severity,
                'date_quarantined': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'status': 'Pending',
                'md5': md5_hash,
                'sha256': sha256_hash,
                'file_size': file_stat.st_size,
                'creation_date': creation_date,
                'signature': signature,
                'risk_level': risk_level,
                'description': description,
                'origin': origin,
                'original_hash': original_hash
            }
            
            self.save_quarantine_db()
            print(f"Quarantined: {file_path} -> {quarantine_path}")
            return True
            
        except Exception as e:
            print(f"Error quarantining file {file_path}: {e}")
            return False
    
    def _calculate_file_hashes(self, file_path: str) -> Tuple[str, str]:
        """Calculate MD5 and SHA256 hashes of a file"""
        try:
            md5_hash = hashlib.md5()
            sha256_hash = hashlib.sha256()
            
            with open(file_path, 'rb') as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    md5_hash.update(chunk)
                    sha256_hash.update(chunk)
            
            return md5_hash.hexdigest(), sha256_hash.hexdigest()
        except Exception as e:
            print(f"Error calculating file hashes: {e}")
            return "", ""
    
    def restore_file(self, file_id: str, restore_path: str = None) -> Tuple[bool, str]:
        """Restore a file from quarantine by ID"""
        try:
            # Find file by ID
            quarantine_name = None
            for name, file_info in self.quarantined_files.items():
                if file_info.get('id') == file_id:
                    quarantine_name = name
                    break
            
            if not quarantine_name:
                return False, "File not found in quarantine."
            
            file_info = self.quarantined_files[quarantine_name]
            
            if file_info.get('status') == 'Deleted':
                return False, "File has been permanently deleted."
            
            quarantine_path = file_info['quarantine_path']
            
            # Use original path if restore_path not specified
            if not restore_path:
                restore_path = file_info['original_path']
            
            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(restore_path), exist_ok=True)
            
            # Move file back to original location
            shutil.move(quarantine_path, restore_path)
            
            # Update database
            file_info['status'] = 'Restored'
            file_info['restore_date'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            file_info['restore_path'] = restore_path
            
            self.save_quarantine_db()
            print(f"Restored: {quarantine_path} -> {restore_path}")
            return True, "File restored successfully."
            
        except Exception as e:
            return False, str(e)
    
    def delete_quarantined_file(self, file_id: str) -> Tuple[bool, str]:
        """Permanently delete a quarantined file by ID"""
        try:
            # Find file by ID
            quarantine_name = None
            for name, file_info in self.quarantined_files.items():
                if file_info.get('id') == file_id:
                    quarantine_name = name
                    break
            
            if not quarantine_name:
                return False, "File not found in quarantine."
            
            file_info = self.quarantined_files[quarantine_name]
            
            if file_info.get('status') == 'Deleted':
                return False, "File has already been deleted."
            
            quarantine_path = file_info['quarantine_path']
            
            # Delete the file
            if os.path.exists(quarantine_path):
                os.remove(quarantine_path)
            
            # Update database
            file_info['status'] = 'Deleted'
            file_info['delete_date'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            self.save_quarantine_db()
            print(f"Deleted quarantined file: {quarantine_name}")
            return True, "File deleted permanently."
            
        except Exception as e:
            return False, str(e)
    
    def get_item_details(self, file_id: str) -> Optional[Dict]:
        """Get detailed information about a quarantined file by ID"""
        for file_info in self.quarantined_files.values():
            if file_info.get('id') == file_id:
                return file_info
        return None
    
    def list_items(self, search: str = None, sort_key: str = None, reverse: bool = False) -> List[Dict]:
        """Get list of quarantined files with search and sort capabilities"""
        try:
            items = []
            for quarantine_name, file_info in self.quarantined_files.items():
                items.append({
                    'quarantine_name': quarantine_name,
                    **file_info
                })
            
            # Apply search filter
            if search:
                items = [item for item in items if search.lower() in item.get('file_name', '').lower()]
            
            # Apply sorting
            if sort_key:
                items.sort(key=lambda x: x.get(sort_key, ''), reverse=reverse)
            
            return items
        except Exception as e:
            print(f"Error listing quarantined files: {e}")
            return []
    
    def get_quarantined_files(self, status: str = None) -> List[Dict]:
        """Get list of quarantined files (legacy method for compatibility)"""
        return self.list_items()
    
    def get_storage_info(self) -> Dict:
        """Get storage information about quarantine"""
        try:
            total_items = len([item for item in self.quarantined_files.values() if item.get('status') == 'Pending'])
            total_size = 0
            
            for item in self.quarantined_files.values():
                if item.get('status') == 'Pending':
                    file_path = item.get('quarantine_path', '')
                    if os.path.exists(file_path):
                        total_size += os.path.getsize(file_path)
            
            available_space = self._get_available_space()
            
            return {
                'total_items': total_items,
                'total_size': total_size,
                'available_space': available_space
            }
        except Exception as e:
            print(f"Error getting storage info: {e}")
            return {'total_items': 0, 'total_size': 0, 'available_space': 0}
    
    def _get_available_space(self) -> int:
        """Get available disk space for quarantine directory"""
        try:
            statvfs = os.statvfs(self.quarantine_dir)
            return statvfs.f_frsize * statvfs.f_bavail
        except Exception:
            return 0
    
    def apply_cleanup_rules(self, max_days: int = None, max_size: int = None) -> bool:
        """Apply auto-cleanup rules"""
        try:
            now = datetime.now()
            changed = False
            
            # Auto-delete files older than max_days
            if max_days is not None:
                for quarantine_name, file_info in list(self.quarantined_files.items()):
                    if file_info.get('status') == 'Pending':
                        try:
                            dt = datetime.strptime(file_info['date_quarantined'], '%Y-%m-%d %H:%M:%S')
                            if (now - dt).days > max_days:
                                success, _ = self.delete_quarantined_file(file_info['id'])
                                if success:
                                    changed = True
                        except Exception:
                            continue
            
            # Limit max size of quarantine folder
            if max_size is not None:
                items = sorted(
                    [item for item in self.quarantined_files.values() if item.get('status') == 'Pending'],
                    key=lambda x: x.get('date_quarantined', '')
                )
                
                while self.get_storage_info()['total_size'] > max_size and items:
                    success, _ = self.delete_quarantined_file(items[0]['id'])
                    if success:
                        items.pop(0)
                        changed = True
                    else:
                        break
            
            if changed:
                self.save_quarantine_db()
            
            return changed
        except Exception as e:
            print(f"Error applying cleanup rules: {e}")
            return False
    
    def get_quarantine_statistics(self) -> Dict:
        """Get statistics about quarantined files"""
        try:
            stats = {
                'total_files': len(self.quarantined_files),
                'quarantined': 0,
                'restored': 0,
                'deleted': 0,
                'total_size': 0,
                'threat_types': {},
                'severities': {}
            }
            
            for file_info in self.quarantined_files.values():
                status = file_info.get('status', 'unknown')
                if status == 'Pending':
                    stats['quarantined'] += 1
                elif status == 'Restored':
                    stats['restored'] += 1
                elif status == 'Deleted':
                    stats['deleted'] += 1
                
                # Count by threat type
                threat_type = file_info.get('threat_type', 'Unknown')
                stats['threat_types'][threat_type] = stats['threat_types'].get(threat_type, 0) + 1
                
                # Count by severity
                severity = file_info.get('severity', 'Unknown')
                stats['severities'][severity] = stats['severities'].get(severity, 0) + 1
                
                # Total size
                stats['total_size'] += file_info.get('file_size', 0)
            
            return stats
        except Exception as e:
            print(f"Error getting quarantine statistics: {e}")
            return {}
    
    def clean_old_quarantined_files(self, days: int = 30) -> int:
        """Clean up old quarantined files (legacy method for compatibility)"""
        try:
            cleaned_count = 0
            now = datetime.now()
            
            for quarantine_name, file_info in list(self.quarantined_files.items()):
                if file_info.get('status') == 'Pending':
                    try:
                        quarantine_date = datetime.strptime(file_info['date_quarantined'], '%Y-%m-%d %H:%M:%S')
                        if (now - quarantine_date).days > days:
                            success, _ = self.delete_quarantined_file(file_info['id'])
                            if success:
                                cleaned_count += 1
                    except Exception:
                        continue
            
            return cleaned_count
        except Exception as e:
            print(f"Error cleaning old quarantined files: {e}")
            return 0
    
    def export_quarantine_report(self, report_file: str):
        """Export quarantine report to file"""
        try:
            stats = self.get_quarantine_statistics()
            report = {
                'export_date': datetime.now().isoformat(),
                'statistics': stats,
                'quarantined_files': self.quarantined_files
            }
            
            with open(report_file, 'w') as f:
                json.dump(report, f, indent=2)
            
            print(f"Quarantine report exported to: {report_file}")
        except Exception as e:
            print(f"Error exporting quarantine report: {e}")
    
    def is_file_quarantined(self, original_path: str) -> bool:
        """Check if a file is quarantined by original path"""
        for file_info in self.quarantined_files.values():
            if file_info.get('original_path') == original_path and file_info.get('status') == 'Pending':
                return True
        return False
    
    def get_quarantine_path(self, original_path: str) -> Optional[str]:
        """Get quarantine path for a file by original path"""
        for file_info in self.quarantined_files.values():
            if file_info.get('original_path') == original_path and file_info.get('status') == 'Pending':
                return file_info.get('quarantine_path')
        return None
    
    def clear_quarantine(self):
        """Clear all quarantined files"""
        try:
            for quarantine_name, file_info in list(self.quarantined_files.items()):
                if file_info.get('status') == 'Pending':
                    self.delete_quarantined_file(file_info['id'])
            print("Quarantine cleared")
        except Exception as e:
            print(f"Error clearing quarantine: {e}") 