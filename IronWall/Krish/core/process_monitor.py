"""
IronWall Antivirus - Real-Time Process Monitor
Monitor running processes, detect suspicious behavior, and provide reputation data
"""

import psutil
import os
import hashlib
import json
import threading
import time
from typing import Dict, List, Optional, Any, Callable
from datetime import datetime
import requests
import subprocess
import platform
import re

class ProcessMonitor:
    def __init__(self, threat_database=None):
        self.threat_db = threat_database
        self.monitoring = False
        self.monitor_thread = None
        self.process_cache = {}
        self.suspicious_processes = set()
        self.blocked_processes = set()
        self.reputation_cache = {}
        self.cache_ttl = 3600  # 1 hour
        
        # Process monitoring settings
        self.scan_interval = 2.0  # seconds
        self.max_processes = 1000
        
        # Suspicious process patterns
        self.suspicious_patterns = {
            'names': [
                r'cryptolocker', r'wannacry', r'petya', r'locky', r'cerber',
                r'zeus', r'citadel', r'dridex', r'emotet', r'trickbot',
                r'keylogger', r'backdoor', r'rat', r'stealer', r'miner',
                r'crypto', r'bitcoin', r'mining', r'coinminer', r'xmrig',
                r'processhacker', r'procexp', r'procexp64', r'processexplorer',
                r'wireshark', r'fiddler', r'burp', r'mitmproxy', r'charles',
                r'ollydbg', r'x64dbg', r'windbg', r'ida', r'ghidra',
                r'cheatengine', r'artmoney', r'gamehack', r'trainer',
                r'crack', r'keygen', r'patch', r'loader', r'injector'
            ],
            'command_lines': [
                r'powershell\s+-enc', r'powershell\s+-encodedcommand',
                r'cmd\.exe\s+/c\s+.*del\s+\*\.\*', r'cmd\.exe\s+/c\s+.*format\s+',
                r'wget\s+.*\.exe', r'curl\s+.*\.exe', r'certutil\s+-urlcache',
                r'bitsadmin\s+/transfer', r'ftp\s+-s:', r'tftp\s+-i\s+',
                r'nc\s+-l', r'netcat\s+-l', r'python\s+-c\s+.*import\s+urllib',
                r'perl\s+-e\s+.*system\s*\(', r'ruby\s+-e\s+.*system\s*\(',
                r'java\s+-jar\s+.*\.jar', r'node\s+.*\.js', r'php\s+.*\.php'
            ],
            'network_activity': [
                r'192\.168\.', r'10\.', r'172\.(1[6-9]|2[0-9]|3[0-1])\.',
                r'\.(ru|cn|tk|ml|ga|cf|gq|pw|cc|top|xyz)$',
                r'\.(bit|onion|i2p)$', r'tor\.', r'proxy\.'
            ]
        }
        
        # High-risk process attributes
        self.high_risk_attributes = {
            'high_cpu_usage': 80.0,  # CPU usage threshold
            'high_memory_usage': 500 * 1024 * 1024,  # 500MB memory threshold
            'high_network_activity': 1024 * 1024,  # 1MB/s network threshold
            'suspicious_parent': ['cmd.exe', 'powershell.exe', 'wscript.exe', 'cscript.exe'],
            'suspicious_children': ['cmd.exe', 'powershell.exe', 'wscript.exe', 'cscript.exe'],
            'suspicious_working_dir': ['temp', 'tmp', 'downloads', 'desktop', 'recent']
        }
        
        # Process reputation sources
        self.reputation_sources = {
            'virustotal': 'https://www.virustotal.com/vtapi/v2/file/report',
            'hybrid_analysis': 'https://www.hybrid-analysis.com/api/v2/search/hash',
            'malware_bazaar': 'https://bazaar.abuse.ch/api/v1/'
        }
        
        # Start monitoring
        self.start_monitoring()
    
    def start_monitoring(self):
        """Start real-time process monitoring"""
        if not self.monitoring:
            self.monitoring = True
            self.monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
            self.monitor_thread.start()
            print("Process Monitor: Started real-time monitoring")
    
    def stop_monitoring(self):
        """Stop real-time process monitoring"""
        self.monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=1)
            print("Process Monitor: Stopped monitoring")
    
    def _monitor_loop(self):
        """Main monitoring loop"""
        while self.monitoring:
            try:
                # Get current processes
                current_processes = self._get_current_processes()
                
                # Analyze processes for suspicious behavior
                for proc_info in current_processes:
                    self._analyze_process(proc_info)
                
                # Clean up old cache entries
                self._cleanup_cache()
                
                # Sleep before next scan
                time.sleep(self.scan_interval)
                
            except Exception as e:
                print(f"Process Monitor: Error in monitoring loop: {e}")
                time.sleep(5)
    
    def _get_current_processes(self) -> List[Dict[str, Any]]:
        """Get current running processes with detailed information"""
        processes = []
        
        try:
            for proc in psutil.process_iter(['pid', 'name', 'exe', 'cmdline', 'cpu_percent', 'memory_info', 'create_time', 'status']):
                try:
                    proc_info = proc.info
                    
                    # Get additional information
                    proc_info['username'] = proc.username()
                    proc_info['working_dir'] = proc.cwd()
                    proc_info['parent_pid'] = proc.ppid()
                    
                    # Get network connections
                    try:
                        connections = proc.connections()
                        proc_info['network_connections'] = len(connections)
                        proc_info['network_addresses'] = [conn.raddr.ip for conn in connections if conn.raddr]
                    except:
                        proc_info['network_connections'] = 0
                        proc_info['network_addresses'] = []
                    
                    # Get open files
                    try:
                        open_files = proc.open_files()
                        proc_info['open_files'] = len(open_files)
                    except:
                        proc_info['open_files'] = 0
                    
                    # Calculate file hash if executable exists
                    if proc_info['exe'] and os.path.exists(proc_info['exe']):
                        proc_info['file_hash'] = self._calculate_file_hash(proc_info['exe'])
                    else:
                        proc_info['file_hash'] = None
                    
                    processes.append(proc_info)
                    
                    # Limit number of processes to monitor
                    if len(processes) >= self.max_processes:
                        break
                        
                except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                    continue
                    
        except Exception as e:
            print(f"Process Monitor: Error getting processes: {e}")
        
        return processes
    
    def _calculate_file_hash(self, file_path: str) -> str:
        """Calculate MD5 hash of executable file"""
        try:
            with open(file_path, 'rb') as f:
                return hashlib.md5(f.read()).hexdigest()
        except:
            return None
    
    def _analyze_process(self, proc_info: Dict[str, Any]):
        """Analyze a process for suspicious behavior"""
        try:
            pid = proc_info['pid']
            name = proc_info['name']
            cmdline = ' '.join(proc_info['cmdline']) if proc_info['cmdline'] else ''
            
            # Check if process is already known
            if pid in self.process_cache:
                return
            
            # Initialize process analysis
            analysis = {
                'pid': pid,
                'name': name,
                'exe': proc_info['exe'],
                'cmdline': cmdline,
                'risk_score': 0.0,
                'suspicious_indicators': [],
                'reputation': 'Unknown',
                'first_seen': datetime.now().isoformat(),
                'last_seen': datetime.now().isoformat()
            }
            
            # Check for suspicious patterns
            risk_score = 0.0
            indicators = []
            
            # Check process name patterns
            for pattern in self.suspicious_patterns['names']:
                if re.search(pattern, name, re.IGNORECASE):
                    risk_score += 0.3
                    indicators.append(f'Suspicious name pattern: {pattern}')
                    break
            
            # Check command line patterns
            for pattern in self.suspicious_patterns['command_lines']:
                if re.search(pattern, cmdline, re.IGNORECASE):
                    risk_score += 0.4
                    indicators.append(f'Suspicious command line: {pattern}')
                    break
            
            # Check resource usage
            if proc_info['cpu_percent'] > self.high_risk_attributes['high_cpu_usage']:
                risk_score += 0.2
                indicators.append(f'High CPU usage: {proc_info["cpu_percent"]}%')
            
            if proc_info['memory_info'].rss > self.high_risk_attributes['high_memory_usage']:
                risk_score += 0.2
                indicators.append(f'High memory usage: {proc_info["memory_info"].rss / (1024*1024):.1f}MB')
            
            # Check network activity
            if proc_info['network_connections'] > 10:
                risk_score += 0.2
                indicators.append(f'High network activity: {proc_info["network_connections"]} connections')
            
            # Check working directory
            working_dir = proc_info.get('working_dir', '')
            for suspicious_dir in self.high_risk_attributes['suspicious_working_dir']:
                if suspicious_dir in working_dir.lower():
                    risk_score += 0.1
                    indicators.append(f'Suspicious working directory: {suspicious_dir}')
                    break
            
            # Check parent process
            parent_pid = proc_info.get('parent_pid')
            if parent_pid:
                try:
                    parent = psutil.Process(parent_pid)
                    parent_name = parent.name()
                    if parent_name in self.high_risk_attributes['suspicious_parent']:
                        risk_score += 0.2
                        indicators.append(f'Suspicious parent process: {parent_name}')
                except:
                    pass
            
            # Get reputation if file hash is available
            if proc_info['file_hash']:
                reputation = self._get_file_reputation(proc_info['file_hash'])
                analysis['reputation'] = reputation
                
                if reputation == 'Malicious':
                    risk_score += 0.5
                    indicators.append('Known malicious file')
                elif reputation == 'Suspicious':
                    risk_score += 0.3
                    indicators.append('Suspicious file reputation')
            
            # Update analysis
            analysis['risk_score'] = min(risk_score, 1.0)
            analysis['suspicious_indicators'] = indicators
            
            # Cache the analysis
            self.process_cache[pid] = analysis
            
            # Mark as suspicious if risk score is high
            if risk_score >= 0.6:
                self.suspicious_processes.add(pid)
                print(f"Process Monitor: Suspicious process detected - {name} (PID: {pid}, Risk: {risk_score:.2f})")
            
        except Exception as e:
            print(f"Process Monitor: Error analyzing process {pid}: {e}")
    
    def _get_file_reputation(self, file_hash: str) -> str:
        """Get file reputation from various sources"""
        try:
            # Check cache first
            if file_hash in self.reputation_cache:
                cache_entry = self.reputation_cache[file_hash]
                if time.time() - cache_entry['timestamp'] < self.cache_ttl:
                    return cache_entry['reputation']
            
            # Check local threat database first
            if self.threat_db and self.threat_db.is_known_threat(file_hash):
                reputation = 'Malicious'
            else:
                # Check online sources (if API keys are available)
                reputation = self._check_online_reputation(file_hash)
            
            # Cache the result
            self.reputation_cache[file_hash] = {
                'reputation': reputation,
                'timestamp': time.time()
            }
            
            return reputation
            
        except Exception as e:
            print(f"Process Monitor: Error getting reputation: {e}")
            return 'Unknown'
    
    def _check_online_reputation(self, file_hash: str) -> str:
        """Check file reputation from online sources"""
        try:
            # Check VirusTotal (if API key is available)
            vt_api_key = os.environ.get('VT_API_KEY')
            if vt_api_key:
                vt_url = f"{self.reputation_sources['virustotal']}?apikey={vt_api_key}&resource={file_hash}"
                response = requests.get(vt_url, timeout=10)
                
                if response.status_code == 200:
                    data = response.json()
                    if data.get('response_code') == 1:
                        positives = data.get('positives', 0)
                        total = data.get('total', 0)
                        
                        if positives > 0:
                            ratio = positives / total
                            if ratio > 0.5:
                                return 'Malicious'
                            elif ratio > 0.1:
                                return 'Suspicious'
                            else:
                                return 'Clean'
            
            # Check MalwareBazaar
            try:
                mb_url = f"{self.reputation_sources['malware_bazaar']}query"
                payload = {'query': 'get_info', 'hash': file_hash}
                response = requests.post(mb_url, data=payload, timeout=10)
                
                if response.status_code == 200:
                    data = response.json()
                    if data.get('query_status') == 'ok':
                        return 'Malicious'
            except:
                pass
            
            return 'Unknown'
            
        except Exception as e:
            print(f"Process Monitor: Error checking online reputation: {e}")
            return 'Unknown'
    
    def _cleanup_cache(self):
        """Clean up old cache entries"""
        current_time = time.time()
        
        # Clean up process cache (keep last 1000 processes)
        if len(self.process_cache) > 1000:
            # Remove oldest entries
            sorted_processes = sorted(self.process_cache.items(), 
                                    key=lambda x: x[1]['last_seen'])
            self.process_cache = dict(sorted_processes[-1000:])
        
        # Clean up reputation cache
        expired_hashes = []
        for file_hash, cache_entry in self.reputation_cache.items():
            if current_time - cache_entry['timestamp'] > self.cache_ttl:
                expired_hashes.append(file_hash)
        
        for file_hash in expired_hashes:
            del self.reputation_cache[file_hash]
    
    def get_suspicious_processes(self) -> List[Dict[str, Any]]:
        """Get list of currently suspicious processes"""
        suspicious = []
        for pid in self.suspicious_processes:
            if pid in self.process_cache:
                suspicious.append(self.process_cache[pid])
        return suspicious
    
    def get_process_list(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Get list of monitored processes"""
        processes = list(self.process_cache.values())
        # Sort by risk score (highest first)
        processes.sort(key=lambda x: x['risk_score'], reverse=True)
        return processes[:limit]
    
    def kill_process(self, pid: int) -> bool:
        """Kill a suspicious process"""
        try:
            if pid in self.suspicious_processes:
                process = psutil.Process(pid)
                process.terminate()
                
                # Wait for process to terminate
                try:
                    process.wait(timeout=5)
                except psutil.TimeoutExpired:
                    process.kill()
                
                self.blocked_processes.add(pid)
                print(f"Process Monitor: Killed suspicious process {pid}")
                return True
            else:
                print(f"Process Monitor: Process {pid} is not marked as suspicious")
                return False
                
        except Exception as e:
            print(f"Process Monitor: Error killing process {pid}: {e}")
            return False
    
    def block_process(self, pid: int) -> bool:
        """Block a process from running (add to blocked list)"""
        try:
            if pid in self.process_cache:
                proc_info = self.process_cache[pid]
                self.blocked_processes.add(pid)
                
                # Add to threat database if it's a known executable
                if self.threat_db and proc_info['exe']:
                    self.threat_db.add_threat({
                        'hash': proc_info.get('file_hash', ''),
                        'name': proc_info['name'],
                        'path': proc_info['exe'],
                        'type': 'suspicious_process',
                        'risk_level': 'high',
                        'detection_date': datetime.now().isoformat()
                    })
                
                print(f"Process Monitor: Blocked process {pid} ({proc_info['name']})")
                return True
            else:
                print(f"Process Monitor: Process {pid} not found in cache")
                return False
                
        except Exception as e:
            print(f"Process Monitor: Error blocking process {pid}: {e}")
            return False
    
    def get_process_stats(self) -> Dict[str, Any]:
        """Get process monitoring statistics"""
        return {
            'total_monitored': len(self.process_cache),
            'suspicious_count': len(self.suspicious_processes),
            'blocked_count': len(self.blocked_processes),
            'reputation_cache_size': len(self.reputation_cache),
            'monitoring_active': self.monitoring,
            'last_update': datetime.now().isoformat()
        }
    
    def get_process_details(self, pid: int) -> Optional[Dict[str, Any]]:
        """Get detailed information about a specific process"""
        if pid in self.process_cache:
            return self.process_cache[pid]
        return None
    
    def clear_cache(self):
        """Clear all caches"""
        self.process_cache.clear()
        self.reputation_cache.clear()
        self.suspicious_processes.clear()
        print("Process Monitor: All caches cleared") 