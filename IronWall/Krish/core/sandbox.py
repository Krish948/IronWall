"""
IronWall Antivirus - Sandbox Execution Module
Simulate suspicious file behavior in a controlled environment
"""

import os
import subprocess
import tempfile
import shutil
import time
import json
import threading
import psutil
from typing import Dict, List, Optional, Any, Callable
from datetime import datetime
import platform
import re
import hashlib
import logging

class SandboxExecution:
    def __init__(self, sandbox_dir: str = None, timeout: int = 30):
        self.sandbox_dir = sandbox_dir or os.path.join(tempfile.gettempdir(), 'ironwall_sandbox')
        self.timeout = timeout
        self.active_sessions = {}
        self.session_counter = 0
        
        # Create sandbox directory
        os.makedirs(self.sandbox_dir, exist_ok=True)
        
        # Initialize logging
        self.logger = self._setup_logging()
        
        # Sandbox configuration
        self.sandbox_config = {
            'max_file_size': 50 * 1024 * 1024,  # 50MB
            'max_execution_time': timeout,
            'allowed_extensions': {'.exe', '.bat', '.cmd', '.ps1', '.vbs', '.js', '.jar'},
            'blocked_extensions': {'.scr', '.pif', '.com', '.cpl', '.msi'},
            'network_allowed': False,
            'registry_allowed': False,
            'file_system_restricted': True
        }
        
        # Monitoring hooks
        self.file_access_log = []
        self.network_activity_log = []
        self.registry_activity_log = []
        self.process_activity_log = []
        
        # Behavioral patterns to monitor
        self.suspicious_behaviors = {
            'file_operations': [
                'mass_file_creation', 'mass_file_deletion', 'file_encryption',
                'file_modification', 'file_copying', 'file_moving'
            ],
            'network_activity': [
                'dns_queries', 'http_requests', 'https_requests', 'ftp_connections',
                'smtp_connections', 'irc_connections', 'tor_connections'
            ],
            'registry_activity': [
                'registry_creation', 'registry_modification', 'registry_deletion',
                'startup_modification', 'service_creation', 'driver_installation'
            ],
            'process_activity': [
                'process_creation', 'process_injection', 'code_injection',
                'dll_loading', 'api_calls', 'privilege_escalation'
            ],
            'system_activity': [
                'service_manipulation', 'scheduled_task_creation', 'user_creation',
                'group_modification', 'audit_disable', 'firewall_disable'
            ]
        }
    
    def _setup_logging(self) -> logging.Logger:
        """Setup logging for sandbox activities"""
        logger = logging.getLogger('IronWall_Sandbox')
        logger.setLevel(logging.DEBUG)
        
        # Create handlers
        log_file = os.path.join(self.sandbox_dir, 'sandbox.log')
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.DEBUG)
        
        # Create formatter
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(formatter)
        
        # Add handler to logger
        logger.addHandler(file_handler)
        
        return logger
    
    def create_sandbox_session(self, file_path: str) -> str:
        """Create a new sandbox session for file analysis"""
        try:
            # Validate file
            if not self._validate_file(file_path):
                raise ValueError(f"File {file_path} is not suitable for sandbox analysis")
            
            # Create session ID
            session_id = f"session_{self.session_counter}_{int(time.time())}"
            self.session_counter += 1
            
            # Create session directory
            session_dir = os.path.join(self.sandbox_dir, session_id)
            os.makedirs(session_dir, exist_ok=True)
            
            # Copy file to sandbox
            sandbox_file_path = self._copy_file_to_sandbox(file_path, session_dir)
            
            # Initialize session
            session_info = {
                'session_id': session_id,
                'original_file': file_path,
                'sandbox_file': sandbox_file_path,
                'session_dir': session_dir,
                'start_time': datetime.now().isoformat(),
                'status': 'created',
                'file_access_log': [],
                'network_activity_log': [],
                'registry_activity_log': [],
                'process_activity_log': [],
                'behavior_analysis': {},
                'risk_score': 0.0,
                'suspicious_indicators': []
            }
            
            self.active_sessions[session_id] = session_info
            self.logger.info(f"Created sandbox session {session_id} for {file_path}")
            
            return session_id
            
        except Exception as e:
            self.logger.error(f"Error creating sandbox session: {e}")
            raise
    
    def _validate_file(self, file_path: str) -> bool:
        """Validate if file is suitable for sandbox analysis"""
        try:
            if not os.path.exists(file_path):
                return False
            
            # Check file size
            file_size = os.path.getsize(file_path)
            if file_size > self.sandbox_config['max_file_size']:
                return False
            
            # Check file extension
            file_ext = os.path.splitext(file_path)[1].lower()
            if file_ext in self.sandbox_config['blocked_extensions']:
                return False
            
            if file_ext not in self.sandbox_config['allowed_extensions']:
                return False
            
            return True
            
        except Exception:
            return False
    
    def _copy_file_to_sandbox(self, file_path: str, session_dir: str) -> str:
        """Copy file to sandbox directory"""
        try:
            file_name = os.path.basename(file_path)
            sandbox_file_path = os.path.join(session_dir, file_name)
            
            # Copy file
            shutil.copy2(file_path, sandbox_file_path)
            
            # Set appropriate permissions
            os.chmod(sandbox_file_path, 0o755)
            
            return sandbox_file_path
            
        except Exception as e:
            self.logger.error(f"Error copying file to sandbox: {e}")
            raise
    
    def execute_in_sandbox(self, session_id: str, callback: Callable = None) -> Dict[str, Any]:
        """Execute file in sandbox and monitor behavior"""
        if session_id not in self.active_sessions:
            raise ValueError(f"Session {session_id} not found")
        
        session_info = self.active_sessions[session_id]
        session_info['status'] = 'executing'
        
        try:
            self.logger.info(f"Starting execution in session {session_id}")
            
            # Start monitoring threads
            monitoring_threads = []
            
            # File system monitoring
            file_monitor = threading.Thread(
                target=self._monitor_file_activity,
                args=(session_id,),
                daemon=True
            )
            file_monitor.start()
            monitoring_threads.append(file_monitor)
            
            # Process monitoring
            process_monitor = threading.Thread(
                target=self._monitor_process_activity,
                args=(session_id,),
                daemon=True
            )
            process_monitor.start()
            monitoring_threads.append(process_monitor)
            
            # Network monitoring (if enabled)
            if not self.sandbox_config['network_allowed']:
                network_monitor = threading.Thread(
                    target=self._monitor_network_activity,
                    args=(session_id,),
                    daemon=True
                )
                network_monitor.start()
                monitoring_threads.append(network_monitor)
            
            # Execute the file
            execution_result = self._execute_file(session_info['sandbox_file'], session_id)
            
            # Wait for monitoring threads to complete
            for thread in monitoring_threads:
                thread.join(timeout=5)
            
            # Analyze behavior
            behavior_analysis = self._analyze_behavior(session_id)
            
            # Update session info
            session_info.update({
                'status': 'completed',
                'execution_result': execution_result,
                'behavior_analysis': behavior_analysis,
                'end_time': datetime.now().isoformat(),
                'risk_score': behavior_analysis.get('risk_score', 0.0),
                'suspicious_indicators': behavior_analysis.get('suspicious_indicators', [])
            })
            
            # Call callback if provided
            if callback:
                callback(session_info)
            
            self.logger.info(f"Completed execution in session {session_id}")
            return session_info
            
        except Exception as e:
            session_info['status'] = 'error'
            session_info['error'] = str(e)
            self.logger.error(f"Error in sandbox execution {session_id}: {e}")
            raise
    
    def _execute_file(self, file_path: str, session_id: str) -> Dict[str, Any]:
        """Execute file in controlled environment"""
        try:
            file_ext = os.path.splitext(file_path)[1].lower()
            
            # Prepare execution command based on file type
            if file_ext == '.exe':
                cmd = [file_path]
            elif file_ext in ['.bat', '.cmd']:
                cmd = ['cmd', '/c', file_path]
            elif file_ext == '.ps1':
                cmd = ['powershell', '-ExecutionPolicy', 'Bypass', '-File', file_path]
            elif file_ext == '.vbs':
                cmd = ['wscript', file_path]
            elif file_ext == '.js':
                cmd = ['wscript', file_path]
            elif file_ext == '.jar':
                cmd = ['java', '-jar', file_path]
            else:
                raise ValueError(f"Unsupported file type: {file_ext}")
            
            # Execute with timeout and resource limits
            start_time = time.time()
            
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                cwd=os.path.dirname(file_path),
                env=self._get_sandbox_environment(),
                creationflags=subprocess.CREATE_NEW_CONSOLE if platform.system() == 'Windows' else 0
            )
            
            try:
                stdout, stderr = process.communicate(timeout=self.timeout)
                execution_time = time.time() - start_time
                
                return {
                    'exit_code': process.returncode,
                    'stdout': stdout.decode('utf-8', errors='ignore'),
                    'stderr': stderr.decode('utf-8', errors='ignore'),
                    'execution_time': execution_time,
                    'process_id': process.pid
                }
                
            except subprocess.TimeoutExpired:
                process.kill()
                process.communicate()
                return {
                    'exit_code': -1,
                    'stdout': '',
                    'stderr': 'Execution timeout',
                    'execution_time': self.timeout,
                    'process_id': process.pid
                }
                
        except Exception as e:
            return {
                'exit_code': -1,
                'stdout': '',
                'stderr': str(e),
                'execution_time': 0,
                'process_id': None
            }
    
    def _get_sandbox_environment(self) -> Dict[str, str]:
        """Get sandbox environment variables"""
        env = os.environ.copy()
        
        # Restrict environment
        env['TEMP'] = os.path.join(self.sandbox_dir, 'temp')
        env['TMP'] = os.path.join(self.sandbox_dir, 'temp')
        env['HOME'] = self.sandbox_dir
        env['USERPROFILE'] = self.sandbox_dir
        
        # Disable network access
        if not self.sandbox_config['network_allowed']:
            env['HTTP_PROXY'] = 'http://localhost:1'
            env['HTTPS_PROXY'] = 'http://localhost:1'
            env['NO_PROXY'] = '*'
        
        return env
    
    def _monitor_file_activity(self, session_id: str):
        """Monitor file system activity during execution"""
        try:
            session_info = self.active_sessions[session_id]
            session_dir = session_info['session_dir']
            
            # Get initial file list
            initial_files = set()
            for root, dirs, files in os.walk(session_dir):
                for file in files:
                    initial_files.add(os.path.join(root, file))
            
            # Monitor for file changes
            start_time = time.time()
            while time.time() - start_time < self.timeout:
                current_files = set()
                for root, dirs, files in os.walk(session_dir):
                    for file in files:
                        current_files.add(os.path.join(root, file))
                
                # Detect new files
                new_files = current_files - initial_files
                for file_path in new_files:
                    self._log_file_activity(session_id, 'created', file_path)
                
                # Detect deleted files
                deleted_files = initial_files - current_files
                for file_path in deleted_files:
                    self._log_file_activity(session_id, 'deleted', file_path)
                
                initial_files = current_files
                time.sleep(1)
                
        except Exception as e:
            self.logger.error(f"Error in file monitoring: {e}")
    
    def _monitor_process_activity(self, session_id: str):
        """Monitor process activity during execution"""
        try:
            start_time = time.time()
            initial_processes = set(psutil.pids())
            
            while time.time() - start_time < self.timeout:
                current_processes = set(psutil.pids())
                
                # Detect new processes
                new_processes = current_processes - initial_processes
                for pid in new_processes:
                    try:
                        process = psutil.Process(pid)
                        self._log_process_activity(session_id, 'created', {
                            'pid': pid,
                            'name': process.name(),
                            'exe': process.exe(),
                            'cmdline': process.cmdline(),
                            'cpu_percent': process.cpu_percent(),
                            'memory_info': process.memory_info()._asdict()
                        })
                    except:
                        pass
                
                initial_processes = current_processes
                time.sleep(1)
                
        except Exception as e:
            self.logger.error(f"Error in process monitoring: {e}")
    
    def _monitor_network_activity(self, session_id: str):
        """Monitor network activity during execution"""
        try:
            start_time = time.time()
            initial_connections = set()
            
            # Get initial network connections
            for conn in psutil.net_connections():
                if conn.status == 'ESTABLISHED':
                    initial_connections.add((conn.laddr.ip, conn.laddr.port, conn.raddr.ip, conn.raddr.port))
            
            while time.time() - start_time < self.timeout:
                current_connections = set()
                
                # Get current network connections
                for conn in psutil.net_connections():
                    if conn.status == 'ESTABLISHED':
                        current_connections.add((conn.laddr.ip, conn.laddr.port, conn.raddr.ip, conn.raddr.port))
                
                # Detect new connections
                new_connections = current_connections - initial_connections
                for conn in new_connections:
                    self._log_network_activity(session_id, 'connection', {
                        'local_ip': conn[0],
                        'local_port': conn[1],
                        'remote_ip': conn[2],
                        'remote_port': conn[3]
                    })
                
                initial_connections = current_connections
                time.sleep(1)
                
        except Exception as e:
            self.logger.error(f"Error in network monitoring: {e}")
    
    def _log_file_activity(self, session_id: str, activity: str, file_path: str):
        """Log file system activity"""
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'activity': activity,
            'file_path': file_path,
            'file_size': os.path.getsize(file_path) if os.path.exists(file_path) else 0
        }
        
        if session_id in self.active_sessions:
            self.active_sessions[session_id]['file_access_log'].append(log_entry)
        
        self.logger.info(f"File activity in {session_id}: {activity} - {file_path}")
    
    def _log_process_activity(self, session_id: str, activity: str, process_info: Dict[str, Any]):
        """Log process activity"""
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'activity': activity,
            'process_info': process_info
        }
        
        if session_id in self.active_sessions:
            self.active_sessions[session_id]['process_activity_log'].append(log_entry)
        
        self.logger.info(f"Process activity in {session_id}: {activity} - {process_info.get('name', 'Unknown')}")
    
    def _log_network_activity(self, session_id: str, activity: str, network_info: Dict[str, Any]):
        """Log network activity"""
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'activity': activity,
            'network_info': network_info
        }
        
        if session_id in self.active_sessions:
            self.active_sessions[session_id]['network_activity_log'].append(log_entry)
        
        self.logger.info(f"Network activity in {session_id}: {activity} - {network_info.get('remote_ip', 'Unknown')}")
    
    def _analyze_behavior(self, session_id: str) -> Dict[str, Any]:
        """Analyze behavior patterns from sandbox execution"""
        if session_id not in self.active_sessions:
            return {}
        
        session_info = self.active_sessions[session_id]
        
        # Initialize analysis
        analysis = {
            'risk_score': 0.0,
            'suspicious_indicators': [],
            'behavior_summary': {},
            'file_operations': len(session_info['file_access_log']),
            'process_operations': len(session_info['process_activity_log']),
            'network_operations': len(session_info['network_activity_log']),
            'registry_operations': len(session_info['registry_activity_log'])
        }
        
        risk_score = 0.0
        indicators = []
        
        # Analyze file operations
        file_ops = session_info['file_access_log']
        if len(file_ops) > 10:
            risk_score += 0.2
            indicators.append('High file operation count')
        
        # Check for suspicious file operations
        for op in file_ops:
            if 'temp' in op['file_path'].lower() and op['activity'] == 'created':
                risk_score += 0.1
                indicators.append('Temporary file creation')
        
        # Analyze process operations
        process_ops = session_info['process_activity_log']
        if len(process_ops) > 5:
            risk_score += 0.3
            indicators.append('Multiple process creation')
        
        # Check for suspicious processes
        for op in process_ops:
            process_name = op['process_info'].get('name', '').lower()
            if any(susp in process_name for susp in ['cmd', 'powershell', 'wscript', 'cscript']):
                risk_score += 0.2
                indicators.append('Suspicious process execution')
        
        # Analyze network operations
        network_ops = session_info['network_activity_log']
        if network_ops:
            risk_score += 0.4
            indicators.append('Network activity detected')
        
        # Check for suspicious network connections
        for op in network_ops:
            remote_ip = op['network_info'].get('remote_ip', '')
            if remote_ip and not remote_ip.startswith(('127.', '192.168.', '10.')):
                risk_score += 0.2
                indicators.append('External network connection')
        
        # Analyze execution result
        exec_result = session_info.get('execution_result', {})
        if exec_result.get('exit_code', 0) != 0:
            risk_score += 0.1
            indicators.append('Abnormal exit code')
        
        # Update analysis
        analysis['risk_score'] = min(risk_score, 1.0)
        analysis['suspicious_indicators'] = indicators
        
        return analysis
    
    def get_session_info(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get information about a sandbox session"""
        return self.active_sessions.get(session_id)
    
    def get_all_sessions(self) -> List[Dict[str, Any]]:
        """Get all active sandbox sessions"""
        return list(self.active_sessions.values())
    
    def cleanup_session(self, session_id: str):
        """Clean up a sandbox session"""
        if session_id in self.active_sessions:
            session_info = self.active_sessions[session_id]
            
            try:
                # Remove session directory
                if os.path.exists(session_info['session_dir']):
                    shutil.rmtree(session_info['session_dir'])
                
                # Remove from active sessions
                del self.active_sessions[session_id]
                
                self.logger.info(f"Cleaned up session {session_id}")
                
            except Exception as e:
                self.logger.error(f"Error cleaning up session {session_id}: {e}")
    
    def cleanup_all_sessions(self):
        """Clean up all sandbox sessions"""
        session_ids = list(self.active_sessions.keys())
        for session_id in session_ids:
            self.cleanup_session(session_id)
    
    def get_sandbox_stats(self) -> Dict[str, Any]:
        """Get sandbox statistics"""
        return {
            'active_sessions': len(self.active_sessions),
            'total_sessions_created': self.session_counter,
            'sandbox_directory': self.sandbox_dir,
            'timeout': self.timeout,
            'network_allowed': self.sandbox_config['network_allowed'],
            'registry_allowed': self.sandbox_config['registry_allowed'],
            'last_update': datetime.now().isoformat()
        } 