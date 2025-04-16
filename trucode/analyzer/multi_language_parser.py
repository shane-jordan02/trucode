import os
import re
from io import BytesIO

class MultiLanguageParser:
    """Parse code files in multiple languages and extract meaningful information."""
    
    def parse(self, file_path):
        """Parse a code file and return structured information about it."""
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                code = file.read()
            
            # Basic info
            filename = os.path.basename(file_path)
            lines = code.split('\n')
            
            # Determine language based on file extension
            extension = os.path.splitext(filename)[1].lower()
            language = self._detect_language(extension)
            
            # Generate simple description
            description = self._generate_description(filename, language, code)
            
            return {
                'filename': filename,
                'code': code,
                'language': language,
                'lines': lines,
                'description': description,
                'has_syntax_errors': False  # We'll let the AI determine this
            }
        except Exception as e:
            print(f"Error processing file: {e}")
            return {
                'filename': os.path.basename(file_path),
                'code': '',
                'language': 'unknown',
                'lines': [],
                'description': f"This file '{os.path.basename(file_path)}' could not be processed due to error: {str(e)}",
                'has_syntax_errors': True
            }
    
    def _detect_language(self, extension):
        """Detect programming language based on file extension."""
        language_map = {
            '.py': 'python',
            '.java': 'java',
            '.cpp': 'cpp',
            '.cc': 'cpp',
            '.cxx': 'cpp',
            '.c': 'c',
            '.h': 'cpp',
            '.hpp': 'cpp',
            '.cs': 'csharp'
        }
        return language_map.get(extension, 'unknown')
    
    def _generate_description(self, filename, language, code):
        """Generate a human-readable description of the code."""
        language_names = {
            'python': 'Python',
            'java': 'Java',
            'cpp': 'C++',
            'c': 'C',
            'csharp': 'C#',
            'unknown': 'unknown language'
        }
        
        lang_name = language_names.get(language, language)
        description = [f"This file '{filename}' is a {lang_name} source file."]
        
        # Estimate complexity based on line count
        line_count = len(code.split('\n'))
        if line_count < 50:
            description.append(f"It is a relatively small file ({line_count} lines).")
        elif line_count < 200:
            description.append(f"It is a medium-sized file ({line_count} lines).")
        else:
            description.append(f"It is a large file ({line_count} lines).")
        
        # Try to identify key components based on language
        if language == 'python':
            if 'class ' in code:
                description.append("It contains class definitions.")
            if 'def ' in code:
                description.append("It contains function definitions.")
            if 'import ' in code:
                description.append("It contains import statements.")
        elif language == 'java':
            if 'class ' in code:
                description.append("It contains class definitions.")
            if 'interface ' in code:
                description.append("It contains interface definitions.")
            if 'import ' in code:
                description.append("It contains import statements.")
        elif language in ['cpp', 'c']:
            if 'class ' in code:
                description.append("It contains class definitions.")
            if 'struct ' in code:
                description.append("It contains struct definitions.")
            if '#include ' in code:
                description.append("It contains include directives.")
        elif language == 'csharp':
            if 'class ' in code:
                description.append("It contains class definitions.")
            if 'interface ' in code:
                description.append("It contains interface definitions.")
            if 'using ' in code:
                description.append("It contains using directives.")
        
        return " ".join(description)