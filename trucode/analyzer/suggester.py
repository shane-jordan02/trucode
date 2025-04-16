import ast
import re
from trucode.analyzer.model_wrapper import ModelWrapper

class CodeSuggester:
    """Generate improvement suggestions for Python code."""
    
    def __init__(self):
        """Initialize the code suggester with necessary models."""
        # Initialize model wrapper for AI-based suggestions
        self.model_wrapper = ModelWrapper()
    
    def generate_suggestions(self, parsed_code, issues):
        """Generate suggestions for code improvements."""
        if not parsed_code:
            return []
        
        # Handle files with syntax errors
        if parsed_code.get('has_syntax_errors', False) and not parsed_code.get('ast'):
            return self._generate_syntax_error_suggestions(parsed_code, issues)
        
        suggestions = []
        
        # Generate rule-based suggestions
        suggestions.extend(self._suggest_code_structure(parsed_code))
        suggestions.extend(self._suggest_best_practices(parsed_code))
        suggestions.extend(self._suggest_documentation(parsed_code))
        suggestions.extend(self._suggest_from_issues(issues))
        
        # Generate AI-based suggestions
        ai_suggestions = self._generate_ai_suggestions(parsed_code, issues)
        if ai_suggestions:
            suggestions.extend(ai_suggestions)
        
        return suggestions
    
    def _generate_syntax_error_suggestions(self, parsed_code, issues):
        """Generate suggestions for files with syntax errors."""
        suggestions = []
        
        error_info = parsed_code.get('syntax_error_info', {})
        error_message = error_info.get('message', 'Unknown syntax error')
        
        # Common syntax errors and suggested fixes
        if 'unexpected indent' in error_message.lower():
            suggestions.append({
                'title': "Fix indentation issues",
                'description': "There appears to be an indentation error in your code. Python uses indentation to define code blocks.",
                'code': "# Correct indentation example:\ndef example_function():\n    # This line is indented with 4 spaces\n    print('Hello, World!')\n\n    if True:\n        # This line is indented with 8 spaces (4 more than parent)\n        print('Inside if block')"
            })
        elif 'expected an indented block' in error_message.lower():
            suggestions.append({
                'title': "Add proper indentation after block statements",
                'description': "After statements like 'if', 'for', 'while', etc., you need an indented block of code.",
                'code': "# Correct indentation example:\nif condition:\n    # This line must be indented\n    do_something()\n\n# Instead of:\nif condition:\ndo_something()  # This will cause an indentation error"
            })
        elif 'invalid syntax' in error_message.lower():
            suggestions.append({
                'title': "Check for syntax errors",
                'description': "There's a syntax error in your code. Common causes include missing parentheses, brackets, colons, or invalid Python statements.",
                'code': "# Common syntax examples:\n# Missing colon\nif condition  # Error\n    print('Hi')\n\n# Correct version\nif condition:  # Note the colon\n    print('Hi')"
            })
        elif 'EOF' in error_message:
            suggestions.append({
                'title': "Check for unclosed brackets or quotes",
                'description': "You might have unclosed parentheses, brackets, or quotation marks in your code.",
                'code': "# Examples of properly closed structures:\nmy_list = [1, 2, 3]  # Opening and closing brackets\nmy_dict = {'key': 'value'}  # Opening and closing braces\nmy_string = \"Hello, world!\"  # Opening and closing quotes"
            })
        else:
            # Generic suggestion for syntax errors
            suggestions.append({
                'title': "Fix syntax errors before analysis",
                'description': f"Your code contains a syntax error: {error_message}. Fix this error to enable proper code analysis.",
                'code': "# Common Python syntax error checklist:\n# 1. Check indentation (use 4 spaces consistently)\n# 2. Ensure all parentheses, brackets, and braces are properly closed\n# 3. Check for missing colons after if, for, while, etc.\n# 4. Make sure all strings are properly closed\n# 5. Verify that keywords are used correctly"
            })
        
        # Add a suggestion about using linters
        suggestions.append({
            'title': "Use a linter to catch syntax errors",
            'description': "Consider using a Python linter like flake8, pylint, or an IDE with built-in linting to catch syntax errors as you write code.",
            'code': "# Install a linter:\n# pip install flake8\n\n# Run the linter on your code:\n# flake8 your_file.py"
        })
        
        return suggestions
    
    def _suggest_code_structure(self, parsed_code):
        """Suggest improvements to code structure."""
        suggestions = []
        
        # Check if main function is missing
        has_main = any(func['name'] == 'main' for func in parsed_code.get('functions', []))
        
        # Check for main guard in the code text directly to be safe
        has_main_guard = "__name__" in parsed_code['code'] and "__main__" in parsed_code['code']
        
        if not has_main_guard and len(parsed_code.get('functions', [])) > 0:
            suggestions.append({
                'title': "Add a main function with proper entry point",
                'description': "Consider organizing your code with a main() function and use the if __name__ == '__main__' pattern to make the script both importable and executable.",
                'code': "def main():\n    # Your main logic here\n    pass\n\nif __name__ == '__main__':\n    main()"
            })
        
        # Check for module-level organization
        if len(parsed_code.get('functions', [])) > 5 and len(parsed_code.get('classes', [])) == 0:
            suggestions.append({
                'title': "Consider organizing functions into classes",
                'description': "Your code has multiple functions but no classes. Consider organizing related functions into class(es) for better structure and maintainability.",
                'code': "class MyClass:\n    \"\"\"A class to encapsulate related functionality.\"\"\"\n    \n    def __init__(self):\n        # Initialize your class\n        pass\n    \n    def method1(self):\n        # First method\n        pass"
            })
        
        return suggestions
    
    def _suggest_best_practices(self, parsed_code):
        """Suggest Python best practices."""
        suggestions = []
        
        # Check for comments over docstrings
        has_comments = False
        has_docstrings = any(func.get('docstring') for func in parsed_code.get('functions', []))
        
        for line in parsed_code.get('lines', []):
            if line.strip().startswith('#') and not line.strip().startswith('# '):
                has_comments = True
                break
        
        if has_comments and not has_docstrings:
            suggestions.append({
                'title': "Use docstrings instead of comments for function documentation",
                'description': "Python has built-in support for documentation strings. Consider using docstrings for documenting functions and classes instead of comments.",
                'code': "def example_function():\n    \"\"\"This is a docstring.\n    \n    It can span multiple lines and provides documentation\n    that can be accessed through the __doc__ attribute.\n    \"\"\"\n    # Function implementation"
            })
        
        # Check for error handling
        has_try_except = "try:" in parsed_code['code'] and "except" in parsed_code['code']
        if not has_try_except and len(parsed_code.get('functions', [])) > 2:
            suggestions.append({
                'title': "Add error handling",
                'description': "Consider adding error handling with try-except blocks for robustness, especially for I/O operations, network calls, or user inputs.",
                'code': "try:\n    result = potentially_risky_function()\nexcept SpecificError as e:\n    print(f\"An error occurred: {e}\")\n    # Handle the error appropriately"
            })
        
        # Check for constants
        has_constants = False
        for line in parsed_code.get('lines', []):
            if re.match(r'^[A-Z][A-Z0-9_]*\s*=', line):
                has_constants = True
                break
        
        if not has_constants and len(parsed_code.get('lines', [])) > 30:
            suggestions.append({
                'title': "Define constants for magic values",
                'description': "Consider defining constants at the module level for values that are used multiple times in your code.",
                'code': "# Define constants at the top of your module\nMAX_RETRIES = 3\nDEFAULT_TIMEOUT = 30\nBASE_URL = 'https://api.example.com'"
            })
        
        return suggestions
    
    def _suggest_documentation(self, parsed_code):
        """Suggest documentation improvements."""
        suggestions = []
        
        # Check if module has a module-level docstring
        try:
            if parsed_code.get('ast'):
                module_docstring = ast.get_docstring(parsed_code['ast'])
                if not module_docstring and len(parsed_code.get('functions', [])) + len(parsed_code.get('classes', [])) > 1:
                    suggestions.append({
                        'title': "Add a module-level docstring",
                        'description': "Consider adding a module-level docstring to explain the purpose and usage of this module.",
                        'code': "\"\"\"Module name: Brief description.\n\nDetailed description of what this module does, how to use it,\nand any dependencies or important information.\n\"\"\"\n\n# Rest of your module code..."
                    })
        except (AttributeError, TypeError):
            # Skip this check if we get an error
            pass
        
        # Check for type hints
        has_type_hints = False
        for line in parsed_code.get('lines', []):
            if "->" in line or ":" in line and "def " in line:
                has_type_hints = True
                break
        
        if not has_type_hints and len(parsed_code.get('functions', [])) > 2:
            suggestions.append({
                'title': "Add type hints",
                'description': "Consider adding type hints to function parameters and return values for better documentation and IDE support.",
                'code': "def calculate_total(items: list[float], tax_rate: float = 0.0) -> float:\n    \"\"\"Calculate the total price including tax.\n    \n    Args:\n        items: List of item prices\n        tax_rate: The tax rate as a decimal\n        \n    Returns:\n        The total price including tax\n    \"\"\"\n    subtotal = sum(items)\n    return subtotal * (1 + tax_rate)"
            })
        
        return suggestions
    
    def _suggest_from_issues(self, issues):
        """Generate suggestions based on detected issues."""
        suggestions = []
        
        # Extract issue types
        issue_types = set()
        for issue in issues:
            issue_types.add(issue.get('type', ''))
        
        # Generate suggestions based on common issue patterns
        if 'Missing Docstring' in issue_types:
            suggestions.append({
                'title': "Add comprehensive docstrings",
                'description': "Add descriptive docstrings to all functions and classes to improve code readability and maintainability.",
                'code': "def example_function(param1, param2):\n    \"\"\"Short description of what the function does.\n    \n    Args:\n        param1: Description of param1\n        param2: Description of param2\n        \n    Returns:\n        Description of return value\n        \n    Raises:\n        ExceptionType: When and why this exception is raised\n    \"\"\"\n    # Function implementation"
            })
        
        if 'Unused Import' in issue_types:
            suggestions.append({
                'title': "Clean up imports",
                'description': "Remove unused imports to keep your code clean and improve loading time.",
                'code': "# Instead of\nimport os\nimport sys\nimport numpy  # Unused\n\n# Use only what you need\nimport os\nimport sys"
            })
        
        if 'Complex Function' in issue_types:
            suggestions.append({
                'title': "Refactor complex functions",
                'description': "Break down complex functions into smaller, more focused functions with single responsibilities.",
                'code': "# Instead of one large function\ndef process_data(data):\n    # 50+ lines of code\n    pass\n\n# Break it down\ndef validate_data(data):\n    # Validation logic\n    pass\n\ndef transform_data(data):\n    # Transformation logic\n    pass\n\ndef process_data(data):\n    validated_data = validate_data(data)\n    return transform_data(validated_data)"
            })
        
        if 'Syntax Error' in issue_types:
            suggestions.append({
                'title': "Fix syntax errors",
                'description': "Your code contains syntax errors that prevent proper execution. Fix these errors before proceeding with further development.",
                'code': "# Common syntax error fixes:\n\n# 1. Fix indentation (use consistent spaces)\ndef function():\n    print('Properly indented')\n\n# 2. Add missing colons\nif condition:\n    print('Colon added')\n\n# 3. Close all brackets and quotes\nmy_list = [1, 2, 3]  # Closed bracket\nmy_string = \"Complete string\"  # Closed quotes"
            })
        
        return suggestions
    
    def _generate_ai_suggestions(self, parsed_code, issues):
        """Generate suggestions using AI model if available."""
        try:
            # Skip AI analysis for files with syntax errors
            if parsed_code.get('has_syntax_errors', False):
                return []
                
            # Extract key information for the AI model
            code_sample = parsed_code['code'][:1000]  # Limit size
            issue_summary = "\n".join([f"- {issue['type']} on line {issue['line']}: {issue['message']}" 
                                    for issue in issues[:5]])
            
            # Use model wrapper for analysis
            ai_analysis = self.model_wrapper.analyze_code(code_sample)
            
            if ai_analysis and 'suggestions' in ai_analysis:
                # Convert AI suggestions to the expected format
                return [{'title': suggestion, 'description': suggestion} 
                        for suggestion in ai_analysis['suggestions']]
            
        except Exception as e:
            print(f"Error generating AI suggestions: {e}")
        
        return []