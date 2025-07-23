"""
IronWall Antivirus - CLI Interface
Command-line interface for triggering scans, updates, and viewing logs
"""

import argparse
import json
import sys
import os
import time
from datetime import datetime
from typing import Dict, List, Optional, Any
import threading

# Import IronWall modules
from core.scanner import IronWallScanner
from core.ai_engine import AIBehavioralEngine
from core.process_monitor import ProcessMonitor
from core.cloud_intelligence import CloudThreatIntelligence
from core.network_protection import NetworkProtection
from core.ransomware_shield import RansomwareShield
from core.restore_point import RestorePointCreator
from utils.threat_database import ThreatDatabase
from utils.system_monitor import SystemMonitor
from utils.quarantine import QuarantineManager
from utils.scheduler import Scheduler
from utils.settings_manager import SettingsManager

class IronWallCLI:
    def __init__(self):
        # Initialize components
        self.threat_db = ThreatDatabase()
        self.scanner = IronWallScanner(self.threat_db)
        self.ai_engine = AIBehavioralEngine()
        self.process_monitor = ProcessMonitor(self.threat_db)
        self.cloud_intel = CloudThreatIntelligence()
        self.network_protection = NetworkProtection()
        self.ransomware_shield = RansomwareShield()
        self.restore_point = RestorePointCreator()
        self.system_monitor = SystemMonitor()
        self.quarantine = QuarantineManager()
        self.scheduler = Scheduler()
        self.settings = SettingsManager()
        
        # CLI state
        self.verbose = False
        self.json_output = False
    
    def setup_parser(self) -> argparse.ArgumentParser:
        """Setup command line argument parser"""
        parser = argparse.ArgumentParser(
            description="IronWall Antivirus CLI",
            formatter_class=argparse.RawDescriptionHelpFormatter,
            epilog="""
Examples:
  ironwall scan /path/to/scan
  ironwall scan --deep --ai
  ironwall process-monitor --list
  ironwall cloud-check /path/to/file
  ironwall network --block-ip 192.168.1.100
  ironwall ransomware --stats
  ironwall restore-point --create "Before scan"
  ironwall quarantine --list
  ironwall scheduler --add "daily" "/home/user" "09:00"
            """
        )
        
        # Global options
        parser.add_argument('--verbose', '-v', action='store_true', help='Verbose output')
        parser.add_argument('--json', action='store_true', help='Output in JSON format')
        
        # Subcommands
        subparsers = parser.add_subparsers(dest='command', help='Available commands')
        
        # Scan command
        scan_parser = subparsers.add_parser('scan', help='Scan files and directories')
        scan_parser.add_argument('path', help='Path to scan')
        scan_parser.add_argument('--deep', action='store_true', help='Enable deep scanning')
        scan_parser.add_argument('--ai', action='store_true', help='Enable AI analysis')
        scan_parser.add_argument('--cloud', action='store_true', help='Enable cloud intelligence')
        scan_parser.add_argument('--output', help='Output file for results')
        
        # Process monitor command
        proc_parser = subparsers.add_parser('process-monitor', help='Process monitoring')
        proc_parser.add_argument('--list', action='store_true', help='List monitored processes')
        proc_parser.add_argument('--suspicious', action='store_true', help='Show suspicious processes')
        proc_parser.add_argument('--kill', type=int, help='Kill process by PID')
        proc_parser.add_argument('--block', type=int, help='Block process by PID')
        proc_parser.add_argument('--stats', action='store_true', help='Show monitoring statistics')
        
        # Cloud intelligence command
        cloud_parser = subparsers.add_parser('cloud-check', help='Cloud threat intelligence')
        cloud_parser.add_argument('file', help='File to check')
        cloud_parser.add_argument('--hash', help='Check by hash instead of file')
        cloud_parser.add_argument('--url', help='Check URL instead of file')
        cloud_parser.add_argument('--sources', nargs='+', help='Specific sources to check')
        
        # Network protection command
        net_parser = subparsers.add_parser('network', help='Network protection')
        net_parser.add_argument('--block-ip', help='Block IP address')
        net_parser.add_argument('--block-domain', help='Block domain')
        net_parser.add_argument('--block-port', type=int, help='Block port')
        net_parser.add_argument('--unblock-ip', help='Unblock IP address')
        net_parser.add_argument('--unblock-domain', help='Unblock domain')
        net_parser.add_argument('--unblock-port', type=int, help='Unblock port')
        net_parser.add_argument('--list', action='store_true', help='List blocked items')
        net_parser.add_argument('--stats', action='store_true', help='Show network statistics')
        net_parser.add_argument('--export', help='Export rules to file')
        net_parser.add_argument('--import-rules', help='Import rules from file')
        
        # Ransomware shield command
        ransom_parser = subparsers.add_parser('ransomware', help='Ransomware protection')
        ransom_parser.add_argument('--stats', action='store_true', help='Show protection statistics')
        ransom_parser.add_argument('--activities', action='store_true', help='Show suspicious activities')
        ransom_parser.add_argument('--restore', help='Restore file from backup')
        ransom_parser.add_argument('--add-protected', help='Add protected directory')
        ransom_parser.add_argument('--remove-protected', help='Remove protected directory')
        ransom_parser.add_argument('--cleanup', type=int, help='Clean up backups older than N days')
        
        # Restore point command
        restore_parser = subparsers.add_parser('restore-point', help='System restore points')
        restore_parser.add_argument('--create', help='Create restore point with description')
        restore_parser.add_argument('--list', action='store_true', help='List restore points')
        restore_parser.add_argument('--restore', help='Restore to specific point ID')
        restore_parser.add_argument('--delete', help='Delete restore point by ID')
        restore_parser.add_argument('--stats', action='store_true', help='Show restore point statistics')
        
        # Quarantine command
        quarantine_parser = subparsers.add_parser('quarantine', help='Quarantine management')
        quarantine_parser.add_argument('--list', action='store_true', help='List quarantined files')
        quarantine_parser.add_argument('--restore', help='Restore file from quarantine')
        quarantine_parser.add_argument('--delete', help='Delete file from quarantine')
        quarantine_parser.add_argument('--stats', action='store_true', help='Show quarantine statistics')
        
        # Scheduler command
        scheduler_parser = subparsers.add_parser('scheduler', help='Scan scheduling')
        scheduler_parser.add_argument('--add', nargs=3, metavar=('NAME', 'PATH', 'TIME'), help='Add scheduled scan')
        scheduler_parser.add_argument('--remove', help='Remove scheduled scan')
        scheduler_parser.add_argument('--list', action='store_true', help='List scheduled scans')
        scheduler_parser.add_argument('--run', help='Run scheduled scan immediately')
        scheduler_parser.add_argument('--enable', help='Enable scheduled scan')
        scheduler_parser.add_argument('--disable', help='Disable scheduled scan')
        
        # System command
        system_parser = subparsers.add_parser('system', help='System information')
        system_parser.add_argument('--stats', action='store_true', help='Show system statistics')
        system_parser.add_argument('--health', action='store_true', help='Check system health')
        system_parser.add_argument('--processes', action='store_true', help='Show running processes')
        
        # Settings command
        settings_parser = subparsers.add_parser('settings', help='Settings management')
        settings_parser.add_argument('--get', help='Get setting value')
        settings_parser.add_argument('--set', nargs=2, metavar=('KEY', 'VALUE'), help='Set setting value')
        settings_parser.add_argument('--list', action='store_true', help='List all settings')
        settings_parser.add_argument('--reset', action='store_true', help='Reset to default settings')
        
        # Reset command
        reset_parser = subparsers.add_parser('reset', help='Data reset operations')
        reset_parser.add_argument('--all', action='store_true', help='Reset all data to factory defaults')
        reset_parser.add_argument('--settings', action='store_true', help='Reset only settings')
        reset_parser.add_argument('--quarantine', action='store_true', help='Reset only quarantine')
        reset_parser.add_argument('--logs', action='store_true', help='Reset only logs')
        reset_parser.add_argument('--no-backup', action='store_true', help='Skip backup creation')
        reset_parser.add_argument('--confirm', action='store_true', help='Skip confirmation prompt')
        
        # Update command
        update_parser = subparsers.add_parser('update', help='Update components')
        update_parser.add_argument('--threat-db', action='store_true', help='Update threat database')
        update_parser.add_argument('--ai-models', action='store_true', help='Update AI models')
        update_parser.add_argument('--all', action='store_true', help='Update all components')
        
        # Diagnostic command
        diag_parser = subparsers.add_parser('diagnostic', help='System diagnostics')
        diag_parser.add_argument('--generate', action='store_true', help='Generate diagnostic report')
        diag_parser.add_argument('--output', help='Output file for diagnostic report')
        
        return parser
    
    def run(self, args: List[str] = None):
        """Run the CLI with given arguments"""
        parser = self.setup_parser()
        parsed_args = parser.parse_args(args)
        
        # Set global options
        self.verbose = parsed_args.verbose
        self.json_output = parsed_args.json
        
        if not parsed_args.command:
            parser.print_help()
            return
        
        try:
            # Execute command
            if parsed_args.command == 'scan':
                self.cmd_scan(parsed_args)
            elif parsed_args.command == 'process-monitor':
                self.cmd_process_monitor(parsed_args)
            elif parsed_args.command == 'cloud-check':
                self.cmd_cloud_check(parsed_args)
            elif parsed_args.command == 'network':
                self.cmd_network(parsed_args)
            elif parsed_args.command == 'ransomware':
                self.cmd_ransomware(parsed_args)
            elif parsed_args.command == 'restore-point':
                self.cmd_restore_point(parsed_args)
            elif parsed_args.command == 'quarantine':
                self.cmd_quarantine(parsed_args)
            elif parsed_args.command == 'scheduler':
                self.cmd_scheduler(parsed_args)
            elif parsed_args.command == 'system':
                self.cmd_system(parsed_args)
            elif parsed_args.command == 'settings':
                self.cmd_settings(parsed_args)
            elif parsed_args.command == 'reset':
                self.cmd_reset(parsed_args)
            elif parsed_args.command == 'update':
                self.cmd_update(parsed_args)
            elif parsed_args.command == 'diagnostic':
                self.cmd_diagnostic(parsed_args)
            else:
                print(f"Unknown command: {parsed_args.command}")
                parser.print_help()
                
        except KeyboardInterrupt:
            print("\nOperation cancelled by user")
        except Exception as e:
            print(f"Error: {e}")
            if self.verbose:
                import traceback
                traceback.print_exc()
    
    def output_result(self, result: Any):
        """Output result in appropriate format"""
        if self.json_output:
            print(json.dumps(result, indent=2, default=str))
        else:
            if isinstance(result, dict):
                for key, value in result.items():
                    print(f"{key}: {value}")
            elif isinstance(result, list):
                for item in result:
                    print(item)
            else:
                print(result)
    
    def cmd_scan(self, args):
        """Handle scan command"""
        if not os.path.exists(args.path):
            print(f"Error: Path {args.path} does not exist")
            return
        
        print(f"Scanning {args.path}...")
        
        # Initialize scan options
        scan_options = {
            'deep_scan': args.deep,
            'ai_analysis': args.ai,
            'cloud_check': args.cloud
        }
        
        # Perform scan
        results = self._perform_scan(args.path, scan_options)
        
        # Output results
        if args.output:
            with open(args.output, 'w') as f:
                json.dump(results, f, indent=2, default=str)
            print(f"Results saved to {args.output}")
        else:
            self.output_result(results)
    
    def _perform_scan(self, path: str, options: Dict[str, bool]) -> Dict[str, Any]:
        """Perform comprehensive scan"""
        results = {
            'scan_path': path,
            'scan_time': datetime.now().isoformat(),
            'options': options,
            'threats_found': [],
            'ai_analysis': [],
            'cloud_results': [],
        }
        
        # Basic file scan
        def scan_callback(threat_info):
            results['threats_found'].append(threat_info)
        
        def progress_callback(current, total):
            if self.verbose:
                print(f"Scanning: {current}/{total} files")
        
        # Perform scan
        self.scanner.scan_folder(path, scan_callback, progress_callback, options['deep_scan'])
        
        # AI analysis
        if options['ai_analysis']:
            if os.path.isfile(path):
                ai_result = self.ai_engine.analyze_file(path)
                results['ai_analysis'].append(ai_result)
            else:
                # Analyze first few files in directory
                for root, dirs, files in os.walk(path):
                    for file in files[:10]:  # Limit to first 10 files
                        file_path = os.path.join(root, file)
                        ai_result = self.ai_engine.analyze_file(file_path)
                        results['ai_analysis'].append(ai_result)
        
        # Cloud intelligence check
        if options['cloud_check']:
            if os.path.isfile(path):
                cloud_result = self.cloud_intel.check_file_hash(self._get_file_hash(path))
                results['cloud_results'].append(cloud_result)
        
        return results
    
    def _get_file_hash(self, file_path: str) -> str:
        """Get file hash"""
        import hashlib
        with open(file_path, 'rb') as f:
            return hashlib.md5(f.read()).hexdigest()
    
    def cmd_process_monitor(self, args):
        """Handle process monitor command"""
        if args.list:
            processes = self.process_monitor.get_process_list()
            self.output_result(processes)
        elif args.suspicious:
            suspicious = self.process_monitor.get_suspicious_processes()
            self.output_result(suspicious)
        elif args.kill:
            success = self.process_monitor.kill_process(args.kill)
            self.output_result({'killed': success, 'pid': args.kill})
        elif args.block:
            success = self.process_monitor.block_process(args.block)
            self.output_result({'blocked': success, 'pid': args.block})
        elif args.stats:
            stats = self.process_monitor.get_process_stats()
            self.output_result(stats)
        else:
            print("Use --list, --suspicious, --kill, --block, or --stats")
    
    def cmd_cloud_check(self, args):
        """Handle cloud check command"""
        if args.hash:
            result = self.cloud_intel.check_file_hash(args.hash)
            self.output_result(result)
        elif args.url:
            result = self.cloud_intel.check_url(args.url)
            self.output_result(result)
        elif args.file:
            if not os.path.exists(args.file):
                print(f"Error: File {args.file} does not exist")
                return
            
            file_hash = self._get_file_hash(args.file)
            result = self.cloud_intel.check_file_hash(file_hash, args.sources)
            self.output_result(result)
        else:
            print("Use --hash, --url, or provide a file path")
    
    def cmd_network(self, args):
        """Handle network command"""
        if args.block_ip:
            self.network_protection.add_blocked_ip(args.block_ip)
            print(f"Blocked IP: {args.block_ip}")
        elif args.block_domain:
            self.network_protection.add_blocked_domain(args.block_domain)
            print(f"Blocked domain: {args.block_domain}")
        elif args.block_port:
            self.network_protection.add_blocked_port(args.block_port)
            print(f"Blocked port: {args.block_port}")
        elif args.unblock_ip:
            self.network_protection.remove_blocked_ip(args.unblock_ip)
            print(f"Unblocked IP: {args.unblock_ip}")
        elif args.unblock_domain:
            self.network_protection.remove_blocked_domain(args.unblock_domain)
            print(f"Unblocked domain: {args.unblock_domain}")
        elif args.unblock_port:
            self.network_protection.remove_blocked_port(args.unblock_port)
            print(f"Unblocked port: {args.unblock_port}")
        elif args.list:
            stats = self.network_protection.get_network_stats()
            self.output_result(stats)
        elif args.stats:
            stats = self.network_protection.get_network_stats()
            self.output_result(stats)
        elif args.export:
            self.network_protection.export_rules(args.export)
            print(f"Rules exported to {args.export}")
        elif args.import_rules:
            self.network_protection.import_rules(args.import_rules)
            print(f"Rules imported from {args.import_rules}")
        else:
            print("Use --block-ip, --block-domain, --block-port, --list, --stats, --export, or --import-rules")
    
    def cmd_ransomware(self, args):
        """Handle ransomware command"""
        if args.stats:
            stats = self.ransomware_shield.get_protection_stats()
            self.output_result(stats)
        elif args.activities:
            activities = self.ransomware_shield.get_suspicious_activities()
            self.output_result(activities)
        elif args.restore:
            success = self.ransomware_shield.restore_file(args.restore)
            self.output_result({'restored': success, 'file': args.restore})
        elif args.add_protected:
            self.ransomware_shield.add_protected_directory(args.add_protected)
            print(f"Added protected directory: {args.add_protected}")
        elif args.remove_protected:
            self.ransomware_shield.remove_protected_directory(args.remove_protected)
            print(f"Removed protected directory: {args.remove_protected}")
        elif args.cleanup:
            self.ransomware_shield.cleanup_old_backups(args.cleanup)
            print(f"Cleaned up backups older than {args.cleanup} days")
        else:
            print("Use --stats, --activities, --restore, --add-protected, --remove-protected, or --cleanup")
    
    def cmd_restore_point(self, args):
        """Handle restore point command"""
        if args.create:
            restore_id = self.restore_point.create_restore_point("manual", args.create)
            self.output_result({'created': restore_id, 'description': args.create})
        elif args.list:
            points = self.restore_point.list_restore_points()
            self.output_result(points)
        elif args.restore:
            success = self.restore_point.restore_system(args.restore)
            self.output_result({'restored': success, 'point_id': args.restore})
        elif args.delete:
            success = self.restore_point.delete_restore_point(args.delete)
            self.output_result({'deleted': success, 'point_id': args.delete})
        elif args.stats:
            stats = self.restore_point.get_restore_point_stats()
            self.output_result(stats)
        else:
            print("Use --create, --list, --restore, --delete, or --stats")
    
    def cmd_quarantine(self, args):
        """Handle quarantine command"""
        if args.list:
            files = self.quarantine.get_quarantined_files()
            self.output_result(files)
        elif args.restore:
            success = self.quarantine.restore_file(args.restore)
            self.output_result({'restored': success, 'file': args.restore})
        elif args.delete:
            success = self.quarantine.delete_file(args.delete)
            self.output_result({'deleted': success, 'file': args.delete})
        elif args.stats:
            stats = self.quarantine.get_quarantine_stats()
            self.output_result(stats)
        else:
            print("Use --list, --restore, --delete, or --stats")
    
    def cmd_scheduler(self, args):
        """Handle scheduler command"""
        if args.add:
            name, path, time_str = args.add
            success = self.scheduler.add_scheduled_scan(name, path, time_str)
            self.output_result({'added': success, 'name': name, 'path': path, 'time': time_str})
        elif args.remove:
            success = self.scheduler.remove_scheduled_scan(args.remove)
            self.output_result({'removed': success, 'name': args.remove})
        elif args.list:
            scans = self.scheduler.get_scheduled_scans()
            self.output_result(scans)
        elif args.run:
            success = self.scheduler.run_scheduled_scan(args.run)
            self.output_result({'run': success, 'name': args.run})
        elif args.enable:
            success = self.scheduler.enable_scheduled_scan(args.enable)
            self.output_result({'enabled': success, 'name': args.enable})
        elif args.disable:
            success = self.scheduler.disable_scheduled_scan(args.disable)
            self.output_result({'disabled': success, 'name': args.disable})
        else:
            print("Use --add, --remove, --list, --run, --enable, or --disable")
    
    def cmd_system(self, args):
        """Handle system command"""
        if args.stats:
            stats = self.system_monitor.get_detailed_stats()
            self.output_result(stats)
        elif args.health:
            health = self.system_monitor.is_system_healthy()
            self.output_result({'healthy': health})
        elif args.processes:
            processes = self.system_monitor.get_process_list()
            self.output_result(processes)
        else:
            print("Use --stats, --health, or --processes")
    
    def cmd_settings(self, args):
        """Handle settings command"""
        if args.get:
            value = self.settings.get_setting(args.get)
            self.output_result({args.get: value})
        elif args.set:
            key, value = args.set
            success = self.settings.set_setting(key, value)
            self.output_result({'set': success, 'key': key, 'value': value})
        elif args.list:
            settings = self.settings.get_all_settings()
            self.output_result(settings)
        elif args.reset:
            success = self.settings.reset_to_defaults()
            self.output_result({'reset': success})
        else:
            print("Use --get, --set, --list, or --reset")
    
    def cmd_update(self, args):
        """Handle update command"""
        if args.threat_db:
            print("Updating threat database...")
            # Implementation would go here
            self.output_result({'updated': True, 'component': 'threat_database'})
        elif args.ai_models:
            print("Updating AI models...")
            # Implementation would go here
            self.output_result({'updated': True, 'component': 'ai_models'})
        elif args.all:
            print("Updating all components...")
            # Implementation would go here
            self.output_result({'updated': True, 'component': 'all'})
        else:
            print("Use --threat-db, --ai-models, or --all")
    
    def cmd_reset(self, args):
        """Handle reset command"""
        try:
            from utils.data_reset import DataResetManager
            
            data_reset_manager = DataResetManager()
            
            if args.all:
                # Reset all data
                if not args.confirm:
                    print("⚠️  WARNING: This will reset ALL IronWall data to factory defaults!")
                    print("This includes settings, scan history, quarantine, logs, and more.")
                    response = input("Are you sure you want to continue? (yes/no): ")
                    if response.lower() not in ['yes', 'y']:
                        print("Reset cancelled.")
                        return
                
                print("🔄 Starting comprehensive data reset...")
                results = data_reset_manager.reset_all_data(create_backup=not args.no_backup)
                
                # Show results
                success_count = sum(1 for success in results.values() if success)
                total_count = len(results)
                
                print(f"\n✅ Reset completed: {success_count}/{total_count} operations successful")
                
                for operation, success in results.items():
                    status = "✅" if success else "❌"
                    print(f"  {status} {operation.replace('_', ' ').title()}")
                
                # Show reset log
                print("\n📋 Reset Log:")
                for log_entry in data_reset_manager.get_reset_log():
                    print(f"  {log_entry}")
                
            elif args.settings:
                # Reset only settings
                print("🔄 Resetting settings to defaults...")
                if data_reset_manager.reset_settings():
                    print("✅ Settings reset successfully")
                else:
                    print("❌ Settings reset failed")
                    
            elif args.quarantine:
                # Reset only quarantine
                print("🔄 Clearing quarantine...")
                if data_reset_manager.reset_quarantine():
                    print("✅ Quarantine cleared successfully")
                else:
                    print("❌ Quarantine reset failed")
                    
            elif args.logs:
                # Reset only logs
                print("🔄 Clearing logs...")
                if data_reset_manager.reset_scan_history() and data_reset_manager.reset_system_logs():
                    print("✅ Logs cleared successfully")
                else:
                    print("❌ Logs reset failed")
                    
            else:
                print("Please specify what to reset:")
                print("  --all       Reset all data to factory defaults")
                print("  --settings  Reset only settings")
                print("  --quarantine Reset only quarantine")
                print("  --logs      Reset only logs")
                
        except Exception as e:
            print(f"❌ Reset failed: {e}")
            if self.verbose:
                import traceback
                traceback.print_exc()
    
    def cmd_diagnostic(self, args):
        """Handle diagnostic command"""
        if args.generate:
            report = self._generate_diagnostic_report()
            
            if args.output:
                with open(args.output, 'w') as f:
                    json.dump(report, f, indent=2, default=str)
                print(f"Diagnostic report saved to {args.output}")
            else:
                self.output_result(report)
        else:
            print("Use --generate")
    
    def _generate_diagnostic_report(self) -> Dict[str, Any]:
        """Generate comprehensive diagnostic report"""
        report = {
            'timestamp': datetime.now().isoformat(),
            'system_info': self.system_monitor.get_system_info(),
            'components': {
                'scanner': self.scanner.get_scan_stats(),
                'ai_engine': self.ai_engine.get_model_info(),
                'process_monitor': self.process_monitor.get_process_stats(),
                'cloud_intelligence': self.cloud_intel.get_cache_stats(),
                'network_protection': self.network_protection.get_network_stats(),
                'ransomware_shield': self.ransomware_shield.get_protection_stats(),
                'restore_point': self.restore_point.get_restore_point_stats(),
                'quarantine': self.quarantine.get_quarantine_stats(),
                'scheduler': self.scheduler.get_scheduler_stats(),
                'system_monitor': self.system_monitor.get_detailed_stats()
            },
            'settings': self.settings.get_all_settings(),
            'threat_database': {
                'total_threats': len(self.threat_db.get_all_threats()),
                'last_updated': self.threat_db.get_last_update()
            }
        }
        
        return report

def main():
    """Main entry point for CLI"""
    cli = IronWallCLI()
    cli.run()

if __name__ == "__main__":
    main() 