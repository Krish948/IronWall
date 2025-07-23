# IronWall Project

---

## Table of Contents
1. [IronWall Antivirus - Main README](#ironwall-antivirus---main-readme)
2. [Data Reset Feature](#data-reset-feature)
3. [Test Files Merge Summary](#test-files-merge-summary)

---

## IronWall Antivirus - Main README

# 🛡️ IronWall Antivirus - Professional Security Suite

A modular antivirus solution for Windows with real-time threat detection and multiple scan types.

## 🌟 Key Features

### 🔐 Core Security
- Real-time threat detection
- Multiple scan types: Quick, Full, and Custom scans
- Heuristic + signature-based scanning
- Quarantine management
- Scan logs and threat history

### ⚙️ System Tools & Utilities
- Scheduled scans
- Drag & drop file scanning support

### 💻 UI/UX
- Modern design
- System tray integration

### 🚀 Performance & Deployment
- Lightweight background operation
- Modular architecture for easy maintenance
- Windows compatibility

## 📋 Requirements

### System Requirements
- OS: Windows 10/11 (64-bit)
- RAM: 4GB minimum
- Storage: 2GB free space
- Python: 3.8 or higher

### Python Dependencies
```bash
pip install -r requirements.txt
```

## 🚀 Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/yourusername/IronWall.git
   cd IronWall/Krish
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application**:
   ```bash
   python main.py
   ```

## 🔧 Configuration

The application uses `ironwall_settings.json` for configuration. Example:
```json
{
  "protection": {
    "real_time_protection": true,
    "heuristic_scanning": "Medium"
  },
  "scanning": {
    "default_scan_type": "Quick"
  }
}
```

## 🎯 Usage

### Basic Scanning
1. **Quick Scan**: Fast scan of critical system areas
2. **Full Scan**: Comprehensive system-wide scan
3. **Custom Scan**: User-selected files and folders

### System Tray
- Right-click tray icon for quick access
- Real-time status indicators
- Quick scan options
- Notification management

## 🏗️ Architecture

### Core Modules
- Scanner: File and system scanning engine
- Process Monitor: Real-time process monitoring
- Network Protection: Firewall and network security
- System Tray: System integration and notifications

### UI Components
- Main Window: Primary application interface
- Dashboard: Real-time system status
- Scan Panel: File scanning interface
- Quarantine Panel: Threat management
- Settings Panel: Configuration management

## 🔒 Security Features

### Threat Detection
- Signature-based detection
- Heuristic analysis
- Behavioral monitoring

### Protection Mechanisms
- Real-time protection
- Network filtering
- File quarantine

## 📊 Monitoring & Reporting

### Real-time Monitoring
- System performance: CPU, memory, disk usage
- Network activity: Connection monitoring
- Threat detection: Real-time alerts and notifications

### Reports & Analytics
- Scan reports: Detailed scan results
- Threat analysis: Malware classification and details
- Activity logs: System activity tracking

## 🛠️ Development

### Project Structure
```
IronWall/
├── Krish/
│   ├── core/                 # Core security modules
│   ├── ui/                   # User interface components
│   ├── utils/                # Utility functions
│   ├── main.py               # Application entry point
│   └── requirements.txt      # Python dependencies
├── quarantine/               # Quarantined files
└── logs/                     # Application logs
```

## 🤝 Support

- Issues: [GitHub Issues](https://github.com/krish948/IronWall/issues)

## ⚠️ Disclaimer

This software is provided for educational and research purposes. Use at your own risk. The developers are not responsible for any damage or data loss that may occur from using this software.

## 🔄 Version History

### v2.0.0 (Current)
- ✨ Added Behavior Analyzer module
- ✨ Added Vulnerability Scanner
- ✨ Added Parental Controls
- ✨ Added Anti-Keylogger protection
- ✨ Added Dark Web Monitor
- ✨ Added System Tray integration
- ✨ Enhanced UI with modern themes
- ✨ Improved threat detection algorithms
- ✨ Added cloud threat intelligence
- ✨ Enhanced network protection

### v1.0.0
- 🎉 Initial release
- Basic antivirus functionality
- File scanning capabilities
- Quarantine management
- Simple UI interface

---

**IronWall Antivirus** - Protecting your digital world with advanced security technology.
