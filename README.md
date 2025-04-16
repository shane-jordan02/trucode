# TruCode

A Python code analyzer that detects common issues and suggests improvements.

## Features

- Parse Python code and extract meaningful information
- Detect common issues in Python code (syntax errors, unused imports, etc.)
- Generate improvement suggestions
- Optional AI-powered code analysis

## Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/trucode.git
cd trucode

# Install the package
pip install -e .
```

## Usage

```bash
# Analyze a Python file
trucode path/to/your/python_file.py

# Enable verbose output
trucode path/to/your/python_file.py --verbose

# Disable AI analysis
trucode path/to/your/python_file.py --no-ai
```

## Requirements

- Python 3.7+
- See requirements.txt for package dependencies

## Project Structure

```
trucode/
├── analyzer/
│   ├── __init__.py
│   ├── detector.py
│   ├── model_wrapper.py
│   ├── parser.py
│   └── suggester.py
├── utils/
│   ├── __init__.py
│   └── helpers.py
├── __init__.py
├── main.py
└── examples/
    └── test_code.py
```

## License

MIT