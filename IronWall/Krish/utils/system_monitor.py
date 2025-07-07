"""
IronWall Antivirus - System Monitor Utility
Real-time system monitoring for CPU, memory, and system status
"""

import psutil
import time
import threading
from typing import Dict, Optional

class SystemMonitor:
    def __init__(self):
        self.monitoring = False
        self.monitor_thread = None
        self.current_stats = {
            'cpu_percent': 0.0,
            'memory_percent': 0.0,
            'system_status': 'Stable',
            'last_update': time.time()
        }
        
        # Start monitoring
        self.start_monitoring()
    
    def start_monitoring(self):
        """Start background system monitoring"""
        if not self.monitoring:
            self.monitoring = True
            self.monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
            self.monitor_thread.start()
    
    def stop_monitoring(self):
        """Stop background system monitoring"""
        self.monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=1)
    
    def _monitor_loop(self):
        """Background monitoring loop"""
        while self.monitoring:
            try:
                # Get CPU usage
                cpu_percent = psutil.cpu_percent(interval=0.05)
                
                # Get memory usage
                memory = psutil.virtual_memory()
                memory_percent = memory.percent
                
                # Determine system status
                system_status = self._determine_system_status(cpu_percent, memory_percent)
                
                # Update current stats
                self.current_stats.update({
                    'cpu_percent': cpu_percent,
                    'memory_percent': memory_percent,
                    'system_status': system_status,
                    'last_update': time.time()
                })
                
                # Sleep for a very short interval (ultra-fast updates)
                time.sleep(0.1)
                
            except Exception as e:
                print(f"Error in system monitoring: {e}")
                time.sleep(0.5)
    
    def _determine_system_status(self, cpu_percent: float, memory_percent: float) -> str:
        """Determine overall system status based on CPU and memory usage"""
        # High load conditions
        if cpu_percent > 80 or memory_percent > 80:
            return "High Load"
        
        # Moderate load conditions
        if cpu_percent > 60 or memory_percent > 60:
            return "Moderate"
        
        # Stable conditions
        return "Stable"
    
    def get_cpu_usage(self) -> float:
        """Get current CPU usage percentage"""
        return self.current_stats['cpu_percent']
    
    def get_memory_usage(self) -> float:
        """Get current memory usage percentage"""
        return self.current_stats['memory_percent']
    
    def get_system_status(self) -> str:
        """Get current system status"""
        return self.current_stats['system_status']
    
    def get_detailed_stats(self) -> Dict:
        """Get detailed system statistics"""
        try:
            # CPU information
            cpu_count = psutil.cpu_count()
            cpu_freq = psutil.cpu_freq()
            
            # Memory information
            memory = psutil.virtual_memory()
            
            # Disk information
            try:
                disk = psutil.disk_usage('/')
            except:
                # On Windows, try C: drive
                disk = psutil.disk_usage('C:\\')
            
            # Network information
            network = psutil.net_io_counters()
            
            return {
                'cpu': {
                    'percent': self.current_stats['cpu_percent'],
                    'count': cpu_count,
                    'frequency': cpu_freq.current if cpu_freq else 0,
                    'load_avg': psutil.getloadavg() if hasattr(psutil, 'getloadavg') else None
                },
                'memory': {
                    'percent': self.current_stats['memory_percent'],
                    'total': memory.total,
                    'available': memory.available,
                    'used': memory.used,
                    'free': memory.free
                },
                'disk': {
                    'total': disk.total,
                    'used': disk.used,
                    'free': disk.free,
                    'percent': (disk.used / disk.total) * 100
                },
                'network': {
                    'bytes_sent': network.bytes_sent,
                    'bytes_recv': network.bytes_recv,
                    'packets_sent': network.packets_sent,
                    'packets_recv': network.packets_recv
                },
                'system_status': self.current_stats['system_status'],
                'last_update': self.current_stats['last_update']
            }
        except Exception as e:
            print(f"Error getting detailed stats: {e}")
            return {}
    
    def get_process_list(self, limit: int = 10) -> list:
        """Get list of top processes by CPU usage"""
        try:
            processes = []
            for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
                try:
                    processes.append(proc.info)
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass
            
            # Sort by CPU usage and return top processes
            processes.sort(key=lambda x: x['cpu_percent'], reverse=True)
            return processes[:limit]
            
        except Exception as e:
            print(f"Error getting process list: {e}")
            return []
    
    def get_system_info(self) -> Dict:
        """Get basic system information"""
        try:
            return {
                'platform': psutil.sys.platform,
                'system': psutil.sys.platform,
                'release': psutil.sys.platform,
                'version': psutil.sys.version,
                'machine': psutil.sys.platform,
                'processor': psutil.sys.platform,
                'boot_time': psutil.boot_time()
            }
        except Exception as e:
            print(f"Error getting system info: {e}")
            return {}
    
    def is_system_healthy(self) -> bool:
        """Check if system is in healthy state"""
        cpu_percent = self.get_cpu_usage()
        memory_percent = self.get_memory_usage()
        
        # System is healthy if CPU and memory usage are below 80%
        return cpu_percent < 80 and memory_percent < 80
    
    def get_system_stats(self) -> Dict:
        """Get system statistics (alias for get_detailed_stats)"""
        return self.get_detailed_stats()
    
    def get_security_status(self) -> Dict:
        """Get security status information"""
        try:
            return {
                'system_healthy': self.is_system_healthy(),
                'performance_score': self.get_performance_score(),
                'cpu_usage': self.get_cpu_usage(),
                'memory_usage': self.get_memory_usage(),
                'system_status': self.get_system_status(),
                'last_update': self.current_stats['last_update']
            }
        except Exception as e:
            print(f"Error getting security status: {e}")
            return {}
    
    def get_resource_usage(self) -> Dict:
        """Get resource usage information (alias for get_detailed_stats)"""
        return self.get_detailed_stats()
    
    def get_performance_score(self) -> int:
        """Get a performance score from 0-100"""
        try:
            cpu_percent = self.get_cpu_usage()
            memory_percent = self.get_memory_usage()
            
            # Calculate score (lower usage = higher score)
            cpu_score = max(0, 100 - cpu_percent)
            memory_score = max(0, 100 - memory_percent)
            
            # Average the scores
            return int((cpu_score + memory_score) / 2)
            
        except Exception as e:
            print(f"Error calculating performance score: {e}")
            return 50 