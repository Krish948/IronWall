"""
IronWall Antivirus - Network Protection Module
Monitor and block malicious IPs, ports, and domains with firewall rules
"""

import os
import socket
import threading
import time
import json
import requests
import psutil
from typing import Dict, List, Optional, Any, Set
from datetime import datetime, timedelta
import ipaddress
import re
import subprocess
import platform

class NetworkProtection:
    def __init__(self, rules_file: str = None):
        self.rules_file = rules_file or os.path.join(os.path.dirname(__file__), '..', '..', 'network_rules.json')
        
        # Network monitoring state
        self.monitoring = False
        self.monitor_thread = None
        
        # Firewall rules
        self.blocked_ips = set()
        self.blocked_domains = set()
        self.blocked_ports = set()
        self.allowed_ips = set()
        self.allowed_domains = set()
        
        # Network activity tracking
        self.connection_log = []
        self.suspicious_connections = []
        self.blocked_connections = []
        
        # Threat intelligence sources
        self.threat_feeds = {
            'abuseipdb': 'https://api.abuseipdb.com/api/v2/blacklist',
            'tor_exit_nodes': 'https://check.torproject.org/exit-addresses',
            'malware_domains': 'https://mirror.cedia.org.ec/malwaredomains/domains.txt',
            'phishing_database': 'https://openphish.com/feed.txt'
        }
        
        # Network monitoring settings
        self.monitor_settings = {
            'log_connections': True,
            'block_suspicious': True,
            'alert_on_block': True,
            'max_log_size': 10000,
            'update_interval': 300  # 5 minutes
        }
        
        # Load existing rules
        self._load_rules()
        
        # Initialize threat feeds
        self._initialize_threat_feeds()
        
        # Start monitoring
        self.start_monitoring()
    
    def _load_rules(self):
        """Load firewall rules from file"""
        try:
            if os.path.exists(self.rules_file):
                with open(self.rules_file, 'r') as f:
                    rules = json.load(f)
                
                self.blocked_ips = set(rules.get('blocked_ips', []))
                self.blocked_domains = set(rules.get('blocked_domains', []))
                self.blocked_ports = set(rules.get('blocked_ports', []))
                self.allowed_ips = set(rules.get('allowed_ips', []))
                self.allowed_domains = set(rules.get('allowed_domains', []))
                
                print(f"Network Protection: Loaded {len(self.blocked_ips)} blocked IPs, {len(self.blocked_domains)} blocked domains")
            else:
                # Create default rules file
                self._create_default_rules()
                
        except Exception as e:
            print(f"Network Protection: Error loading rules: {e}")
            self._create_default_rules()
    
    def _create_default_rules(self):
        """Create default firewall rules"""
        default_rules = {
            'blocked_ips': [
                '127.0.0.1',  # Localhost (for testing)
                '0.0.0.0',    # Invalid IP
                '255.255.255.255'  # Broadcast
            ],
            'blocked_domains': [
                'malware.example.com',
                'phishing.example.com'
            ],
            'blocked_ports': [
                22,    # SSH (if not needed)
                23,    # Telnet
                3389,  # RDP (if not needed)
                1433,  # SQL Server (if not needed)
                3306,  # MySQL (if not needed)
                5432   # PostgreSQL (if not needed)
            ],
            'allowed_ips': [
                '8.8.8.8',      # Google DNS
                '8.8.4.4',      # Google DNS
                '1.1.1.1',      # Cloudflare DNS
                '1.0.0.1'       # Cloudflare DNS
            ],
            'allowed_domains': [
                'google.com',
                'microsoft.com',
                'cloudflare.com'
            ]
        }
        
        try:
            with open(self.rules_file, 'w') as f:
                json.dump(default_rules, f, indent=2)
            
            self.blocked_ips = set(default_rules['blocked_ips'])
            self.blocked_domains = set(default_rules['blocked_domains'])
            self.blocked_ports = set(default_rules['blocked_ports'])
            self.allowed_ips = set(default_rules['allowed_ips'])
            self.allowed_domains = set(default_rules['allowed_domains'])
            
            print("Network Protection: Created default rules")
            
        except Exception as e:
            print(f"Network Protection: Error creating default rules: {e}")
    
    def _save_rules(self):
        """Save firewall rules to file"""
        try:
            rules = {
                'blocked_ips': list(self.blocked_ips),
                'blocked_domains': list(self.blocked_domains),
                'blocked_ports': list(self.blocked_ports),
                'allowed_ips': list(self.allowed_ips),
                'allowed_domains': list(self.allowed_domains),
                'last_updated': datetime.now().isoformat()
            }
            
            with open(self.rules_file, 'w') as f:
                json.dump(rules, f, indent=2)
                
        except Exception as e:
            print(f"Network Protection: Error saving rules: {e}")
    
    def _initialize_threat_feeds(self):
        """Initialize threat intelligence feeds"""
        try:
            # Start background thread to update threat feeds
            update_thread = threading.Thread(target=self._update_threat_feeds, daemon=True)
            update_thread.start()
            
        except Exception as e:
            print(f"Network Protection: Error initializing threat feeds: {e}")
    
    def _update_threat_feeds(self):
        """Update threat intelligence feeds"""
        while True:
            try:
                self._update_tor_exit_nodes()
                self._update_malware_domains()
                time.sleep(self.monitor_settings['update_interval'])
                
            except Exception as e:
                print(f"Network Protection: Error updating threat feeds: {e}")
                time.sleep(60)
    
    def _update_tor_exit_nodes(self):
        """Update Tor exit node list"""
        try:
            response = requests.get(self.threat_feeds['tor_exit_nodes'], timeout=30)
            if response.status_code == 200:
                lines = response.text.split('\n')
                tor_ips = set()
                
                for line in lines:
                    if line.startswith('ExitAddress'):
                        parts = line.split()
                        if len(parts) >= 2:
                            tor_ips.add(parts[1])
                
                # Add Tor exit nodes to blocked IPs
                self.blocked_ips.update(tor_ips)
                print(f"Network Protection: Updated {len(tor_ips)} Tor exit nodes")
                
        except Exception as e:
            print(f"Network Protection: Error updating Tor exit nodes: {e}")
    
    def _update_malware_domains(self):
        """Update malware domain list"""
        try:
            response = requests.get(self.threat_feeds['malware_domains'], timeout=30)
            if response.status_code == 200:
                lines = response.text.split('\n')
                malware_domains = set()
                
                for line in lines:
                    if line and not line.startswith('#'):
                        domain = line.strip().split('\t')[-1]
                        if domain and '.' in domain:
                            malware_domains.add(domain)
                
                # Add malware domains to blocked domains
                self.blocked_domains.update(malware_domains)
                print(f"Network Protection: Updated {len(malware_domains)} malware domains")
                
        except Exception as e:
            print(f"Network Protection: Error updating malware domains: {e}")
    
    def start_monitoring(self):
        """Start network monitoring"""
        if not self.monitoring:
            self.monitoring = True
            self.monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
            self.monitor_thread.start()
            print("Network Protection: Started network monitoring")
    
    def stop_monitoring(self):
        """Stop network monitoring"""
        self.monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=1)
            print("Network Protection: Stopped network monitoring")
    
    def _monitor_loop(self):
        """Main network monitoring loop"""
        while self.monitoring:
            try:
                # Monitor current network connections
                self._monitor_connections()
                
                # Check for suspicious activity
                self._check_suspicious_activity()
                
                # Sleep before next check
                time.sleep(5)
                
            except Exception as e:
                print(f"Network Protection: Error in monitoring loop: {e}")
                time.sleep(10)
    
    def _monitor_connections(self):
        """Monitor current network connections"""
        try:
            connections = psutil.net_connections()
            
            for conn in connections:
                if conn.status == 'ESTABLISHED' and conn.raddr:
                    connection_info = {
                        'timestamp': datetime.now().isoformat(),
                        'local_ip': conn.laddr.ip,
                        'local_port': conn.laddr.port,
                        'remote_ip': conn.raddr.ip,
                        'remote_port': conn.raddr.port,
                        'status': conn.status,
                        'pid': conn.pid
                    }
                    
                    # Get process information
                    try:
                        if conn.pid:
                            process = psutil.Process(conn.pid)
                            connection_info['process_name'] = process.name()
                            connection_info['process_exe'] = process.exe()
                    except:
                        connection_info['process_name'] = 'Unknown'
                        connection_info['process_exe'] = 'Unknown'
                    
                    # Check if connection should be blocked
                    if self._should_block_connection(connection_info):
                        self._block_connection(connection_info)
                    
                    # Log connection
                    if self.monitor_settings['log_connections']:
                        self.connection_log.append(connection_info)
                        
                        # Limit log size
                        if len(self.connection_log) > self.monitor_settings['max_log_size']:
                            self.connection_log = self.connection_log[-self.monitor_settings['max_log_size']:]
                
        except Exception as e:
            print(f"Network Protection: Error monitoring connections: {e}")
    
    def _should_block_connection(self, connection_info: Dict[str, Any]) -> bool:
        """Determine if a connection should be blocked"""
        remote_ip = connection_info['remote_ip']
        remote_port = connection_info['remote_port']
        
        # Check if IP is blocked
        if remote_ip in self.blocked_ips:
            return True
        
        # Check if IP is in blocked ranges
        for blocked_range in self._get_blocked_ranges():
            try:
                if ipaddress.ip_address(remote_ip) in ipaddress.ip_network(blocked_range):
                    return True
            except:
                pass
        
        # Check if port is blocked
        if remote_port in self.blocked_ports:
            return True
        
        # Check if IP is allowed (whitelist takes precedence)
        if remote_ip in self.allowed_ips:
            return False
        
        # Check for suspicious patterns
        if self._is_suspicious_connection(connection_info):
            return True
        
        return False
    
    def _get_blocked_ranges(self) -> List[str]:
        """Get list of blocked IP ranges"""
        # Common malicious IP ranges
        return [
            '10.0.0.0/8',      # Private network (if blocking private networks)
            '172.16.0.0/12',   # Private network
            '192.168.0.0/16',  # Private network
            '224.0.0.0/4',     # Multicast
            '240.0.0.0/4'      # Reserved
        ]
    
    def _is_suspicious_connection(self, connection_info: Dict[str, Any]) -> bool:
        """Check if connection is suspicious"""
        remote_ip = connection_info['remote_ip']
        remote_port = connection_info['remote_port']
        process_name = connection_info.get('process_name', '').lower()
        
        # Check for suspicious ports
        suspicious_ports = [22, 23, 3389, 1433, 3306, 5432, 27017, 6379]
        if remote_port in suspicious_ports:
            return True
        
        # Check for suspicious process names
        suspicious_processes = ['cmd', 'powershell', 'wscript', 'cscript', 'python', 'perl', 'ruby']
        if any(proc in process_name for proc in suspicious_processes):
            return True
        
        # Check for connections to known malicious IPs
        malicious_ip_patterns = [
            r'^192\.168\.',  # Private network (if suspicious)
            r'^10\.',        # Private network
            r'^172\.(1[6-9]|2[0-9]|3[0-1])\.',  # Private network
        ]
        
        for pattern in malicious_ip_patterns:
            if re.match(pattern, remote_ip):
                return True
        
        return False
    
    def _block_connection(self, connection_info: Dict[str, Any]):
        """Block a suspicious connection"""
        try:
            # Add to blocked connections log
            self.blocked_connections.append({
                **connection_info,
                'blocked_at': datetime.now().isoformat(),
                'reason': 'Suspicious connection detected'
            })
            
            # Try to terminate the connection
            if connection_info.get('pid'):
                try:
                    process = psutil.Process(connection_info['pid'])
                    process.terminate()
                    print(f"Network Protection: Terminated process {connection_info['pid']} for suspicious connection")
                except:
                    pass
            
            # Add IP to blocked list
            remote_ip = connection_info['remote_ip']
            if remote_ip not in self.blocked_ips:
                self.blocked_ips.add(remote_ip)
                self._save_rules()
            
            print(f"Network Protection: Blocked connection to {remote_ip}:{connection_info['remote_port']}")
            
        except Exception as e:
            print(f"Network Protection: Error blocking connection: {e}")
    
    def _check_suspicious_activity(self):
        """Check for suspicious network activity patterns"""
        try:
            # Check for rapid connection attempts
            recent_connections = [
                conn for conn in self.connection_log
                if datetime.fromisoformat(conn['timestamp']) > datetime.now() - timedelta(minutes=5)
            ]
            
            # Group by remote IP
            ip_connections = {}
            for conn in recent_connections:
                remote_ip = conn['remote_ip']
                if remote_ip not in ip_connections:
                    ip_connections[remote_ip] = []
                ip_connections[remote_ip].append(conn)
            
            # Check for suspicious patterns
            for remote_ip, connections in ip_connections.items():
                if len(connections) > 10:  # More than 10 connections in 5 minutes
                    self.suspicious_connections.append({
                        'timestamp': datetime.now().isoformat(),
                        'remote_ip': remote_ip,
                        'connection_count': len(connections),
                        'pattern': 'Rapid connection attempts'
                    })
                    
                    # Block the IP
                    if remote_ip not in self.blocked_ips:
                        self.blocked_ips.add(remote_ip)
                        self._save_rules()
                        print(f"Network Protection: Blocked IP {remote_ip} due to rapid connections")
                
        except Exception as e:
            print(f"Network Protection: Error checking suspicious activity: {e}")
    
    def add_blocked_ip(self, ip: str, reason: str = "Manual block"):
        """Add IP to blocked list"""
        try:
            # Validate IP address
            ipaddress.ip_address(ip)
            
            self.blocked_ips.add(ip)
            self._save_rules()
            
            print(f"Network Protection: Added {ip} to blocked IPs ({reason})")
            
        except Exception as e:
            print(f"Network Protection: Error adding blocked IP: {e}")
    
    def add_blocked_domain(self, domain: str, reason: str = "Manual block"):
        """Add domain to blocked list"""
        try:
            self.blocked_domains.add(domain)
            self._save_rules()
            
            print(f"Network Protection: Added {domain} to blocked domains ({reason})")
            
        except Exception as e:
            print(f"Network Protection: Error adding blocked domain: {e}")
    
    def add_blocked_port(self, port: int, reason: str = "Manual block"):
        """Add port to blocked list"""
        try:
            if 0 <= port <= 65535:
                self.blocked_ports.add(port)
                self._save_rules()
                
                print(f"Network Protection: Added port {port} to blocked ports ({reason})")
            else:
                print(f"Network Protection: Invalid port number: {port}")
                
        except Exception as e:
            print(f"Network Protection: Error adding blocked port: {e}")
    
    def remove_blocked_ip(self, ip: str):
        """Remove IP from blocked list"""
        try:
            self.blocked_ips.discard(ip)
            self._save_rules()
            
            print(f"Network Protection: Removed {ip} from blocked IPs")
            
        except Exception as e:
            print(f"Network Protection: Error removing blocked IP: {e}")
    
    def remove_blocked_domain(self, domain: str):
        """Remove domain from blocked list"""
        try:
            self.blocked_domains.discard(domain)
            self._save_rules()
            
            print(f"Network Protection: Removed {domain} from blocked domains")
            
        except Exception as e:
            print(f"Network Protection: Error removing blocked domain: {e}")
    
    def remove_blocked_port(self, port: int):
        """Remove port from blocked list"""
        try:
            self.blocked_ports.discard(port)
            self._save_rules()
            
            print(f"Network Protection: Removed port {port} from blocked ports")
            
        except Exception as e:
            print(f"Network Protection: Error removing blocked port: {e}")
    
    def get_network_stats(self) -> Dict[str, Any]:
        """Get network protection statistics"""
        return {
            'monitoring_active': self.monitoring,
            'blocked_ips_count': len(self.blocked_ips),
            'blocked_domains_count': len(self.blocked_domains),
            'blocked_ports_count': len(self.blocked_ports),
            'allowed_ips_count': len(self.allowed_ips),
            'allowed_domains_count': len(self.allowed_domains),
            'connection_log_size': len(self.connection_log),
            'suspicious_connections_count': len(self.suspicious_connections),
            'blocked_connections_count': len(self.blocked_connections),
            'last_update': datetime.now().isoformat()
        }
    
    def get_connection_log(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get recent connection log"""
        return self.connection_log[-limit:]
    
    def get_suspicious_connections(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Get suspicious connections"""
        return self.suspicious_connections[-limit:]
    
    def get_blocked_connections(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Get blocked connections"""
        return self.blocked_connections[-limit:]
    
    def clear_logs(self):
        """Clear all logs"""
        self.connection_log.clear()
        self.suspicious_connections.clear()
        self.blocked_connections.clear()
        print("Network Protection: All logs cleared")
    
    def export_rules(self, file_path: str):
        """Export firewall rules to file"""
        try:
            rules = {
                'blocked_ips': list(self.blocked_ips),
                'blocked_domains': list(self.blocked_domains),
                'blocked_ports': list(self.blocked_ports),
                'allowed_ips': list(self.allowed_ips),
                'allowed_domains': list(self.allowed_domains),
                'export_date': datetime.now().isoformat()
            }
            
            with open(file_path, 'w') as f:
                json.dump(rules, f, indent=2)
            
            print(f"Network Protection: Rules exported to {file_path}")
            
        except Exception as e:
            print(f"Network Protection: Error exporting rules: {e}")
    
    def import_rules(self, file_path: str):
        """Import firewall rules from file"""
        try:
            with open(file_path, 'r') as f:
                rules = json.load(f)
            
            self.blocked_ips = set(rules.get('blocked_ips', []))
            self.blocked_domains = set(rules.get('blocked_domains', []))
            self.blocked_ports = set(rules.get('blocked_ports', []))
            self.allowed_ips = set(rules.get('allowed_ips', []))
            self.allowed_domains = set(rules.get('allowed_domains', []))
            
            self._save_rules()
            
            print(f"Network Protection: Rules imported from {file_path}")
            
        except Exception as e:
            print(f"Network Protection: Error importing rules: {e}") 