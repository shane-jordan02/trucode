import ast
import os
import re
import tokenize
from io import BytesIO

class CodeParser:
    """Parse Python code files and extract meaningful information."""
    
    def parse(self, file_path):
        """Parse a Python file and return structured information about it."""
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                code = file.read()
            
            # Basic info
            filename = os.path.basename(file_path)
            lines = code.split('\n')
            
            # Try to parse with AST
            try:
                tree = ast.parse(code)
                # Extract high-level code information
                functions = self._extract_functions(tree)
                classes = self._extract_classes(tree)
                imports = self._extract_imports(tree)
                has_syntax_errors = False
                syntax_error_info = None
            except SyntaxError as e:
                # Still return partial information even with syntax errors
                print(f"Warning: Syntax error in file: {e}")
                tree = None
                functions = []
                classes = []
                imports = self._extract_imports_from_text(code)
                has_syntax_errors = True
                syntax_error_info = {
                    'line': e.lineno,
                    'offset': e.offset,
                    'message': str(e)
                }
                
                # Try to extract some basic information despite syntax errors
                self._analyze_tokens(code)
            
            # Generate simple description
            description = self._generate_description(filename, functions, classes, imports, has_syntax_errors)
            
            # Even with syntax errors, we return what we can
            return {
                'filename': filename,
                'code': code,
                'ast': tree,
                'functions': functions,
                'classes': classes,
                'imports': imports,
                'description': description,
                'lines': lines,
                'has_syntax_errors': has_syntax_errors,
                'syntax_error_info': syntax_error_info
            }
        except Exception as e:
            print(f"Error processing file: {e}")
            return {
                'filename': os.path.basename(file_path),
                'code': '',
                'ast': None,
                'functions': [],
                'classes': [],
                'imports': [],
                'description': f"This file '{os.path.basename(file_path)}' could not be processed due to error: {str(e)}",
                'lines': [],
                'has_syntax_errors': True,
                'syntax_error_info': {'message': str(e)}
            }
    
    def _extract_functions(self, tree):
        """Extract function definitions from AST."""
        functions = []
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                # Get docstring if available
                docstring = ast.get_docstring(node)
                
                # Get arguments
                args = []
                for arg in node.args.args:
                    args.append(arg.arg)
                
                # Get function range (line numbers)
                start_line = node.lineno
                end_line = max([n.lineno for n in ast.walk(node) if hasattr(n, 'lineno')], default=start_line)
                
                functions.append({
                    'name': node.name,
                    'docstring': docstring,
                    'args': args,
                    'start_line': start_line,
                    'end_line': end_line
                })
        return functions
    
    def _extract_classes(self, tree):
        """Extract class definitions from AST."""
        classes = []
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                # Get docstring if available
                docstring = ast.get_docstring(node)
                
                # Get methods
                methods = []
                for child in node.body:
                    if isinstance(child, ast.FunctionDef):
                        methods.append(child.name)
                
                # Get class range (line numbers)
                start_line = node.lineno
                end_line = max([n.lineno for n in ast.walk(node) if hasattr(n, 'lineno')], default=start_line)
                
                classes.append({
                    'name': node.name,
                    'docstring': docstring,
                    'methods': methods,
                    'start_line': start_line,
                    'end_line': end_line
                })
        return classes
    
    def _extract_imports(self, tree):
        """Extract import statements from AST."""
        imports = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for name in node.names:
                    imports.append(name.name)
            elif isinstance(node, ast.ImportFrom):
                module = node.module
                for name in node.names:
                    imports.append(f"{module}.{name.name}")
        return imports
    
    def _extract_imports_from_text(self, code):
        """Extract imports by scanning the text (used when AST parsing fails)."""
        imports = []
        import_pattern = re.compile(r'^import\s+([a-zA-Z0-9_.]+)')
        from_import_pattern = re.compile(r'^from\s+([a-zA-Z0-9_.]+)\s+import\s+([a-zA-Z0-9_., ]+)')
        
        for line in code.split('\n'):
            line = line.strip()
            
            # Check for 'import x'
            match = import_pattern.match(line)
            if match:
                imports.append(match.group(1))
                continue
                
            # Check for 'from x import y'
            match = from_import_pattern.match(line)
            if match:
                module = match.group(1)
                for name in match.group(2).split(','):
                    name = name.strip()
                    if name and name != '*':
                        imports.append(f"{module}.{name}")
        
        return imports
    
    def _analyze_tokens(self, code):
        """Analyze code tokens for basic information when AST parsing fails."""
        try:
            tokens = tokenize.tokenize(BytesIO(code.encode('utf-8')).readline)
            token_list = list(tokens)
            
            # Extract token information if needed
            # This is a placeholder for any token-based analysis you might want to add
            return token_list
        except Exception as e:
            print(f"Token analysis failed: {e}")
            return []
    
    def _generate_description(self, filename, functions, classes, imports, has_syntax_errors):
        """Generate a human-readable description of the code."""
        description = [f"This file '{filename}' is a Python script."]
        
        if has_syntax_errors:
            description[0] += " (Note: This file contains syntax errors)"
        
        if imports:
            description.append(f"It imports {len(imports)} module(s): {', '.join(imports[:5])}" + 
                             (", and others..." if len(imports) > 5 else "."))
        
        if classes:
            description.append(f"It defines {len(classes)} class(es): {', '.join([c['name'] for c in classes])}.")
        
        if functions:
            description.append(f"It contains {len(functions)} function(s): {', '.join([f['name'] for f in functions])}.")
            
        if not classes and not functions:
            if has_syntax_errors:
                description.append("Due to syntax errors, function and class analysis could not be performed.")
            else:
                description.append("It appears to be a script with no function or class definitions.")
        
        return " ".join(description)