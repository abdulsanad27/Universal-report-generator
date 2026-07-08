# Universal Report Analyzer - Quick Start Guide

## For First-Time Users

### 1. Installation (One-Time Setup)

```bash
# Open terminal
# Navigate to project folder
cd ~/Desktop/UVSL_report_gen

# Create virtual environment (if needed)
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Running the Application

**Option A: Using the startup script (Recommended)**
```bash
./run.sh
```

**Option B: Manual startup**
```bash
source venv/bin/activate
python3 main.py
```

### 3. Basic Usage

1. **Start the Application**
   - Click "Browse Files" or drag files onto the window

2. **Select Report Files**
   - Choose any of these formats:
     - XML files (.xml)
     - JSON files (.json)
     - Text files (.txt)
     - Log files (.log)
     - HTML files (.html)

3. **Generate Report**
   - Click "Generate HTML Report"
   - Wait for processing (progress bar shown)
   - Report automatically opens in browser

4. **View Results**
   - HTML report shows:
     - Report type detected
     - Total tests, passed, failed, skipped counts
     - Generation time
   - Summary panel displays statistics

## Supported Report Formats

| Format | Extension | Auto-Detected | Example |
|--------|-----------|---------------|---------|
| XML (JUnit) | .xml | ✓ Yes | JUnit test results |
| JSON | .json | ✓ Yes | Custom JSON reports |
| HTML | .html/.htm | ✓ Yes | Pre-generated HTML |
| TXT | .txt | ✓ Yes | Text-based reports |
| LOG | .log | ✓ Yes | Log files |
| TradeFed Event | .log | ✓ Yes | Android testing logs |
| TradeFed Host | .log | ✓ Yes | TradeFed host logs |
| TradeFed Java | .log | ✓ Yes | Java execution logs |
| TradeFed Passed | .log | ✓ Yes | Passed tests list |

## Tips & Tricks

### Tip 1: Drag & Drop
Simply drag report files directly onto the window - no need to use Browse button.

### Tip 2: Multiple Files
Select multiple files at once:
- In file browser: `Ctrl+Click` to select multiple files
- In file list: Right-click to remove individual files

### Tip 3: Batch Processing
Generate reports from different folders:
1. Clear list with "Clear All"
2. Select files from different locations
3. Click "Generate HTML Report"

### Tip 4: View Generated Reports
- Reports saved in `reports/` folder
- Each report has timestamp in filename
- Open any report directly in browser

### Tip 5: Test the App
Try included sample files:
```bash
# These work out-of-the-box:
test_reports/sample_test.xml
test_reports/sample_test.json
```

## Troubleshooting

### Issue: "ModuleNotFoundError: No module named 'PySide6'"

**Solution:**
```bash
# Make sure virtual environment is activated
source venv/bin/activate

# Reinstall dependencies
pip install --force-reinstall PySide6 Jinja2
```

### Issue: Application won't start

**Solution:**
```bash
# Check Python version (need 3.8+)
python3 --version

# Try running with explicit Python path
/usr/bin/python3 main.py
```

### Issue: File not detected correctly

**Solution:**
1. Check file extension matches format (.xml, .json, etc.)
2. Ensure file is readable
3. Try with sample files in `test_reports/`

### Issue: Report didn't open in browser

**Solution:**
- Report is still saved in `reports/` folder
- Manually open it from file manager
- Try clicking the summary path

## File Structure

```
UVSL_report_gen/
├── main.py                    # Start the app
├── run.sh                     # Convenient startup
├── config.py                  # Configuration
├── requirements.txt           # Dependencies
├── gui/
│   ├── __init__.py
│   └── main_window.py        # GUI implementation
├── detector/                  # Report type detection
├── parsers/                   # Report parsers
├── models/                    # Data structures
├── services/                  # Service layer
├── reports/                   # Generated reports (output)
├── test_reports/              # Sample test files
│   ├── sample_test.xml
│   └── sample_test.json
└── venv/                      # Virtual environment
```

## Getting Help

### View Application Help
1. Window title shows version
2. Status bar shows current state
3. Error dialogs explain issues

### Check Test Files
- Look in `test_reports/` folder
- Try generating report from samples
- Verify workflow works

### View Documentation
- `README.md` - Full documentation
- `test_integration.py` - All features with tests
- `config.py` - Configuration options

## Common Workflows

### Workflow 1: Single Report
1. Open app
2. Click "Browse Files"
3. Select 1 XML file
4. Click "Generate HTML Report"
5. View result

### Workflow 2: Batch Processing
1. Open app
2. Drag 5 XML files onto window
3. Select first file only
4. Click "Generate HTML Report"
5. Repeat for other files (or select each)

### Workflow 3: Compare Formats
1. Open app
2. Add XML report
3. Generate and compare
4. Clear all, add JSON report
5. Generate and compare

### Workflow 4: Automated Testing
```bash
# Run tests
source venv/bin/activate
python3 test_integration.py
```

## Next Steps

### For End Users
- Use daily for report generation
- Check `reports/` folder for outputs
- Share HTML reports with team

### For Developers
- Add custom parsers in `parsers/`
- Extend GUI in `gui/main_window.py`
- Add tests in `test_integration.py`
- See `README.md` for architecture

## System Requirements

- **OS**: Ubuntu 22.04 or newer
- **Python**: 3.8 or newer
- **RAM**: 512 MB minimum
- **Disk**: 100 MB for app + reports

## Performance

- **Small files** (< 1 MB): < 1 second
- **Medium files** (1-5 MB): 1-3 seconds
- **Large files** (5-20 MB): 3-10 seconds

---

**Ready to start?** Run `./run.sh` and enjoy generating beautiful test reports! 🚀
