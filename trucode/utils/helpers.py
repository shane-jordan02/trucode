"""
Helper functions for code analysis and transformation.
"""

def get_line_content(lines, line_number):
    """
    Get the content of a specific line (1-based indexing).
    
    Args:
        lines: List of lines in the file
        line_number: Line number to retrieve (1-based index)
        
    Returns:
        The content of the line, or None if line number is out of range
    """
    if 1 <= line_number <= len(lines):
        return lines[line_number - 1]
    return None

def extract_code_from_line(line):
    """
    Extract code from a line, removing comments.
    
    Args:
        line: A line of code that may contain comments
        
    Returns:
        The code portion of the line with comments removed and whitespace trimmed
    """
    if '#' in line:
        line = line.split('#')[0]
    return line.strip()