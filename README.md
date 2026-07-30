# Universal Report Analyzer - PySide6 Desktop Application

A professional desktop application for analyzing and generating HTML reports from various test formats. Built with PySide6 for Ubuntu Linux.

## Features

✓ **Multiple Report Formats**
- XML Reports (JUnit format)
- JSON Reports
- HTML Reports
- TXT/LOG Reports
- TradeFed Event Logs
- TradeFed Host Logs
- TradeFed Java Logs
- TradeFed Passed Tests Reports

✓ **Modern Desktop UI**
- Clean, intuitive interface
- Drag & Drop file selection
- File browsing dialog
- Real-time status updates
- Progress indication
- Summary statistics panel

✓ **Intelligent Report Detection**
- Automatic report type detection
- Smart parser selection
- Multi-format support

✓ **HTML Report Generation**
- Professional report formatting
- Color-coded test status
- Summary statistics
- Auto-open in default browser

✓ **Cross-Platform**
- Ubuntu 22.04+
- Ubuntu 24.04+
- Wayland support
- X11 support

## Installation

### Prerequisites

- Python 3.8+
- Ubuntu 22.04 or later

### Setup

```bash
# Clone or navigate to project directory
git clone https://github.com/abdulsanad27/Universal-report-generator.git

cd Universal-report-generator

# Create virtual environment (if not present)
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

## Usage

### Starting the Application

```bash
# Activate virtual environment
source venv/bin/activate

# Run the application
python3 python3 universal_report_analyzer.py
```

### Basic Workflow

1. **Open Application**
   - Launch the application using the command above
   - Window will appear with file selection area

2. **Select Report Files**
   - Option A: Drag & Drop files onto the window
   - Option B: Click "Browse Files" button
   - Select one 
   - Files will appear in the "Selected Files" list

3. **Generate Report**
   - Click "Generate HTML Report" button
   - Progress bar shows generation status
   - Status updates display real-time information

4. **View Report**
   - Generated HTML report opens automatically
   - Summary statistics displayed in the application
   - Report saved to `reports/` folder

5. **Manage Files**
   - **Remove Selected**: Remove highlighted file from list
   - **Clear All**: Remove all files from list

## Project Structure

```
UVSL_report_gen/
├── main.py                 # Application entry point
├── config.py              # Configuration
├── gui/                   # GUI components (NEW)
│   ├── __init__.py
│   └── main_window.py     # Main window implementation
├── detector/              # Report type detection (existing)
├── models/                # Data models (existing)
├── parsers/               # Report parsers (existing)
├── services/              # Service layer (existing)
├── templates/             # HTML templates (existing)
├── static/                # Static assets (existing)
├── reports/               # Generated reports (output)
├── uploads/               # File upload area
├── test_reports/          # Sample test files
├── venv/                  # Virtual environment
└── requirements.txt       # Python dependencies
```

## Architecture

### Core Components

**MainWindow** (gui/main_window.py)
- Main application window
- Handles user interactions
- Manages file list
- Coordinates report generation

**ReportGenerationWorker** (gui/main_window.py)
- Background thread for report generation
- Prevents UI blocking
- Provides progress updates
- Generates summary statistics

### Backend Integration

The desktop application preserves the entire backend architecture:

```
PySide6 GUI
    ↓
detector.detect_file_type()      [Detects report type]
    ↓
ParserFactory.get_parser()       [Gets appropriate parser]
    ↓
Parser.parse()                   [Parses report]
    ↓
Report Model                     [Universal data model]
    ↓
HTML Report Generation           [Generates HTML]
    ↓
Browser Display                  [Opens in default browser]
```

## Configuration

Configuration is centralized in `config.py`:

- `UPLOAD_FOLDER`: Directory for uploads
- `MAX_CONTENT_LENGTH`: Maximum file size (20 MB)
- `ALLOWED_EXTENSIONS`: Supported file types
- `STATUS_COLORS`: Color scheme for report status
- `VERSION`: Application version

## Creating Test Reports

### Sample XML Report

Create `test_reports/sample.xml`:
```xml
<?xml version="1.0" encoding="UTF-8"?>
<testsuite name="My Test Suite" tests="5" failures="1" skipped="1">
    <testcase classname="com.example.Tests" name="testPass" time="0.5"/>
    <testcase classname="com.example.Tests" name="testFail" time="0.3">
        <failure message="Test failed">Assertion error details</failure>
    </testcase>
</testsuite>
```

### Sample JSON Report

Create `test_reports/sample.json`:
```json
{
  "testSuite": "My Test Suite",
  "tests": 5,
  "passed": 4,
  "failed": 1,
  "testCases": [...]
}
```

## Error Handling

The application includes comprehensive error handling:

- **No Files Selected**: Shows warning dialog
- **Unsupported Format**: Displays error message
- **Parse Errors**: Catches exceptions and displays details
- **File Access Issues**: Handles permission/read errors
- **HTML Generation Errors**: Falls back to minimal template

## Development

### Running Tests

```bash
source venv/bin/activate
python3 test_integration.py  # Run integration tests
```

### Adding New Parsers

1. Create parser in `parsers/my_parser.py`
2. Inherit from `BaseParser`
3. Implement `parse()` method
4. Register in `ParserFactory`
5. Update detector signatures
6. No GUI changes needed

### Threading Considerations

- Report generation runs in background thread
- UI remains responsive
- Progress signals update main window
- Worker thread completes independently

## Deployment

### Creating Standalone Binary

```bash
# Install PyInstaller
pip install pyinstaller

# Create standalone executable
pyinstaller --onefile \
    --windowed \
    --name "UniversalReportAnalyzer" \
    --icon icon.png \
    main.py
```

### Creating AppImage

```bash
# Build AppImage (Linux)
./build_appimage.sh
```

### Creating .deb Package

```bash
# Build deb package
./build_deb.sh
```

## Troubleshooting

### Application Won't Start

```bash
# Check Python version
python3 --version

# Verify virtual environment
source venv/bin/activate
which python3

# Check PySide6 installation
python3 -c "from PySide6.QtWidgets import QApplication; print('OK')"
```

### No Display (Headless)

```bash
# Set QT platform
export QT_QPA_PLATFORM=offscreen
python3 main.py
```

### File Not Detected

1. Check file format matches expected structure
2. Verify file extension
3. Check file permissions (readable)
4. Test with sample files in `test_reports/`



**Version**: 2.0  
**Last Updated**: 2026-07-08  
**Target Platform**: Ubuntu Linux
