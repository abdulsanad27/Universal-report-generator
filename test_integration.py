"""
Integration tests for Universal Report Analyzer.

Run with: source venv/bin/activate && python3 test_integration.py
"""

import sys
import os
import tempfile
from pathlib import Path

# Set headless mode for testing
os.environ['QT_QPA_PLATFORM'] = 'offscreen'

from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt

from gui.main_window import MainWindow, ReportGenerationWorker
from detector.file_detector import detect_file_type
from parsers.parser_factory import ParserFactory


class TestRunner:
    """Test runner for integration tests."""
    
    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.errors = []
    
    def run_test(self, test_name, test_func):
        """Run a single test."""
        try:
            print(f"Running: {test_name}...", end=" ")
            test_func()
            print("✓ PASSED")
            self.passed += 1
        except AssertionError as e:
            print(f"✗ FAILED: {e}")
            self.failed += 1
            self.errors.append((test_name, str(e)))
        except Exception as e:
            print(f"✗ ERROR: {e}")
            self.failed += 1
            self.errors.append((test_name, f"Unexpected error: {e}"))
    
    def print_summary(self):
        """Print test summary."""
        total = self.passed + self.failed
        print(f"\n{'='*60}")
        print(f"Test Summary: {self.passed}/{total} passed")
        print(f"{'='*60}")
        
        if self.errors:
            print("\nFailed Tests:")
            for test_name, error in self.errors:
                print(f"  - {test_name}: {error}")
        
        return self.failed == 0


# Initialize QApplication for testing
app = QApplication.instance() or QApplication([])
runner = TestRunner()


# =====================================================================
# DETECTOR TESTS
# =====================================================================

def test_xml_detection():
    """Test XML file detection."""
    xml_content = b'<?xml version="1.0"?><testsuite></testsuite>'
    result = detect_file_type("test.xml", xml_content)
    assert result == "xml", f"Expected 'xml', got '{result}'"


def test_json_detection():
    """Test JSON file detection."""
    json_content = b'{"testSuite": "test"}'
    result = detect_file_type("test.json", json_content)
    assert result == "json", f"Expected 'json', got '{result}'"


def test_html_detection():
    """Test HTML file detection."""
    html_content = b'<!DOCTYPE html><html></html>'
    result = detect_file_type("test.html", html_content)
    assert result == "html", f"Expected 'html', got '{result}'"


def test_txt_detection():
    """Test TXT file detection."""
    txt_content = b'PASS FAIL SKIP'
    result = detect_file_type("test.txt", txt_content)
    assert result in ["generic_txt", "tradefed_host"], f"Unexpected result: '{result}'"


# =====================================================================
# PARSER TESTS
# =====================================================================

def test_xml_parser():
    """Test XML parser."""
    xml_path = "test_reports/sample_test.xml"
    assert os.path.exists(xml_path), f"Test file not found: {xml_path}"
    
    with open(xml_path, 'rb') as f:
        content = f.read()
    
    parser = ParserFactory.get_parser("xml")
    report = parser.parse(content)
    
    assert report is not None, "Parser returned None"
    assert report.total > 0, f"Expected total > 0, got {report.total}"


def test_json_parser():
    """Test JSON parser."""
    json_path = "test_reports/sample_test.json"
    assert os.path.exists(json_path), f"Test file not found: {json_path}"
    
    with open(json_path, 'rb') as f:
        content = f.read()
    
    parser = ParserFactory.get_parser("json")
    report = parser.parse(content)
    
    assert report is not None, "Parser returned None"


def test_unsupported_parser():
    """Test that unsupported parser raises exception."""
    try:
        ParserFactory.get_parser("unsupported_format")
        assert False, "Should have raised exception for unsupported parser"
    except Exception as e:
        assert "No parser found" in str(e), f"Unexpected error: {e}"


# =====================================================================
# REPORT GENERATION TESTS
# =====================================================================

def test_report_generation_workflow():
    """Test complete report generation workflow."""
    xml_path = "test_reports/sample_test.xml"
    assert os.path.exists(xml_path), f"Test file not found: {xml_path}"
    
    worker = ReportGenerationWorker([xml_path])
    
    # Track results
    results = []
    def track_result(success, message, summary):
        results.append((success, message, summary))
    
    worker.finished.connect(track_result)
    worker.run()
    
    assert len(results) > 0, "No results from worker"
    success, message, summary = results[0]
    
    assert success is True, f"Generation failed: {message}"
    assert summary['detected_type'] == 'XML', f"Wrong type: {summary['detected_type']}"
    assert summary['output_file'] is not None, "No output file"
    assert os.path.exists(summary['output_file']), "Output file doesn't exist"


def test_report_summary_data():
    """Test that report summary contains correct statistics."""
    xml_path = "test_reports/sample_test.xml"
    
    worker = ReportGenerationWorker([xml_path])
    
    results = []
    def track_result(success, message, summary):
        results.append((success, message, summary))
    
    worker.finished.connect(track_result)
    worker.run()
    
    success, message, summary = results[0]
    
    assert summary['file_count'] == 1, f"Expected 1 file, got {summary['file_count']}"
    assert summary['total_tests'] > 0, f"Expected tests > 0, got {summary['total_tests']}"
    assert summary['generation_time'] > 0, f"Expected generation time > 0, got {summary['generation_time']}"


def test_html_report_file():
    """Test that generated HTML report is valid."""
    xml_path = "test_reports/sample_test.xml"
    
    worker = ReportGenerationWorker([xml_path])
    
    results = []
    def track_result(success, message, summary):
        results.append((success, message, summary))
    
    worker.finished.connect(track_result)
    worker.run()
    
    success, message, summary = results[0]
    output_file = summary['output_file']
    
    assert os.path.exists(output_file), f"Output file not found: {output_file}"
    
    with open(output_file, 'r', encoding='utf-8') as f:
        html_content = f.read()
    
    assert '<!DOCTYPE html>' in html_content, "Invalid HTML: missing DOCTYPE"
    assert '<title>' in html_content, "Invalid HTML: missing title"
    assert 'Test Report' in html_content, "Invalid HTML: missing report title"


# =====================================================================
# GUI TESTS
# =====================================================================

def test_main_window_creation():
    """Test MainWindow creation."""
    window = MainWindow()
    assert window is not None, "Failed to create MainWindow"
    assert window.windowTitle() == "Universal Report Analyzer", f"Wrong title: {window.windowTitle()}"
    assert window.width() == 900, f"Wrong width: {window.width()}"
    assert window.height() == 650, f"Wrong height: {window.height()}"


def test_main_window_widgets():
    """Test MainWindow has all required widgets."""
    window = MainWindow()
    
    required_widgets = [
        'browse_button',
        'generate_button',
        'remove_button',
        'clear_button',
        'exit_button',
        'file_list_widget',
        'progress_bar',
        'status_label',
        'summary_frame',
        'summary_text',
        'drop_label'
    ]
    
    for widget_name in required_widgets:
        assert hasattr(window, widget_name), f"Missing widget: {widget_name}"


def test_file_list_management():
    """Test file list add/remove functionality."""
    window = MainWindow()
    
    # Test add file
    test_file = "test_reports/sample_test.xml"
    window._add_file(test_file)
    assert len(window.file_list) == 1, "File not added to list"
    assert window.file_list_widget.count() == 1, "File not added to widget"
    
    # Test add duplicate (should not duplicate)
    window._add_file(test_file)
    assert len(window.file_list) == 1, "Duplicate file was added"
    
    # Test add different file
    test_file2 = "test_reports/sample_test.json"
    window._add_file(test_file2)
    assert len(window.file_list) == 2, "Second file not added"
    assert window.file_list_widget.count() == 2, "Second file not added to widget"


def test_file_list_clear():
    """Test clearing file list."""
    window = MainWindow()
    window._add_file("test_reports/sample_test.xml")
    window._add_file("test_reports/sample_test.json")
    
    assert len(window.file_list) == 2, "Files not added"
    
    window._on_clear_clicked()
    
    assert len(window.file_list) == 0, "Files not cleared"
    assert window.file_list_widget.count() == 0, "Widget not cleared"


def test_file_list_remove():
    """Test removing selected file."""
    window = MainWindow()
    file1 = "test_reports/sample_test.xml"
    file2 = "test_reports/sample_test.json"
    
    window._add_file(file1)
    window._add_file(file2)
    
    assert len(window.file_list) == 2, "Files not added"
    
    # Select first item and remove
    window.file_list_widget.setCurrentRow(0)
    window._on_remove_clicked()
    
    assert len(window.file_list) == 1, "File not removed"
    assert window.file_list[0] == file2, "Wrong file was removed"


# =====================================================================
# RUN ALL TESTS
# =====================================================================

if __name__ == "__main__":
    print("="*60)
    print("Universal Report Analyzer - Integration Tests")
    print("="*60)
    print()
    
    # Detector tests
    print("DETECTOR TESTS")
    print("-"*60)
    runner.run_test("XML detection", test_xml_detection)
    runner.run_test("JSON detection", test_json_detection)
    runner.run_test("HTML detection", test_html_detection)
    runner.run_test("TXT detection", test_txt_detection)
    print()
    
    # Parser tests
    print("PARSER TESTS")
    print("-"*60)
    runner.run_test("XML parser", test_xml_parser)
    runner.run_test("JSON parser", test_json_parser)
    runner.run_test("Unsupported parser", test_unsupported_parser)
    print()
    
    # Report generation tests
    print("REPORT GENERATION TESTS")
    print("-"*60)
    runner.run_test("Report generation workflow", test_report_generation_workflow)
    runner.run_test("Report summary data", test_report_summary_data)
    runner.run_test("HTML report file", test_html_report_file)
    print()
    
    # GUI tests
    print("GUI TESTS")
    print("-"*60)
    runner.run_test("MainWindow creation", test_main_window_creation)
    runner.run_test("MainWindow widgets", test_main_window_widgets)
    runner.run_test("File list management", test_file_list_management)
    runner.run_test("File list clear", test_file_list_clear)
    runner.run_test("File list remove", test_file_list_remove)
    print()
    
    # Print summary
    success = runner.print_summary()
    
    sys.exit(0 if success else 1)
