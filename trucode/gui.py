import os
import sys
import threading

from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                            QHBoxLayout, QLabel, QLineEdit, QPushButton, 
                            QTextEdit, QProgressBar, QCheckBox, QFileDialog, 
                            QGroupBox, QMessageBox, QStatusBar, QSplitter)
from PyQt6.QtCore import Qt, pyqtSignal, pyqtSlot, QThread
from PyQt6.QtGui import QFont, QTextCursor, QColor, QTextCharFormat

# Import using relative imports
from .analyzer.parser import CodeParser
from .analyzer.detector import IssueDetector
from .analyzer.suggester import CodeSuggester


class AnalysisWorker(QThread):
    """Worker thread for running the analysis without blocking the UI"""
    update_signal = pyqtSignal(str)
    finished_signal = pyqtSignal(dict)
    error_signal = pyqtSignal(str)
    
    def __init__(self, file_path, options):
        super().__init__()
        self.file_path = file_path
        self.options = options
    
    def run(self):
        try:
            # Parse the code
            self.update_signal.emit(f"Analyzing {self.file_path}...")
            code_parser = CodeParser()
            parsed_code = code_parser.parse(self.file_path)
            
            if not parsed_code:
                self.error_signal.emit(f"Error: Could not parse {self.file_path}")
                return
            
            # Check if there are syntax errors
            if parsed_code.get('has_syntax_errors', False) and not self.options['force']:
                self.finished_signal.emit({
                    'type': 'basic',
                    'parsed_code': parsed_code,
                    'verbose': self.options['verbose']
                })
                return
            
            # Detect issues
            self.update_signal.emit("Detecting code issues...")
            detector = IssueDetector()
            issues = detector.detect_issues(parsed_code)
            
            # Generate suggestions
            self.update_signal.emit("Generating improvement suggestions...")
            suggester = CodeSuggester()
            
            # Disable AI if requested
            if self.options['no_ai']:
                suggester.model_wrapper.load_model = lambda: False
            
            suggestions = suggester.generate_suggestions(parsed_code, issues)
            
            # Send results back to main thread
            self.finished_signal.emit({
                'type': 'full',
                'file_path': self.file_path,
                'parsed_code': parsed_code,
                'issues': issues,
                'suggestions': suggestions,
                'verbose': self.options['verbose']
            })
            
        except Exception as e:
            self.error_signal.emit(f"Error during analysis: {str(e)}")


class TruCodeApp(QMainWindow):
    def __init__(self):
        super().__init__()
        
        # Setup window properties
        self.setWindowTitle("TruCode - Python Code Analyzer")
        self.setMinimumSize(900, 700)
        
        # Create central widget and main layout
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QVBoxLayout(self.central_widget)
        
        # Create UI elements
        self.setup_file_section()
        self.setup_options_section()
        self.setup_results_section()
        self.setup_status_bar()
        
        # Initialize worker thread
        self.analysis_thread = None
    
    def setup_file_section(self):
        file_group = QGroupBox("Select Python File")
        file_layout = QHBoxLayout()
        
        self.file_path_input = QLineEdit()
        self.file_path_input.setPlaceholderText("Path to Python file...")
        browse_button = QPushButton("Browse...")
        browse_button.clicked.connect(self.browse_file)
        analyze_button = QPushButton("Analyze Code")
        analyze_button.clicked.connect(self.analyze_code)
        analyze_button.setStyleSheet("QPushButton { background-color: #4CAF50; color: white; font-weight: bold; }")
        
        file_layout.addWidget(self.file_path_input)
        file_layout.addWidget(browse_button)
        file_layout.addWidget(analyze_button)
        
        file_group.setLayout(file_layout)
        self.main_layout.addWidget(file_group)
    
    def setup_options_section(self):
        options_group = QGroupBox("Options")
        options_layout = QHBoxLayout()
        
        self.verbose_check = QCheckBox("Verbose Output")
        self.no_ai_check = QCheckBox("Disable AI Analysis")
        self.force_check = QCheckBox("Force Analysis (even with syntax errors)")
        
        options_layout.addWidget(self.verbose_check)
        options_layout.addWidget(self.no_ai_check)
        options_layout.addWidget(self.force_check)
        options_layout.addStretch()
        
        options_group.setLayout(options_layout)
        self.main_layout.addWidget(options_group)
    
    def setup_results_section(self):
        results_group = QGroupBox("Analysis Results")
        results_layout = QVBoxLayout()
        
        self.results_text = QTextEdit()
        self.results_text.setReadOnly(True)
        self.results_text.setFont(QFont("Consolas", 10))
        
        results_layout.addWidget(self.results_text)
        results_group.setLayout(results_layout)
        
        # Make results section expand to fill available space
        self.main_layout.addWidget(results_group, 1)  # 1 is stretch factor
    
    def setup_status_bar(self):
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setTextVisible(False)
        self.progress_bar.setMaximumHeight(15)
        self.progress_bar.setMaximumWidth(200)
        self.progress_bar.setVisible(False)
        
        self.status_bar.addPermanentWidget(self.progress_bar)
        self.status_bar.showMessage("Ready")
    
    def browse_file(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select Python File",
            "",
            "Python Files (*.py);;All Files (*)"
        )
        
        if file_path:
            self.file_path_input.setText(file_path)
    
    def analyze_code(self):
        file_path = self.file_path_input.text()
        if not file_path:
            QMessageBox.warning(self, "No File Selected", "Please select a Python file to analyze.")
            return
        
        if not os.path.exists(file_path):
            QMessageBox.critical(self, "File Not Found", f"The file {file_path} does not exist.")
            return
        
        # Clear previous results
        self.results_text.clear()
        
        # Start progress bar
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 0)  # Indeterminate progress
        self.status_bar.showMessage("Analyzing...")
        
        # Collect options
        options = {
            'verbose': self.verbose_check.isChecked(),
            'no_ai': self.no_ai_check.isChecked(),
            'force': self.force_check.isChecked()
        }
        
        # Create and start worker thread
        self.analysis_thread = AnalysisWorker(file_path, options)
        self.analysis_thread.update_signal.connect(self.update_results)
        self.analysis_thread.finished_signal.connect(self.show_analysis_results)
        self.analysis_thread.error_signal.connect(self.show_error)
        self.analysis_thread.finished.connect(self.analysis_completed)
        self.analysis_thread.start()
    
    @pyqtSlot(str)
    def update_results(self, message):
        self.results_text.append(message)
    
    @pyqtSlot(dict)
    def show_analysis_results(self, results):
        if results['type'] == 'basic':
            self.show_basic_analysis(results['parsed_code'], results['verbose'])
        else:
            self.show_full_analysis(
                results['file_path'],
                results['parsed_code'],
                results['issues'],
                results['suggestions'],
                results['verbose']
            )
    
    @pyqtSlot(str)
    def show_error(self, message):
        self.results_text.append(f"\n❌ {message}")
        # Make text red
        cursor = self.results_text.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.End)
        cursor.movePosition(QTextCursor.MoveOperation.PreviousBlock, QTextCursor.MoveMode.KeepAnchor)
        format = QTextCharFormat()
        format.setForeground(QColor("red"))
        cursor.mergeCharFormat(format)
    
    @pyqtSlot()
    def analysis_completed(self):
        self.progress_bar.setVisible(False)
        self.status_bar.showMessage("Analysis complete")
    
    def show_basic_analysis(self, parsed_code, verbose):
        self.results_text.append("\n" + "="*80)
        self.results_text.append(f"BASIC ANALYSIS REPORT (SYNTAX ERRORS DETECTED): {parsed_code['filename']}")
        self.results_text.append("="*80)
        
        # File information
        self.results_text.append("\n📝 FILE INFORMATION:")
        self.results_text.append(parsed_code['description'])
        self.results_text.append(f"Total lines: {len(parsed_code['lines'])}")
        
        # Syntax error details
        self.results_text.append("\⚠️ SYNTAX ERROR DETAILS:")
        error_info = parsed_code.get('syntax_error_info', {})
        if error_info:
            self.results_text.append(f"  Error on line {error_info.get('line', 'unknown')}: {error_info.get('message', 'Unknown error')}")
            
            # Show the problematic line if available
            if 'line' in error_info and error_info['line'] <= len(parsed_code['lines']):
                line_num = error_info['line']
                line_content = parsed_code['lines'][line_num - 1]
                self.results_text.append(f"\n  Line {line_num}: {line_content}")
                
                # Show a pointer to the error position if available
                if 'offset' in error_info and error_info['offset'] > 0:
                    pointer = ' ' * (len(f"  Line {line_num}: ") + error_info['offset'] - 1) + '^'
                    self.results_text.append(pointer)
        
        self.results_text.append("\n" + "="*80)
        self.results_text.append("To run a more detailed analysis despite syntax errors, check the 'Force Analysis' option")
        self.results_text.append("="*80)
    
    def show_full_analysis(self, file_path, parsed_code, issues, suggestions, verbose):
        self.results_text.append("\n" + "="*80)
        self.results_text.append(f"CODE ANALYSIS REPORT: {file_path}")
        self.results_text.append("="*80)
        
        # Syntax error warning if using force
        if parsed_code.get('has_syntax_errors', False):
            self.results_text.append("\n⚠️ WARNING: This file contains syntax errors. Analysis may be incomplete.")
            error_info = parsed_code.get('syntax_error_info', {})
            if error_info:
                self.results_text.append(f"  Error on line {error_info.get('line', 'unknown')}: {error_info.get('message', 'Unknown error')}")
        
        # Code description
        self.results_text.append("\n📝 CODE DESCRIPTION:")
        self.results_text.append(parsed_code['description'])
        
        # Issues
        self.results_text.append("\n❌ ISSUES DETECTED:")
        if issues:
            for i, issue in enumerate(issues, 1):
                self.results_text.append(f"\n  Issue #{i}: {issue['type']}")
                self.results_text.append(f"  Line {issue['line']}: {issue['message']}")
                if issue.get('suggestion'):
                    self.results_text.append(f"  Suggestion: {issue['suggestion']}")
                if verbose and issue.get('context'):
                    self.results_text.append(f"  Context: {issue['context']}")
        else:
            self.results_text.append("  No issues detected!")
        
        # Suggestions
        self.results_text.append("\n✨ IMPROVEMENT SUGGESTIONS:")
        if suggestions:
            for i, suggestion in enumerate(suggestions, 1):
                self.results_text.append(f"\n  Suggestion #{i}: {suggestion['title']}")
                self.results_text.append(f"  Description: {suggestion['description']}")
                if suggestion.get('code'):
                    self.results_text.append(f"\n  Example implementation:\n")
                    for line in suggestion['code'].split('\n'):
                        self.results_text.append(f"    {line}")
        else:
            self.results_text.append("  No suggestions available.")
        
        self.results_text.append("\n" + "="*80)


def main():
    app = QApplication(sys.argv)
    window = TruCodeApp()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()