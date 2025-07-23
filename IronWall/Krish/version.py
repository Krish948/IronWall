"""
IronWall Antivirus - Version Configuration
Centralized version information for the application
"""

# Application Version Information
APP_VERSION = "3.2.1"
APP_BUILD = "2024.1.15.1234"
APP_RELEASE_DATE = "January 15, 2024"
APP_NAME = "IronWall Antivirus"
APP_DESCRIPTION = "Professional antivirus solution with modular architecture"

# Supported Platforms
SUPPORTED_OS = "Windows 10/11 (64-bit)"
MIN_PYTHON_VERSION = "3.8"

def get_version_info():
    """Get complete version information dictionary"""
    return {
        "app_version": APP_VERSION,
        "app_build": APP_BUILD,
        "app_release_date": APP_RELEASE_DATE,
        "app_name": APP_NAME,
        "app_description": APP_DESCRIPTION,
        "supported_os": SUPPORTED_OS
    } 