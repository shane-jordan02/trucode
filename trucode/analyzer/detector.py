import ast
import re
from trucode.utils.helpers import get_line_content, extract_code_from_line

class IssueDetector:
    """Detect common issues in Python code."""
    
    def detect_issues(self, parsed_code):
        """
        Analyze code and detect potential issues.
        Returns a list of issues found.
        """
        if not parsed_code:
            return []
        
        # If the file has syntax errors and no AST, return just the syntax error
        if parsed_code.get('has_syntax_errors', False) and not parsed_code.get('ast'):
            error_info = parsed_code.get('syntax_error_info', {})
            issues = [{
                'type': 'Syntax Error',
                'line': error_info.get('line', 1),
                'message': f"Syntax error: {error_info.get('message', 'Unknown syntax error')}",
                'suggestion': "Fix the syntax error to make the code valid."
            }]
            return issues
        
        issues = []
        
        # Run all detectors, but only if we have an AST to analyze
        if parsed_code.get('ast'):
            issues.extend(self._detect_syntax_errors(parsed_code))
            issues.extend(self._detect_undefined_variables(parsed_code))
            issues.extend(self._detect_unused_imports(parsed_code))
            issues.extend(self._detect_unused_variables(parsed_code))
            issues.extend(self._detect_complex_functions(parsed_code))
            issues.extend(self._detect_missing_docstrings(parsed_code))
            issues.extend(self._detect_exception_handling(parsed_code))
            issues.extend(self._detect_hardcoded_values(parsed_code))
            issues.extend(self._detect_main_guard(parsed_code))
        else:
            # If we don't have an AST, just report it as a syntax error
            issues.append({
                'type': 'Syntax Error',
                'line': 1,
                'message': "The file contains syntax errors and could not be fully analyzed.",
                'suggestion': "Fix the syntax errors to enable complete analysis."
            })
        
        return issues
    
    def _detect_syntax_errors(self, parsed_code):
        """Check for syntax errors in the code."""
        issues = []
        try:
            ast.parse(parsed_code['code'])
        except SyntaxError as e:
            issues.append({
                'type': 'Syntax Error',
                'line': e.lineno,
                'message': f"Syntax error: {e.msg}",
                'suggestion': "Fix the syntax error to make the code valid."
            })
        return issues
    
    def _detect_undefined_variables(self, parsed_code):
        """Detect potentially undefined variables."""
        issues = []
        
        # Skip if no AST
        if not parsed_code.get('ast'):
            return issues
            
        defined_names = set()
        used_names = set()
        
        # Helper function to check nodes
        def process_node(node):
            if node is None:
                return
                
            if isinstance(node, ast.Name):
                if isinstance(node.ctx, ast.Store):
                    defined_names.add(node.id)
                elif isinstance(node.ctx, ast.Load):
                    used_names.add(node.id)
        
        # Walk through all nodes
        try:
            for node in ast.walk(parsed_code['ast']):
                process_node(node)
        except (AttributeError, TypeError) as e:
            # If we encounter an error during walking, just return no issues
            print(f"Warning: Error during variable analysis: {e}")
            return []
        
        # Built-in names and common globals that might be imported
        builtins = dir(__builtins__)
        
        # Check for used but not defined names
        for name in used_names:
            if name not in defined_names and name not in builtins:
                # Find line number where this name is used
                line_num = None
                for i, line in enumerate(parsed_code['lines'], 1):
                    if re.search(rf'\b{name}\b', line):
                        line_num = i
                        break
                
                if line_num:
                    issues.append({
                        'type': 'Potential Undefined Variable',
                        'line': line_num,
                        'message': f"Variable '{name}' is used but might not be defined.",
                        'suggestion': f"Make sure '{name}' is defined before use, or check for typos."
                    })
        
        return issues
    
    def _detect_unused_imports(self, parsed_code):
        """Detect imported modules that are not used."""
        issues = []
        
        # Skip if no AST
        if not parsed_code.get('ast'):
            return issues
            
        # Get all imported names
        imported_names = {}
        try:
            for node in ast.walk(parsed_code['ast']):
                if isinstance(node, ast.Import):
                    for name in node.names:
                        imported_names[name.name.split('.')[0]] = node.lineno
                elif isinstance(node, ast.ImportFrom):
                    for name in node.names:
                        if name.asname:
                            imported_names[name.asname] = node.lineno
                        else:
                            imported_names[name.name] = node.lineno
        except (AttributeError, TypeError) as e:
            # If we encounter an error during walking, just return no issues
            print(f"Warning: Error during import analysis: {e}")
            return []
        
        # Get all used names
        used_names = set()
        try:
            for node in ast.walk(parsed_code['ast']):
                if isinstance(node, ast.Name) and isinstance(node.ctx, ast.Load):
                    used_names.add(node.id)
        except (AttributeError, TypeError) as e:
            # If we encounter an error during walking, just return no issues
            print(f"Warning: Error during name usage analysis: {e}")
            return []
        
        # Find unused imports
        for imported_name, line_num in imported_names.items():
            if imported_name not in used_names:
                issues.append({
                    'type': 'Unused Import',
                    'line': line_num,
                    'message': f"Import '{imported_name}' is not used in the code.",
                    'suggestion': f"Remove the unused import to make the code cleaner."
                })
        
        return issues
    
    def _detect_unused_variables(self, parsed_code):
        """Detect defined variables that are not used."""
        issues = []
        
        # Skip if no AST
        if not parsed_code.get('ast'):
            return issues
            
        assigned_names = {}
        used_names = set()
        
        # Find all assigned and used names
        try:
            for node in ast.walk(parsed_code['ast']):
                if isinstance(node, ast.Assign):
                    for target in node.targets:
                        if isinstance(target, ast.Name):
                            assigned_names[target.id] = target.lineno
                elif isinstance(node, ast.Name) and isinstance(node.ctx, ast.Load):
                    used_names.add(node.id)
        except (AttributeError, TypeError) as e:
            # If we encounter an error during walking, just return no issues
            print(f"Warning: Error during variable usage analysis: {e}")
            return []
        
        # Check for unused variables (ignore if starts with underscore)
        for name, line_num in assigned_names.items():
            if name not in used_names and not name.startswith('_'):
                issues.append({
                    'type': 'Unused Variable',
                    'line': line_num,
                    'message': f"Variable '{name}' is assigned but never used.",
                    'suggestion': f"Remove the unused variable or prefix with underscore (_) if intentional."
                })
        
        return issues
    
    def _detect_complex_functions(self, parsed_code):
        """Detect functions that are too complex or too long."""
        issues = []
        
        # Skip if no functions detected
        if not parsed_code.get('functions'):
            return issues
            
        for func in parsed_code['functions']:
            function_length = func['end_line'] - func['start_line']
            
            # Check for very long functions
            if function_length > 50:
                issues.append({
                    'type': 'Complex Function',
                    'line': func['start_line'],
                    'message': f"Function '{func['name']}' is very long ({function_length} lines).",
                    'suggestion': "Consider breaking this function into smaller, more focused functions."
                })
            
            # Check for functions with too many arguments
            if len(func['args']) > 5:
                issues.append({
                    'type': 'Too Many Arguments',
                    'line': func['start_line'],
                    'message': f"Function '{func['name']}' has {len(func['args'])} parameters, which might be too many.",
                    'suggestion': "Consider grouping related parameters into a class or dictionary."
                })
        
        return issues
    
    def _detect_missing_docstrings(self, parsed_code):
        """Detect missing docstrings in functions and classes."""
        issues = []
        
        # Check functions
        for func in parsed_code.get('functions', []):
            if not func['docstring'] and not func['name'].startswith('_'):
                issues.append({
                    'type': 'Missing Docstring',
                    'line': func['start_line'],
                    'message': f"Function '{func['name']}' lacks a docstring.",
                    'suggestion': "Add a descriptive docstring to document the function's purpose and usage."
                })
        
        # Check classes
        for cls in parsed_code.get('classes', []):
            if not cls['docstring']:
                issues.append({
                    'type': 'Missing Docstring',
                    'line': cls['start_line'],
                    'message': f"Class '{cls['name']}' lacks a docstring.",
                    'suggestion': "Add a descriptive docstring to document the class's purpose and usage."
                })
        
        return issues
    
    def _detect_exception_handling(self, parsed_code):
        """Detect bare exceptions and other exception handling issues."""
        issues = []
        
        # Skip if no AST
        if not parsed_code.get('ast'):
            return issues
            
        try:
            for node in ast.walk(parsed_code['ast']):
                if isinstance(node, ast.Try):
                    for handler in node.handlers:
                        if handler.type is None:
                            issues.append({
                                'type': 'Bare Exception',
                                'line': handler.lineno,
                                'message': "Using a bare 'except:' clause catches all exceptions, including KeyboardInterrupt and SystemExit.",
                                'suggestion': "Catch specific exceptions instead, like 'except ValueError:' or use 'except Exception:' if necessary."
                            })
        except (AttributeError, TypeError) as e:
            # If we encounter an error during walking, just return no issues
            print(f"Warning: Error during exception analysis: {e}")
            return []
        
        return issues
    
    def _detect_hardcoded_values(self, parsed_code):
        """Detect hardcoded values that might be better as constants."""
        issues = []
        
        # Skip if no AST
        if not parsed_code.get('ast'):
            return issues
            
        seen_values = {}
        
        try:
            for node in ast.walk(parsed_code['ast']):
                if isinstance(node, ast.Constant):
                    # Skip small numbers and empty strings
                    if isinstance(node.value, (int, float)) and abs(node.value) <= 1:
                        continue
                    if isinstance(node.value, str) and len(node.value) <= 1:
                        continue
                    
                    # Track constants by their value and location
                    value_str = str(node.value)
                    if value_str in seen_values:
                        seen_values[value_str]['count'] += 1
                    else:
                        seen_values[value_str] = {
                            'count': 1,
                            'line': node.lineno,
                            'value': node.value
                        }
        except (AttributeError, TypeError) as e:
            # If we encounter an error during walking, just return no issues
            print(f"Warning: Error during constants analysis: {e}")
            return []
        
        # Report repeated hardcoded values
        for value_str, info in seen_values.items():
            if info['count'] > 2:
                value_display = repr(info['value']) if isinstance(info['value'], str) else str(info['value'])
                issues.append({
                    'type': 'Repeated Hardcoded Value',
                    'line': info['line'],
                    'message': f"Value {value_display} appears {info['count']} times in the code.",
                    'suggestion': f"Consider defining a constant for this value to improve maintainability."
                })
        
        return issues
    
    def _detect_main_guard(self, parsed_code):
        """Check if the script has a proper if __name__ == '__main__' guard."""
        issues = []
        
        # Skip if no functions are defined (might be a simple script) or no AST
        if not parsed_code.get('functions') or not parsed_code.get('ast'):
            return issues
        
        has_main_guard = False
        try:
            for node in ast.walk(parsed_code['ast']):
                if isinstance(node, ast.If):
                    # Check for if __name__ == '__main__':
                    if (isinstance(node.test, ast.Compare) and 
                        isinstance(node.test.left, ast.Name) and
                        node.test.left.id == '__name__' and
                        len(node.test.ops) > 0 and
                        isinstance(node.test.ops[0], ast.Eq) and
                        len(node.test.comparators) > 0 and
                        isinstance(node.test.comparators[0], ast.Constant) and
                        node.test.comparators[0].value == '__main__'):
                        has_main_guard = True
                        break
        except (AttributeError, TypeError) as e:
            # If we encounter an error during walking, just return no issues
            print(f"Warning: Error during main guard analysis: {e}")
            return []
        
        if not has_main_guard:
            # Find the last line to suggest adding the guard there
            last_line = len(parsed_code['lines'])
            issues.append({
                'type': 'Missing Main Guard',
                'line': last_line,
                'message': "Missing 'if __name__ == \"__main__\":' guard for script code.",
                'suggestion': "Add 'if __name__ == \"__main__\":' guard to make the script importable without executing the main code."
            })
        
        return issues