"""
IronWall Antivirus - Threat Database Utility
Hash-based malware detection and signature database management
"""

import json
import os
import hashlib
from typing import Dict, List, Optional, Set
from datetime import datetime

class ThreatDatabase:
    def __init__(self, db_file: str = "threat_database.json"):
        self.db_file = db_file
        self.threat_hashes: Dict[str, Dict] = {}
        self.threat_signatures: List[str] = []
        self.load_database()
        self.initialize_default_threats()
    
    def load_database(self):
        """Load threat database from file"""
        try:
            if os.path.exists(self.db_file):
                with open(self.db_file, 'r') as f:
                    data = json.load(f)
                    self.threat_hashes = data.get('hashes', {})
                    self.threat_signatures = data.get('signatures', [])
                print(f"Loaded {len(self.threat_hashes)} threat hashes and {len(self.threat_signatures)} signatures")
            else:
                print("No existing threat database found. Creating new one.")
        except Exception as e:
            print(f"Error loading threat database: {e}")
            self.threat_hashes = {}
            self.threat_signatures = []
    
    def save_database(self):
        """Save threat database to file"""
        try:
            data = {
                'hashes': self.threat_hashes,
                'signatures': self.threat_signatures,
                'last_updated': datetime.now().isoformat(),
                'version': '1.0'
            }
            with open(self.db_file, 'w') as f:
                json.dump(data, f, indent=2)
            print(f"Threat database saved with {len(self.threat_hashes)} hashes")
        except Exception as e:
            print(f"Error saving threat database: {e}")
    
    def initialize_default_threats(self):
        """Initialize database with real-world threat hashes and signatures"""
        try:
            # Real-world malware hashes (examples - these are not actual malware hashes)
            default_threats = {
                # Example ransomware hashes
                "a1b2c3d4e5f678901234567890123456": {
                    "name": "WannaCry_Ransomware",
                    "type": "Ransomware",
                    "severity": "Critical",
                    "description": "WannaCry ransomware variant",
                    "added_date": datetime.now().isoformat()
                },
                "b2c3d4e5f67890123456789012345678": {
                    "name": "Petya_Ransomware",
                    "type": "Ransomware",
                    "severity": "Critical",
                    "description": "Petya ransomware variant",
                    "added_date": datetime.now().isoformat()
                },
                "c3d4e5f6789012345678901234567890": {
                    "name": "Locky_Ransomware",
                    "type": "Ransomware",
                    "severity": "Critical",
                    "description": "Locky ransomware variant",
                    "added_date": datetime.now().isoformat()
                },
                
                # Example trojan hashes
                "d4e5f678901234567890123456789012": {
                    "name": "Zeus_Trojan",
                    "type": "Trojan",
                    "severity": "High",
                    "description": "Zeus banking trojan",
                    "added_date": datetime.now().isoformat()
                },
                "e5f67890123456789012345678901234": {
                    "name": "Emotet_Trojan",
                    "type": "Trojan",
                    "severity": "High",
                    "description": "Emotet banking trojan",
                    "added_date": datetime.now().isoformat()
                },
                "f6789012345678901234567890123456": {
                    "name": "TrickBot_Trojan",
                    "type": "Trojan",
                    "severity": "High",
                    "description": "TrickBot banking trojan",
                    "added_date": datetime.now().isoformat()
                },
                
                # Example spyware hashes
                "67890123456789012345678901234567": {
                    "name": "DarkComet_RAT",
                    "type": "Spyware",
                    "severity": "High",
                    "description": "DarkComet remote access trojan",
                    "added_date": datetime.now().isoformat()
                },
                "78901234567890123456789012345678": {
                    "name": "BlackShades_RAT",
                    "type": "Spyware",
                    "severity": "High",
                    "description": "BlackShades remote access trojan",
                    "added_date": datetime.now().isoformat()
                },
                
                # Example worm hashes
                "89012345678901234567890123456789": {
                    "name": "Conficker_Worm",
                    "type": "Worm",
                    "severity": "High",
                    "description": "Conficker worm variant",
                    "added_date": datetime.now().isoformat()
                },
                "90123456789012345678901234567890": {
                    "name": "Sasser_Worm",
                    "type": "Worm",
                    "severity": "High",
                    "description": "Sasser worm variant",
                    "added_date": datetime.now().isoformat()
                },
                
                # Example rootkit hashes
                "01234567890123456789012345678901": {
                    "name": "TDSS_Rootkit",
                    "type": "Rootkit",
                    "severity": "Critical",
                    "description": "TDSS/Alureon rootkit",
                    "added_date": datetime.now().isoformat()
                },
                "12345678901234567890123456789012": {
                    "name": "MebRoot_Rootkit",
                    "type": "Rootkit",
                    "severity": "Critical",
                    "description": "MebRoot bootkit",
                    "added_date": datetime.now().isoformat()
                }
            }
            
            # Add default threats if they don't exist
            for hash_value, threat_info in default_threats.items():
                if hash_value not in self.threat_hashes:
                    self.threat_hashes[hash_value] = threat_info
            
            # Real-world malicious signatures/patterns
            default_signatures = [
                # Ransomware patterns
                "encrypt_files", "decrypt_files", "pay_ransom", "bitcoin_payment",
                "wallet_address", "encrypted_extension", "ransom_note",
                
                # Banking trojan patterns
                "banking_trojan", "credential_stealer", "form_grabber",
                "keylogger", "screen_capture", "webcam_capture",
                
                # RAT patterns
                "remote_access", "backdoor", "command_control", "c2_server",
                "reverse_shell", "process_injection", "dll_injection",
                
                # Worm patterns
                "self_replicating", "network_propagation", "email_spread",
                "p2p_spread", "removable_drive_spread", "network_scan",
                
                # Rootkit patterns
                "kernel_mode", "ring0", "system_hook", "api_hooking",
                "registry_hiding", "file_hiding", "process_hiding",
                
                # Stealth techniques
                "anti_debug", "anti_vm", "anti_analysis", "code_obfuscation",
                "packed_executable", "encrypted_payload", "polymorphic",
                
                # Command and control
                "http_request", "dns_query", "irc_connection", "ftp_upload",
                "smtp_send", "webhook", "api_call", "cloud_storage",
                
                # Persistence mechanisms
                "registry_run", "startup_folder", "scheduled_task",
                "service_installation", "browser_extension", "driver_installation",
                
                # Privilege escalation
                "uac_bypass", "token_manipulation", "process_impersonation",
                "service_abuse", "dll_hijacking", "path_manipulation",
                
                # Defense evasion
                "process_termination", "service_stop", "firewall_disable",
                "antivirus_disable", "logging_disable", "monitoring_disable",
                
                # Credential access
                "password_dump", "hash_dump", "credential_harvesting",
                "keylogging", "credential_phishing", "brute_force",
                
                # Discovery
                "system_info", "network_discovery", "process_discovery",
                "service_discovery", "file_discovery", "registry_discovery",
                
                # Lateral movement
                "remote_execution", "pass_the_hash", "pass_the_ticket",
                "remote_service", "ssh_hijacking", "rdp_hijacking",
                
                # Collection
                "data_staging", "archive_collected", "clipboard_data",
                "input_capture", "audio_capture", "video_capture",
                
                # Exfiltration
                "data_compressed", "data_encrypted", "data_transfer",
                "email_exfiltration", "web_service", "file_transfer",
                
                # Impact
                "data_destruction", "service_stop", "system_shutdown",
                "account_manipulation", "data_manipulation", "defacement"
            ]
            
            # Add default signatures if they don't exist
            for signature in default_signatures:
                if signature not in self.threat_signatures:
                    self.threat_signatures.append(signature)
            
            # Save the database
            self.save_database()
        except Exception as e:
            print(f"Error initializing default threats: {e}")
    
    def check_hash(self, file_hash: str) -> Optional[str]:
        """Check if a file hash matches known threats"""
        try:
            if file_hash in self.threat_hashes:
                threat_info = self.threat_hashes[file_hash]
                return f"{threat_info['type']}: {threat_info['name']}"
            return None
        except Exception as e:
            print(f"Error checking hash: {e}")
            return None
    
    def add_threat_hash(self, file_hash: str, threat_name: str, threat_type: str, 
                       severity: str = "Medium", description: str = ""):
        """Add a new threat hash to the database"""
        try:
            self.threat_hashes[file_hash] = {
                "name": threat_name,
                "type": threat_type,
                "severity": severity,
                "description": description,
                "added_date": datetime.now().isoformat()
            }
            self.save_database()
        except Exception as e:
            print(f"Error adding threat hash: {e}")
    
    def add_threat(self, threat_info: Dict):
        """Add a threat to the database (alias for add_threat_hash)"""
        try:
            file_hash = threat_info.get('id', '')
            threat_name = threat_info.get('name', '')
            threat_type = threat_info.get('type', '')
            severity = threat_info.get('severity', 'Medium')
            description = threat_info.get('description', '')
            
            self.add_threat_hash(file_hash, threat_name, threat_type, severity, description)
        except Exception as e:
            print(f"Error adding threat: {e}")
    
    def remove_threat_hash(self, file_hash: str) -> bool:
        """Remove a threat hash from the database"""
        try:
            if file_hash in self.threat_hashes:
                del self.threat_hashes[file_hash]
                self.save_database()
                return True
            return False
        except Exception as e:
            print(f"Error removing threat hash: {e}")
            return False
    
    def check_signature(self, content: str) -> List[str]:
        """Check content against known threat signatures"""
        try:
            found_signatures = []
            content_lower = content.lower()
            
            for signature in self.threat_signatures:
                if signature.lower() in content_lower:
                    found_signatures.append(signature)
            
            return found_signatures
        except Exception as e:
            print(f"Error checking signatures: {e}")
            return []
    
    def add_signature(self, signature: str):
        """Add a new threat signature to the database"""
        try:
            if signature not in self.threat_signatures:
                self.threat_signatures.append(signature)
                self.save_database()
        except Exception as e:
            print(f"Error adding signature: {e}")
    
    def remove_signature(self, signature: str) -> bool:
        """Remove a threat signature from the database"""
        try:
            if signature in self.threat_signatures:
                self.threat_signatures.remove(signature)
                self.save_database()
                return True
            return False
        except Exception as e:
            print(f"Error removing signature: {e}")
            return False
    
    def get_threat_statistics(self) -> Dict:
        """Get statistics about the threat database"""
        try:
            threat_types = {}
            severities = {}
            
            for threat_info in self.threat_hashes.values():
                # Count by type
                threat_type = threat_info.get('type', 'Unknown')
                threat_types[threat_type] = threat_types.get(threat_type, 0) + 1
                
                # Count by severity
                severity = threat_info.get('severity', 'Unknown')
                severities[severity] = severities.get(severity, 0) + 1
            
            return {
                'total_hashes': len(self.threat_hashes),
                'total_signatures': len(self.threat_signatures),
                'threat_types': threat_types,
                'severities': severities,
                'last_updated': datetime.now().isoformat()
            }
        except Exception as e:
            print(f"Error getting threat statistics: {e}")
            return {}
    
    def search_threats(self, query: str) -> List[Dict]:
        """Search threats by name, type, or description"""
        try:
            results = []
            query_lower = query.lower()
            
            for hash_value, threat_info in self.threat_hashes.items():
                if (query_lower in threat_info.get('name', '').lower() or
                    query_lower in threat_info.get('type', '').lower() or
                    query_lower in threat_info.get('description', '').lower()):
                    results.append({
                        'hash': hash_value,
                        **threat_info
                    })
            
            return results
        except Exception as e:
            print(f"Error searching threats: {e}")
            return []
    
    def export_database(self, export_file: str):
        """Export threat database to a file"""
        try:
            data = {
                'hashes': self.threat_hashes,
                'signatures': self.threat_signatures,
                'export_date': datetime.now().isoformat(),
                'version': '1.0'
            }
            with open(export_file, 'w') as f:
                json.dump(data, f, indent=2)
            print(f"Threat database exported to {export_file}")
        except Exception as e:
            print(f"Error exporting threat database: {e}")
    
    def import_database(self, import_file: str):
        """Import threat database from a file"""
        try:
            with open(import_file, 'r') as f:
                data = json.load(f)
            
            imported_hashes = data.get('hashes', {})
            imported_signatures = data.get('signatures', [])
            
            # Merge with existing database
            self.threat_hashes.update(imported_hashes)
            for signature in imported_signatures:
                if signature not in self.threat_signatures:
                    self.threat_signatures.append(signature)
            
            self.save_database()
            print(f"Imported {len(imported_hashes)} hashes and {len(imported_signatures)} signatures")
        except Exception as e:
            print(f"Error importing threat database: {e}")
    
    def clear_database(self):
        """Clear all threats from the database"""
        try:
            self.threat_hashes.clear()
            self.threat_signatures.clear()
            self.save_database()
            print("Threat database cleared")
        except Exception as e:
            print(f"Error clearing threat database: {e}")
    
    def get_all_threats(self) -> List[Dict]:
        """Get all threats in the database"""
        try:
            all_threats = []
            for hash_value, threat_info in self.threat_hashes.items():
                threat_info_copy = threat_info.copy()
                threat_info_copy['hash'] = hash_value
                all_threats.append(threat_info_copy)
            return all_threats
        except Exception as e:
            print(f"Error getting all threats: {e}")
            return []
    
    def get_recent_threats(self, days: int = 7) -> List[Dict]:
        """Get threats added in the last N days"""
        try:
            recent_threats = []
            cutoff_date = datetime.now().timestamp() - (days * 24 * 60 * 60)
            
            for hash_value, threat_info in self.threat_hashes.items():
                try:
                    added_date = datetime.fromisoformat(threat_info.get('added_date', ''))
                    if added_date.timestamp() > cutoff_date:
                        recent_threats.append({
                            'hash': hash_value,
                            **threat_info
                        })
                except:
                    continue
            
            return recent_threats
        except Exception as e:
            print(f"Error getting recent threats: {e}")
            return [] 