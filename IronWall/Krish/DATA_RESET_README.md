# IronWall Antivirus - Data Reset Feature

## Overview

The Data Reset feature provides comprehensive functionality to reset all IronWall Antivirus data to factory defaults. This feature is useful for troubleshooting, privacy protection, or starting fresh with the application.

## Features

### 🔄 Comprehensive Data Reset
- **Settings Reset**: All application settings restored to factory defaults
- **Scan History Clear**: Complete scan history and results cleared
- **Quarantine Reset**: All quarantined files and quarantine database cleared
- **Threat Database Reset**: Threat signatures and hashes cleared
- **System Logs Clear**: All system logs and diagnostic data cleared
- **Scheduled Scans Reset**: All scheduled scan configurations removed
- **Network Rules Reset**: Network protection rules restored to defaults
- **Backup Data Clear**: All backup directories and files cleared
- **Restore Points Clear**: System restore points cleared
- **Diagnostic Files Clear**: All diagnostic report files removed

### 📦 Automatic Backup
- Creates timestamped backup before reset operations
- Backup includes all data files and directories
- Backup stored in `reset_backups/` directory
- Backup can be restored if needed

### 🛡️ Safety Features
- Confirmation dialogs for destructive operations
- Detailed logging of all reset operations
- Progress tracking during reset process
- Error handling and recovery

## Usage

### GUI Interface

1. **Open Settings Panel**:
   - Launch IronWall Antivirus
   - Navigate to Settings → Advanced tab
   - Click "🔄 Reset All Data" button

2. **Reset Dialog**:
   - Review the warning message
   - Choose backup options
   - Confirm the reset operation
   - Monitor progress and results

### Command Line Interface

```bash
# Reset all data to factory defaults
python cli.py reset --all

# Reset all data without confirmation prompt
python cli.py reset --all --confirm

# Reset all data without creating backup
python cli.py reset --all --no-backup

# Reset only settings
python cli.py reset --settings

# Reset only quarantine
python cli.py reset --quarantine

# Reset only logs
python cli.py reset --logs
```

### Programmatic Usage

```python
from utils.data_reset import DataResetManager

# Create reset manager
data_reset_manager = DataResetManager()

# Reset all data with backup
results = data_reset_manager.reset_all_data(create_backup=True)

# Reset individual components
data_reset_manager.reset_settings()
data_reset_manager.reset_quarantine()
data_reset_manager.reset_scan_history()

# Get reset log
log_entries = data_reset_manager.get_reset_log()
```

## Data Files Affected

### Configuration Files
- `ironwall_settings.json` - Application settings
- `threat_database.json` - Threat signatures and hashes
- `scan_history.json` - Scan results and history
- `system_logs.json` - System event logs
- `scheduled_scans.json` - Scheduled scan configurations
- `network_rules.json` - Network protection rules

### Directories
- `quarantine/` - Quarantined files and database
- `backups/` - Backup data and restore points
- `restore_points/` - System restore point data

### Diagnostic Files
- `ironwall_diagnostic_*.json` - Diagnostic reports

## Backup and Restore

### Automatic Backup
- Created before reset operations (if enabled)
- Stored in `reset_backups/pre_reset_backup_YYYYMMDD_HHMMSS/`
- Includes all data files and directories
- Timestamped for easy identification

### Manual Restore
```python
from utils.data_reset import DataResetManager

data_reset_manager = DataResetManager()
data_reset_manager.restore_from_backup("path/to/backup/directory")
```

## Safety Considerations

### ⚠️ Important Warnings
- **Data Loss**: Reset operations permanently delete data
- **No Recovery**: Deleted data cannot be recovered without backup
- **Application Restart**: Some changes require application restart
- **Settings Impact**: All customizations will be lost

### 🔒 Privacy Protection
- All user data is completely removed
- Scan history and logs are cleared
- Quarantined files are deleted
- No traces of previous activity remain

## Error Handling

### Common Issues
- **Permission Errors**: Ensure write access to data directories
- **File Locked**: Close application before reset
- **Backup Failure**: Check disk space and permissions
- **Partial Reset**: Some operations may fail, check logs

### Troubleshooting
1. Check reset log for specific error messages
2. Ensure application is not running during reset
3. Verify sufficient disk space for backup
4. Check file permissions on data directories

## Testing

### Test Script
Run the included test script to verify functionality:

```bash
python test_data_reset.py
```

### Test Coverage
- Individual reset operations
- Comprehensive reset functionality
- Backup creation and restore
- Error handling scenarios
- Log generation and retrieval

## Integration

### Settings Panel Integration
- Added to Advanced tab in settings
- Consistent with existing UI design
- Proper error handling and user feedback

### CLI Integration
- New `reset` command with multiple options
- Consistent with existing CLI structure
- Detailed output and progress reporting

### API Integration
- Clean, documented API for programmatic use
- Thread-safe operations
- Comprehensive error handling

## Future Enhancements

### Planned Features
- **Selective Reset**: Choose specific data types to reset
- **Scheduled Reset**: Automatically reset data on schedule
- **Reset Templates**: Predefined reset configurations
- **Cloud Backup**: Backup to cloud storage
- **Reset History**: Track reset operations over time

### Configuration Options
- **Auto-backup**: Always create backup before reset
- **Reset confirmation**: Require confirmation for all resets
- **Log retention**: Keep reset logs for specified period
- **Notification settings**: Configure reset notifications

## Support

### Documentation
- This README file
- Inline code documentation
- API documentation in docstrings

### Troubleshooting
- Check reset logs for detailed error information
- Verify file permissions and disk space
- Test with included test script
- Review error messages for specific issues

---

**Note**: This feature is designed for advanced users and system administrators. Use with caution as it permanently deletes data. 