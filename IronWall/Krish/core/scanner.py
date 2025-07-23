"""
IronWall Antivirus - Core Scanner Module
Advanced threat detection with hash-based and pattern-based analysis
"""

import os
import hashlib
import threading
import time
from pathlib import Path
import re
from typing import Callable, Dict, List, Optional
import concurrent.futures
import math
import requests
try:
    import magic
    HAS_MAGIC = True
except ImportError:
    HAS_MAGIC = False
from utils import scan_history

def batch_scan_worker(batch, deep_scan_enabled):
    import os, time, hashlib
    results = []
    for file_path in batch:
        t0 = time.time()
        try:
            if not os.path.exists(file_path):
                continue
            file_name = os.path.basename(file_path)
            full_path = os.path.abspath(file_path)
            file_size = os.path.getsize(file_path)
            file_ext = os.path.splitext(file_path)[1].lower()
            # Fast hash
            hash_md5 = hashlib.md5()
            with open(file_path, "rb") as f:
                for chunk in iter(lambda: f.read(1024*1024), b""):
                    hash_md5.update(chunk)
            md5_hash = hash_md5.hexdigest()
            # Only basic info for speed; deep analysis can be added if needed
            result = (file_name, full_path, file_size, file_ext, md5_hash, t0, time.time())
            results.append(result)
        except Exception as e:
            results.append((file_path, None, None, None, None, t0, time.time(), str(e)))
    return results

class IronWallScanner:
    def __init__(self, threat_database):
        self.threat_db = threat_database
        self.stop_scanning = False
        self.paused = False
        self.scan_stats = {
            'files_scanned': 0,
            'threats_found': 0,
            'start_time': None,
            'end_time': None
        }
        self.virustotal_api_key = os.environ.get('VT_API_KEY', None)  # User must set this
        
        # Enhanced suspicious file extensions with real threats
        self.suspicious_extensions = {
            '.bat', '.cmd', '.exe', '.vbs', '.ps1', '.js', '.jar', '.scr', '.pif', '.com',
            '.dll', '.sys', '.drv', '.ocx', '.cpl', '.msi', '.msu', '.msp', '.mst',
            '.hta', '.wsf', '.wsh', '.reg', '.inf', '.lnk', '.url', '.scf', '.chm'
        }
        
        # Real-world dangerous patterns and malware signatures
        self.dangerous_patterns = [
            # File deletion and system destruction
            r'del\s+\*\.\*', r'del\s+/s\s+/q', r'del\s+/f\s+/s',
            r'rmdir\s+/s\s+/q', r'rmdir\s+/q\s+/s',
            r'format\s+[a-z]:', r'format\s+/q\s+[a-z]:',
            
            # System shutdown and restart
            r'shutdown\s+/s', r'shutdown\s+/r', r'shutdown\s+/a',
            r'logoff', r'restart', r'halt',
            
            # Registry modifications (malicious)
            r'reg\s+add\s+HKEY_LOCAL_MACHINE', r'reg\s+add\s+HKEY_CURRENT_USER',
            r'reg\s+delete\s+HKEY_LOCAL_MACHINE', r'reg\s+delete\s+HKEY_CURRENT_USER',
            r'reg\s+copy\s+HKEY_LOCAL_MACHINE', r'reg\s+copy\s+HKEY_CURRENT_USER',
            
            # PowerShell bypass and encoded execution
            r'powershell\s+-enc', r'powershell\s+-encodedcommand',
            r'powershell\s+-exec\s+bypass', r'powershell\s+-executionpolicy\s+bypass',
            r'powershell\s+-windowstyle\s+hidden', r'powershell\s+-noprofile',
            
            # Command execution and process manipulation
            r'cmd\.exe\s+/c', r'cmd\.exe\s+/k', r'cmd\s+/c', r'cmd\s+/k',
            r'taskkill\s+/f', r'taskkill\s+/im', r'taskkill\s+/pid',
            r'tskill\s+', r'ntsd\s+-c\s+q\s+-p',
            
            # File download and network operations
            r'wget\s+', r'curl\s+', r'certutil\s+-urlcache',
            r'bitsadmin\s+/transfer', r'bitsadmin\s+/create',
            r'ftp\s+-s:', r'tftp\s+-i\s+', r'nc\s+-l', r'netcat\s+-l',
            
            # Scheduled tasks and persistence
            r'schtasks\s+/create', r'schtasks\s+/run', r'schtasks\s+/query',
            r'at\s+', r'sc\s+create', r'sc\s+start', r'sc\s+config',
            
            # User and group manipulation
            r'net\s+user\s+', r'net\s+group\s+', r'net\s+localgroup\s+',
            r'net\s+accounts', r'net\s+share', r'net\s+use',
            
            # File permissions and access control
            r'icacls\s+', r'cacls\s+', r'cacls\s+/e\s+/p',
            r'takeown\s+/f', r'takeown\s+/r', r'takeown\s+/d',
            
            # Network scanning and reconnaissance
            r'netstat\s+-an', r'netstat\s+-n', r'netstat\s+-o',
            r'nslookup\s+', r'ping\s+-n\s+', r'tracert\s+',
            
            # Service manipulation
            r'sc\s+delete', r'sc\s+stop', r'sc\s+config\s+start=',
            r'net\s+stop', r'net\s+start',
            
            # File system operations
            r'copy\s+.*\s+%temp%', r'copy\s+.*\s+%tmp%',
            r'move\s+.*\s+%temp%', r'move\s+.*\s+%tmp%',
            r'xcopy\s+.*\s+%temp%', r'robocopy\s+.*\s+%temp%',
            
            # Stealth and obfuscation techniques
            r'echo\s+.*\s+\|\s+cmd', r'type\s+.*\s+\|\s+cmd',
            r'findstr\s+.*\s+\|\s+cmd', r'find\s+.*\s+\|\s+cmd',
            r'for\s+/f\s+.*\s+in\s+.*\s+do\s+',
            
            # Malicious URL patterns
            r'https?://[^\s]*\.(ru|cn|tk|ml|ga|cf|gq|pw|cc|top|xyz)',
            r'https?://[^\s]*\.(bit|onion|i2p)',
            r'https?://[^\s]*\.(exe|bat|cmd|ps1|vbs|js)',
            
            # Encoded content patterns
            r'base64\s+', r'base64\s+-d', r'base64\s+-i',
            r'certutil\s+-decode', r'certutil\s+-decodehex',
            
            # Process injection and DLL hijacking
            r'rundll32\s+', r'regsvr32\s+', r'regasm\s+',
            r'regsvcs\s+', r'regsvr32\s+/s\s+',
            
            # Memory manipulation
            r'wmic\s+process\s+call\s+create', r'wmic\s+process\s+where',
            r'wmic\s+service\s+call\s+start', r'wmic\s+service\s+where',
        ]
        
        # Real-world malware family signatures
        self.malware_families = {
            'ransomware': [
                'cryptolocker', 'wannacry', 'petya', 'notpetya', 'locky', 'cerber',
                'cryptowall', 'teslacrypt', 'cryptobit', 'cryptodefense', 'cryptoshield',
                'encrypt', 'decrypt', 'ransom', 'bitcoin', 'payment', 'wallet',
                'encrypted_files', 'decrypt_files', 'pay_ransom', 'bitcoin_address'
            ],
            'trojan': [
                'zeus', 'citadel', 'spyeye', 'carberp', 'tinba', 'ramnit', 'vawtrak',
                'dridex', 'emotet', 'trickbot', 'ursnif', 'gozi', 'shylock', 'dyre',
                'banker', 'stealer', 'keylogger', 'backdoor', 'rat', 'remote_access'
            ],
            'spyware': [
                'finfisher', 'hackingteam', 'darkcomet', 'blackshades', 'cyberghost',
                'spyware', 'keylogger', 'screen_capture', 'webcam_capture', 'mic_capture',
                'password_stealer', 'browser_hijacker', 'adware', 'tracking'
            ],
            'worm': [
                'conficker', 'sasser', 'blaster', 'nimda', 'code_red', 'sql_slammer',
                'msblast', 'lovsan', 'welchia', 'sobig', 'mydoom', 'bagle', 'netsky',
                'worm', 'self_replicating', 'network_propagation'
            ],
            'rootkit': [
                'tdss', 'alureon', 'mebroot', 'sinowal', 'rustock', 'cutwail',
                'rootkit', 'bootkit', 'kernel_mode', 'ring0', 'system_hook',
                'api_hooking', 'registry_hiding', 'file_hiding'
            ]
        }
        
        # Stealth detection patterns
        self.stealth_patterns = [
            # Anti-debugging and anti-VM techniques
            r'IsDebuggerPresent', r'CheckRemoteDebuggerPresent', r'OutputDebugString',
            r'GetTickCount', r'QueryPerformanceCounter', r'RDTSC',
            r'VirtualAlloc', r'VirtualProtect', r'VirtualFree',
            r'CreateRemoteThread', r'WriteProcessMemory', r'ReadProcessMemory',
            
            # Process injection techniques
            r'SetWindowsHookEx', r'SetWindowsHook', r'CallNextHookEx',
            r'CreateToolhelp32Snapshot', r'Process32First', r'Process32Next',
            r'OpenProcess', r'CreateProcess', r'ShellExecute',
            
            # Registry persistence
            r'RegCreateKey', r'RegSetValue', r'RegDeleteValue',
            r'Software\\Microsoft\\Windows\\CurrentVersion\\Run',
            r'Software\\Microsoft\\Windows\\CurrentVersion\\RunOnce',
            r'Software\\Microsoft\\Windows\\CurrentVersion\\Policies\\Explorer\\Run',
            
            # File system hiding
            r'SetFileAttributes', r'GetFileAttributes', r'FILE_ATTRIBUTE_HIDDEN',
            r'FILE_ATTRIBUTE_SYSTEM', r'FindFirstFile', r'FindNextFile',
            
            # Network communication
            r'connect', r'bind', r'listen', r'accept', r'send', r'recv',
            r'WSASocket', r'closesocket', r'gethostbyname', r'getaddrinfo',
            
            # Code obfuscation
            r'xor', r'rol', r'ror', r'shl', r'shr', r'and', r'or', r'not',
            r'base64', r'rot13', r'caesar', r'substitution'
        ]
    
    def scan_folder(self, folder_path: str, result_callback: Callable, progress_callback: Callable, deep_scan_enabled=False):
        """Scan specific folder for threats"""
        self.reset_scan_state()  # Reset state for new scan
        self.scan_stats['start_time'] = time.time()
        
        self._scan_directory(folder_path, result_callback, progress_callback, deep_scan_enabled=deep_scan_enabled)
        self.scan_stats['end_time'] = time.time()
    
    def _scan_directory(self, directory: str, result_callback: Callable, progress_callback: Callable, file_discovered_callback: Callable = None, deep_scan_enabled=False):
        """Scan a specific directory in parallel using ProcessPoolExecutor and report file discovery"""
        try:
            file_paths = []
            # Directories to skip for performance and safety
            skip_dirs = {
                '$Recycle.Bin', 'System Volume Information', 'Windows.old', 
                'Windows\\Temp', 'Windows\\Prefetch', 'Windows\\SoftwareDistribution',
                'ProgramData\\Package Cache', 'Users\\*\\AppData\\Local\\Temp',
                'Users\\*\\AppData\\Local\\Microsoft\\Windows\\INetCache',
                'Users\\*\\AppData\\Local\\Microsoft\\Windows\\WebCache',
                'Users\\*\\AppData\\Roaming\\Microsoft\\Windows\\Recent',
                'Users\\*\\AppData\\Local\\Microsoft\\Windows\\Explorer\\ThumbCacheToDelete'
            }
            for root, dirs, files in os.walk(directory):
                if self.stop_scanning:
                    break
                # Skip system directories
                dirs[:] = [d for d in dirs if d not in skip_dirs and not d.startswith('.')]
                for file in files:
                    if self.stop_scanning:
                        break
                    file_lower = file.lower()
                    if (file_lower.endswith(('.tmp', '.log', '.cache', '.bak', '.old')) or
                        file_lower.startswith('~') or
                        file_lower in ('thumbs.db', 'desktop.ini')):
                        continue
                    file_path = os.path.join(root, file)
                    try:
                        if os.path.getsize(file_path) > 100 * 1024 * 1024:  # 100MB
                            continue
                    except (OSError, PermissionError):
                        continue
                    file_paths.append(file_path)
                    if file_discovered_callback:
                        try:
                            file_discovered_callback(len(file_paths))
                        except:
                            pass
            total_files = len(file_paths)
            print(f"Found {total_files} files to scan in {directory}")

            # --- Caching: skip files already scanned in this run (by path+mtime) ---
            scan_cache = set()
            def file_cache_key(path):
                try:
                    return (path, os.path.getmtime(path))
                except Exception:
                    return (path, 0)
            file_paths = [fp for fp in file_paths if file_cache_key(fp) not in scan_cache]
            # Mark all as to-be-scanned
            for fp in file_paths:
                scan_cache.add(file_cache_key(fp))

            # --- Batch files for each worker ---
            batch_size = 20
            batches = [file_paths[i:i+batch_size] for i in range(0, len(file_paths), batch_size)]

            from concurrent.futures import ProcessPoolExecutor, as_completed
            import multiprocessing
            import threading
            stats_lock = threading.Lock()
            max_workers = min(16, (multiprocessing.cpu_count() or 4) * 2, len(batches)) if len(batches) > 0 else 1
            with ProcessPoolExecutor(max_workers=max_workers) as executor:
                futures = [executor.submit(batch_scan_worker, batch, deep_scan_enabled) for batch in batches]
                files_scanned = 0
                buffer = []
                BUFFER_SIZE = 50
                for idx, future in enumerate(as_completed(futures)):
                    if self.stop_scanning:
                        for f in futures:
                            f.cancel()
                        break
                    try:
                        batch_results = future.result()
                        for res in batch_results:
                            if len(res) == 7 and res[1] is not None:
                                file_name, full_path, file_size, file_ext, md5_hash, t0, t1 = res
                                files_scanned += 1
                                buffer.append((file_name, full_path, file_size, file_ext, None, md5_hash, None, 'Scanned', 'Clean'))
                                if len(buffer) >= BUFFER_SIZE:
                                    if result_callback:
                                        for b in buffer:
                                            result_callback(*b)
                                    buffer.clear()
                                if t1 - t0 > 1.0:
                                    print(f"[PROFILE] Slow scan: {full_path} took {t1-t0:.2f}s")
                        if progress_callback and files_scanned % 5 == 0:
                            progress_callback(None, None, {'files_scanned': files_scanned, 'threats_found': 0})
                    except Exception as e:
                        print(f"Error in batch scan: {e}")
                # Flush any remaining buffered results
                if buffer and result_callback:
                    for b in buffer:
                        result_callback(*b)
                buffer.clear()
        except PermissionError:
            print(f"Permission denied accessing {directory}")
        except Exception as e:
            if not self.stop_scanning:
                print(f"Error scanning directory {directory}: {e}")
    
    def _scan_file_enhanced(self, file_path: str, result_callback: Callable, deep_scan_enabled=False):
        """Enhanced file scanning with multiple detection methods and full info"""
        import time
        t0 = time.time()
        try:
            while self.paused:
                time.sleep(0.1)
            if self.stop_scanning:
                return
            if not os.path.exists(file_path):
                return
            file_name = os.path.basename(file_path)
            full_path = os.path.abspath(file_path)
            file_size = os.path.getsize(file_path)
            # File type detection
            if HAS_MAGIC:
                try:
                    file_type = magic.from_file(file_path, mime=True)
                except Exception:
                    file_type = Path(file_path).suffix.lower()
            else:
                file_type = Path(file_path).suffix.lower()
            file_ext = Path(file_path).suffix.lower()  # Always get extension
            # Hashes
            if self.stop_scanning:
                return
            md5_hash = self._calculate_fast_hash(file_path)
            if self.stop_scanning:
                return
            sha256_hash = self._calculate_sha256(file_path)
            # Heuristic analysis
            if self.stop_scanning:
                return
            entropy = self._calculate_entropy(file_path)
            obfuscated = self._is_obfuscated(file_path)
            heuristic = 'Clean'
            if entropy > 7.5:
                heuristic = 'High Entropy'
            if obfuscated:
                heuristic = 'Obfuscated'
            # Threat detection
            if self.stop_scanning:
                return
            threat_type = self.threat_db.check_hash(md5_hash)
            if threat_type:
                if not self.stop_scanning:
                    self.scan_stats['threats_found'] += 1
                    scan_history.add_threat_to_history({
                        'file_name': file_name,
                        'full_path': full_path,
                        'file_size': file_size,
                        'file_type': file_type,
                        'threat_type': threat_type,
                        'md5': md5_hash,
                        'sha256': sha256_hash,
                        'status': 'Known Threat',
                        'heuristic': heuristic,
                        'timestamp': time.time()
                    })
                    if result_callback:
                        try:
                            result_callback(file_name, full_path, file_size, file_type, threat_type, md5_hash, sha256_hash, 'Known Threat', heuristic)
                        except:
                            pass
                return
            if self.stop_scanning:
                return
            # Always analyze text/script files for patterns based on extension
            text_script_exts = ['.bat', '.cmd', '.txt', '.ps1', '.vbs', '.js', '.hta', '.wsf']
            if file_ext in text_script_exts:
                pattern_threat = self._analyze_text_file_enhanced(file_path)
                if pattern_threat:
                    if not self.stop_scanning:
                        self.scan_stats['threats_found'] += 1
                        scan_history.add_threat_to_history({
                            'file_name': file_name,
                            'full_path': full_path,
                            'file_size': file_size,
                            'file_type': file_type,
                            'threat_type': pattern_threat,
                            'md5': md5_hash,
                            'sha256': sha256_hash,
                            'status': 'Pattern Match',
                            'heuristic': heuristic,
                            'timestamp': time.time()
                        })
                        if result_callback:
                            try:
                                result_callback(file_name, full_path, file_size, file_type, pattern_threat, md5_hash, sha256_hash, 'Pattern Match', heuristic)
                            except:
                                pass
                    return
            # For suspicious extensions, check for size/wrong extension
            if file_ext in self.suspicious_extensions:
                threat_type = self._analyze_suspicious_file_enhanced(file_path, file_ext)
                if threat_type:
                    if not self.stop_scanning:
                        self.scan_stats['threats_found'] += 1
                        scan_history.add_threat_to_history({
                            'file_name': file_name,
                            'full_path': full_path,
                            'file_size': file_size,
                            'file_type': file_type,
                            'threat_type': threat_type,
                            'md5': md5_hash,
                            'sha256': sha256_hash,
                            'status': 'Suspicious',
                            'heuristic': heuristic,
                            'timestamp': time.time()
                        })
                        if result_callback:
                            try:
                                result_callback(file_name, full_path, file_size, file_type, threat_type, md5_hash, sha256_hash, 'Suspicious', heuristic)
                            except:
                                pass
                    return
            if self.stop_scanning:
                return
            if file_ext in ['.exe', '.dll', '.sys', '.scr', '.com']:
                threat_type = self._analyze_binary_file(file_path)
                if threat_type:
                    if not self.stop_scanning:
                        self.scan_stats['threats_found'] += 1
                        scan_history.add_threat_to_history({
                            'file_name': file_name,
                            'full_path': full_path,
                            'file_size': file_size,
                            'file_type': file_type,
                            'threat_type': threat_type,
                            'md5': md5_hash,
                            'sha256': sha256_hash,
                            'status': 'Binary Analysis',
                            'heuristic': heuristic,
                            'timestamp': time.time()
                        })
                        if result_callback:
                            try:
                                result_callback(file_name, full_path, file_size, file_type, threat_type, md5_hash, sha256_hash, 'Binary Analysis', heuristic)
                            except:
                                pass
                    return
            # If no threat found, still call result_callback to show file as scanned
            vt_result = None
            if deep_scan_enabled and self.virustotal_api_key:
                vt_result = self.scan_file_with_virustotal(file_path)
            if not self.stop_scanning and result_callback:
                try:
                    result_callback(file_name, full_path, file_size, file_type, None, md5_hash, sha256_hash, 'Scanned', heuristic, vt_result)
                except:
                    pass
        except Exception as e:
            if not self.stop_scanning:
                print(f"Error scanning file {file_path}: {e}")
        finally:
            t1 = time.time()
            if t1 - t0 > 1.0:
                print(f"[PROFILE] Slow scan: {file_path} took {t1-t0:.2f}s")
    
    def _calculate_fast_hash(self, file_path: str) -> str:
        """Calculate a fast hash (MD5) for a file, optimized for speed"""
        hash_md5 = hashlib.md5()
        try:
            with open(file_path, "rb") as f:
                for chunk in iter(lambda: f.read(1024*1024), b""):
                    hash_md5.update(chunk)
        except Exception:
            return ""
        return hash_md5.hexdigest()
    
    def _calculate_sha256(self, file_path: str) -> str:
        try:
            if self.stop_scanning:
                return ""
            hash_sha256 = hashlib.sha256()
            with open(file_path, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    if self.stop_scanning:
                        return ""
                    hash_sha256.update(chunk)
            return hash_sha256.hexdigest()
        except:
            return ""
    
    def _calculate_entropy(self, file_path: str) -> float:
        try:
            with open(file_path, 'rb') as f:
                data = f.read()
            if not data:
                return 0.0
            byte_counts = [0] * 256
            for b in data:
                byte_counts[b] += 1
            entropy = 0.0
            for count in byte_counts:
                if count == 0:
                    continue
                p = count / len(data)
                entropy -= p * math.log2(p)
            return entropy
        except:
            return 0.0
    
    def _is_obfuscated(self, file_path: str) -> bool:
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            # Heuristic: lots of non-alphanumeric chars, long lines, or repeated patterns
            if len(content) > 0 and sum(1 for c in content if not c.isalnum() and not c.isspace()) / len(content) > 0.3:
                return True
            if any(len(line) > 200 for line in content.splitlines()):
                return True
            if content.count('chr(') > 5 or content.count('base64') > 2:
                return True
            return False
        except:
            return False
    
    def _analyze_suspicious_file_enhanced(self, file_path: str, file_ext: str) -> Optional[str]:
        """Enhanced analysis of suspicious file types"""
        try:
            file_size = os.path.getsize(file_path)
            
            # Check for oversized files
            if file_ext == '.exe' and file_size > 50 * 1024 * 1024:  # 50MB
                return "Oversized Executable"
            elif file_ext == '.dll' and file_size > 10 * 1024 * 1024:  # 10MB
                return "Oversized DLL"
            elif file_ext in ['.bat', '.ps1', '.vbs', '.js'] and file_size > 1024 * 1024:  # 1MB
                return "Oversized Script"
            
            # Check if file is executable but has wrong extension
            if self._is_executable(file_path) and file_ext not in ['.exe', '.com', '.scr', '.dll', '.sys']:
                return "Executable with Wrong Extension"
            
            return None
            
        except:
            return None
    
    def _analyze_text_file_enhanced(self, file_path: str) -> Optional[str]:
        """Enhanced analysis of text files for dangerous patterns"""
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read().lower()
            
            # Check for dangerous patterns
            for pattern in self.dangerous_patterns:
                if re.search(pattern, content):
                    return f"Pattern: {pattern}"
            
            # Check for malware family signatures
            for family, signatures in self.malware_families.items():
                for signature in signatures:
                    if signature in content:
                        return f"Malware Family: {family.title()}"
            
            # Check for stealth patterns
            for pattern in self.stealth_patterns:
                if re.search(pattern, content, re.IGNORECASE):
                    return f"Stealth Technique: {pattern}"
            
            # Check for encoded content
            if self._contains_encoded_content(content):
                return "Encoded Content"
            
            # Check for suspicious URLs
            suspicious_urls = self._find_suspicious_urls(content)
            if suspicious_urls:
                return f"Suspicious URLs: {len(suspicious_urls)} found"
            
            # Check for obfuscated code
            if self._is_obfuscated_code(content):
                return "Obfuscated Code"
            
            return None
            
        except:
            return None
    
    def _analyze_binary_file(self, file_path: str) -> Optional[str]:
        """Analyze binary files for malware indicators"""
        try:
            with open(file_path, 'rb') as f:
                # Read first 4KB for analysis
                header = f.read(4096)
                
                # Check for suspicious strings
                suspicious_strings = [
                    b'IsDebuggerPresent', b'CheckRemoteDebuggerPresent',
                    b'VirtualAlloc', b'VirtualProtect', b'CreateRemoteThread',
                    b'WriteProcessMemory', b'ReadProcessMemory', b'SetWindowsHookEx',
                    b'RegCreateKey', b'RegSetValue', b'CreateProcess',
                    b'ShellExecute', b'URLDownloadToFile', b'WinExec',
                    b'base64', b'xor', b'encrypt', b'decrypt', b'ransom',
                    b'bitcoin', b'wallet', b'payment', b'stealer', b'keylogger'
                ]
                
                for suspicious_string in suspicious_strings:
                    if suspicious_string in header:
                        return f"Suspicious Binary Content: {suspicious_string.decode('utf-8', errors='ignore')}"
                
            return None
            
        except:
            return None
    
    def _contains_encoded_content(self, content: str) -> bool:
        """Check for encoded content in text files"""
        try:
            # Check for base64 patterns
            base64_pattern = r'[A-Za-z0-9+/]{20,}={0,2}'
            if len(re.findall(base64_pattern, content)) > 3:
                return True
            
            # Check for hex encoded content
            hex_pattern = r'[0-9A-Fa-f]{20,}'
            if len(re.findall(hex_pattern, content)) > 5:
                return True
            
            # Check for URL encoded content
            url_encoded_pattern = r'%[0-9A-Fa-f]{2}'
            if len(re.findall(url_encoded_pattern, content)) > 10:
                return True
            
            return False
        except:
            return False
    
    def _find_suspicious_urls(self, content: str) -> List[str]:
        """Find suspicious URLs in content"""
        try:
            url_pattern = r'https?://[^\s]+'
            urls = re.findall(url_pattern, content)
            
            suspicious_urls = []
            for url in urls:
                # Check for suspicious TLDs
                suspicious_tlds = ['.ru', '.cn', '.tk', '.ml', '.ga', '.cf', '.gq', '.pw', '.cc', '.top', '.xyz']
                if any(tld in url.lower() for tld in suspicious_tlds):
                    suspicious_urls.append(url)
                
                # Check for executable downloads
                if any(ext in url.lower() for ext in ['.exe', '.bat', '.cmd', '.ps1', '.vbs', '.js']):
                    suspicious_urls.append(url)
                
                # Check for too many URLs
                if len(urls) > 10:
                    suspicious_urls.extend(urls)
                    break
            
            return suspicious_urls
        except:
            return []
    
    def _is_obfuscated_code(self, content: str) -> bool:
        """Check for obfuscated code patterns"""
        try:
            # Check for excessive use of special characters
            special_chars = len(re.findall(r'[^a-zA-Z0-9\s]', content))
            total_chars = len(content)
            
            if total_chars > 0 and special_chars / total_chars > 0.3:
                return True
            
            # Check for encoded strings
            if 'chr(' in content and content.count('chr(') > 5:
                return True
            
            # Check for concatenated strings
            if content.count('"') > 20 and content.count('+') > 10:
                return True
            
            return False
        except:
            return False
    
    def _is_executable(self, file_path: str) -> bool:
        """Check if file is executable"""
        try:
            with open(file_path, 'rb') as f:
                header = f.read(2)
                return header == b'MZ'  # DOS executable header
        except:
            return False
    
    def stop_scan(self):
        """Stop the current scan"""
        self.stop_scanning = True
    
    def reset_scan_state(self):
        """Reset the scanner state for a new scan"""
        self.stop_scanning = False
        self.scan_stats = {
            'files_scanned': 0,
            'threats_found': 0,
            'start_time': None,
            'end_time': None
        }
    
    def get_scan_stats(self) -> Dict:
        """Get current scan statistics"""
        return self.scan_stats.copy()
    
    def count_files_efficiently(self, directory: str, progress_callback: Callable = None) -> int:
        """Count files efficiently with progress updates"""
        total_files = 0
        try:
            # Directories to skip for performance
            skip_dirs = {
                '$Recycle.Bin', 'System Volume Information', 'Windows.old', 
                'Windows\\Temp', 'Windows\\Prefetch', 'Windows\\SoftwareDistribution',
                'ProgramData\\Package Cache', 'Users\\*\\AppData\\Local\\Temp',
                'Users\\*\\AppData\\Local\\Microsoft\\Windows\\INetCache',
                'Users\\*\\AppData\\Local\\Microsoft\\Windows\\WebCache',
                'Users\\*\\AppData\\Roaming\\Microsoft\\Windows\\Recent',
                'Users\\*\\AppData\\Local\\Microsoft\\Windows\\Explorer\\ThumbCacheToDelete'
            }
            
            for root, dirs, files in os.walk(directory):
                if self.stop_scanning:
                    break
                
                # Skip system directories
                dirs[:] = [d for d in dirs if d not in skip_dirs and not d.startswith('.')]
                
                # Count files in this directory
                file_count = len(files)
                total_files += file_count
                
                # Call progress callback every 1000 files
                if total_files % 1000 == 0 and progress_callback:
                    try:
                        progress_callback(total_files)
                    except:
                        pass
                        
        except PermissionError:
            print(f"Permission denied accessing {directory}")
        except Exception as e:
            print(f"Error counting files in {directory}: {e}")
            
        return total_files

    def scan_file_with_virustotal(self, file_path):
        """Query VirusTotal for a file hash. Returns VT result dict or None."""
        if not self.virustotal_api_key:
            return None
        sha256_hash = self._calculate_sha256(file_path)
        url = f'https://www.virustotal.com/api/v3/files/{sha256_hash}'
        headers = {'x-apikey': self.virustotal_api_key}
        try:
            resp = requests.get(url, headers=headers)
            if resp.status_code == 200:
                data = resp.json()
                return data
            else:
                return None
        except Exception as e:
            print(f"VirusTotal error: {e}")
            return None

    # Example usage:
    if __name__ == "__main__":
        scanner = IronWallScanner(None)
        # You can specify drives or folders to scan, e.g., ["C:\\", "D:\\"]
        scanner.full_scan(["C:\\Users\\306PC1\\Downloads\\Vaibhav"])