import argparse
import os
import sys
from trucode.analyzer.parser import CodeParser
from trucode.analyzer.detector import IssueDetector
from trucode.analyzer.suggester import CodeSuggester
from trucode.analyzer.model_wrapper import ModelWrapper

def main():
    parser = argparse.ArgumentParser(description='Analyze Python code for issues and suggestions')
    parser.add_argument('file_path', type=str, help='Path to the Python file to analyze')
    parser.add_argument('--verbose', '-v', action='store_true', help='Enable verbose output')
    parser.add_argument('--no-ai', action='store_true', help='Disable AI analysis')
    parser.add_argument('--force', action='store_true', help='Force detailed analysis even for files with syntax errors')
    args = parser.parse_args()
    
    if not os.path.exists(args.file_path):
        print(f"Error: File not found: {args.file_path}")
        return
    
    print(f"Analyzing {args.file_path}...")
    
    # Parse the code
    code_parser = CodeParser()
    parsed_code = code_parser.parse(args.file_path)
    if not parsed_code:
        print(f"Error: Could not open or process {args.file_path}")
        return
    
    # Check if there are syntax errors
    if parsed_code.get('has_syntax_errors', False) and not args.force:
        print_basic_analysis(parsed_code, args.verbose)
        return
    
    # Detect issues
    print("Detecting code issues...")
    detector = IssueDetector()
    issues = detector.detect_issues(parsed_code)
    
    # Generate suggestions
    print("Generating improvement suggestions...")
    suggester = CodeSuggester()
    
    # Disable AI if requested
    if args.no_ai:
        # Monkey patch the model wrapper to return None
        suggester.model_wrapper.load_model = lambda: False
    
    suggestions = suggester.generate_suggestions(parsed_code, issues)
    
    # Display results
    print_results(args.file_path, parsed_code, issues, suggestions, args.verbose)

def print_basic_analysis(parsed_code, verbose=False):
    """Print basic analysis for files with syntax errors."""
    print("\n" + "="*80)
    print(f"BASIC ANALYSIS REPORT (SYNTAX ERRORS DETECTED): {parsed_code['filename']}")
    print("="*80)
    
    # File information
    print("\n📝 FILE INFORMATION:")
    print(parsed_code['description'])
    print(f"Total lines: {len(parsed_code['lines'])}")
    
    # Syntax error details
    print("\n⚠️ SYNTAX ERROR DETAILS:")
    error_info = parsed_code.get('syntax_error_info', {})
    if error_info:
        print(f"  Error on line {error_info.get('line', 'unknown')}: {error_info.get('message', 'Unknown error')}")
        
        # Show the problematic line if available
        if 'line' in error_info and error_info['line'] <= len(parsed_code['lines']):
            line_num = error_info['line']
            line_content = parsed_code['lines'][line_num - 1]
            print(f"\n  Line {line_num}: {line_content}")
            
            # Show a pointer to the error position if available
            if 'offset' in error_info and error_info['offset'] > 0:
                pointer = ' ' * (len(f"  Line {line_num}: ") + error_info['offset'] - 1) + '^'
                print(pointer)
    
    # Basic code checks
    print("\n🔍 BASIC CODE CHECKS:")
    
    # Check for mixed tabs and spaces
    has_tabs = any('\t' in line for line in parsed_code['lines'])
    has_spaces = any('    ' in line for line in parsed_code['lines'])
    if has_tabs and has_spaces:
        print("  ⚠️ Mixed tabs and spaces detected - this can cause indentation errors")
    
    # Check for common syntax issues
    missing_colons = []
    unclosed_parentheses = []
    unclosed_quotes = []
    
    open_parens = 0
    in_single_quote = False
    in_double_quote = False
    
    for i, line in enumerate(parsed_code['lines'], 1):
        stripped = line.strip()
        
        # Check for missing colons
        if stripped and stripped.startswith(('def ', 'class ', 'if ', 'else', 'elif ', 'for ', 'while ', 'try', 'except ', 'finally')):
            if not stripped.endswith(':'):
                missing_colons.append(i)
        
        # Count unclosed quotes and parentheses (very basic check)
        for char in line:
            if char == '(' and not in_single_quote and not in_double_quote:
                open_parens += 1
            elif char == ')' and not in_single_quote and not in_double_quote:
                open_parens -= 1
                if open_parens < 0:
                    unclosed_parentheses.append(i)
                    open_parens = 0
            elif char == "'" and not in_double_quote:
                in_single_quote = not in_single_quote
            elif char == '"' and not in_single_quote:
                in_double_quote = not in_double_quote
        
        if in_single_quote or in_double_quote:
            unclosed_quotes.append(i)
            in_single_quote = False
            in_double_quote = False
    
    if open_parens > 0:
        unclosed_parentheses.append(len(parsed_code['lines']))
    
    # Report issues
    if missing_colons:
        print(f"  ⚠️ Possibly missing colons on lines: {', '.join(map(str, missing_colons[:5]))}" + 
              ("..." if len(missing_colons) > 5 else ""))
    
    if unclosed_parentheses:
        print(f"  ⚠️ Possible unclosed parentheses on lines: {', '.join(map(str, unclosed_parentheses[:5]))}" + 
              ("..." if len(unclosed_parentheses) > 5 else ""))
    
    if unclosed_quotes:
        print(f"  ⚠️ Possible unclosed quotes on lines: {', '.join(map(str, unclosed_quotes[:5]))}" + 
              ("..." if len(unclosed_quotes) > 5 else ""))
    
    # Show imports
    if parsed_code.get('imports'):
        print("\n📦 DETECTED IMPORTS:")
        for i, imp in enumerate(parsed_code['imports'], 1):
            print(f"  {i}. {imp}")
    
    print("\n" + "="*80)
    print("To run a more detailed analysis despite syntax errors, use the --force flag")
    print("="*80)

def print_results(file_path, parsed_code, issues, suggestions, verbose):
    print("\n" + "="*80)
    print(f"CODE ANALYSIS REPORT: {file_path}")
    print("="*80)
    
    # Syntax error warning if using --force
    if parsed_code.get('has_syntax_errors', False):
        print("\n⚠️ WARNING: This file contains syntax errors. Analysis may be incomplete.")
        error_info = parsed_code.get('syntax_error_info', {})
        if error_info:
            print(f"  Error on line {error_info.get('line', 'unknown')}: {error_info.get('message', 'Unknown error')}")
    
    # Code description
    print("\n📝 CODE DESCRIPTION:")
    print(parsed_code['description'])
    
    # Issues
    print("\n❌ ISSUES DETECTED:")
    if issues:
        for i, issue in enumerate(issues, 1):
            print(f"\n  Issue #{i}: {issue['type']}")
            print(f"  Line {issue['line']}: {issue['message']}")
            if issue.get('suggestion'):
                print(f"  Suggestion: {issue['suggestion']}")
            if verbose and issue.get('context'):
                print(f"  Context: {issue['context']}")
    else:
        print("  No issues detected!")
    
    # Suggestions
    print("\n✨ IMPROVEMENT SUGGESTIONS:")
    if suggestions:
        for i, suggestion in enumerate(suggestions, 1):
            print(f"\n  Suggestion #{i}: {suggestion['title']}")
            print(f"  Description: {suggestion['description']}")
            if suggestion.get('code'):
                print(f"\n  Example implementation:\n")
                for line in suggestion['code'].split('\n'):
                    print(f"    {line}")
    else:
        print("  No suggestions available.")
    
    print("\n" + "="*80)

if __name__ == "__main__":
    main()