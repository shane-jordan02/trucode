class CodeGenerator:
    """Generate code based on natural language prompts."""
    
    def __init__(self):
        """Initialize the code generator."""
        self.model_wrapper = ModelWrapper()
    
    def generate_code(self, prompt, language="python"):
        """
        Generate code based on a natural language prompt.
        
        Args:
            prompt: Natural language description of code to generate
            language: Target programming language (python, java, cpp, csharp)
            
        Returns:
            Generated code and metadata
        """
        result = self.model_wrapper.generate_code(prompt, language)
        return result
    
    def get_supported_languages(self):
        """Get list of supported programming languages."""
        return [
            {"id": "python", "name": "Python", "extension": ".py"},
            {"id": "java", "name": "Java", "extension": ".java"},
            {"id": "cpp", "name": "C++", "extension": ".cpp"},
            {"id": "csharp", "name": "C#", "extension": ".cs"}
        ]
    
    def get_language_templates(self, language):
        """Get code templates for the specified language."""
        templates = {
            "python": {
                "class": "class MyClass:\n    \"\"\"Class docstring\"\"\"\n    \n    def __init__(self):\n        \"\"\"Initialize the class\"\"\"\n        pass\n    \n    def my_method(self):\n        \"\"\"Method docstring\"\"\"\n        pass",
                "function": "def my_function(param1, param2):\n    \"\"\"Function docstring\n    \n    Args:\n        param1: Description of param1\n        param2: Description of param2\n        \n    Returns:\n        Description of return value\n    \"\"\"\n    # Function implementation\n    pass"
            },
            "java": {
                "class": "public class MyClass {\n    // Class fields\n    private int myField;\n    \n    /**\n     * Constructor\n     */\n    public MyClass() {\n        // Initialize\n    }\n    \n    /**\n     * Method description\n     * @param param Description of param\n     * @return Description of return value\n     */\n    public int myMethod(int param) {\n        // Method implementation\n        return 0;\n    }\n}",
                "interface": "public interface MyInterface {\n    /**\n     * Method description\n     * @param param Description of param\n     * @return Description of return value\n     */\n    int myMethod(int param);\n}"
            },
            "cpp": {
                "class": "class MyClass {\nprivate:\n    // Private members\n    int myField;\n\npublic:\n    // Constructor\n    MyClass();\n    \n    // Destructor\n    ~MyClass();\n    \n    // Methods\n    int myMethod(int param);\n};\n\n// Implementation\nMyClass::MyClass() {\n    // Initialize\n}\n\nMyClass::~MyClass() {\n    // Cleanup\n}\n\nint MyClass::myMethod(int param) {\n    // Method implementation\n    return 0;\n}",
                "function": "/**\n * Function description\n * @param param Description of param\n * @return Description of return value\n */\nint myFunction(int param) {\n    // Function implementation\n    return 0;\n}"
            },
            "csharp": {
                "class": "public class MyClass\n{\n    // Class fields\n    private int _myField;\n    \n    /// <summary>\n    /// Constructor\n    /// </summary>\n    public MyClass()\n    {\n        // Initialize\n    }\n    \n    /// <summary>\n    /// Method description\n    /// </summary>\n    /// <param name=\"param\">Description of param</param>\n    /// <returns>Description of return value</returns>\n    public int MyMethod(int param)\n    {\n        // Method implementation\n        return 0;\n    }\n}",
                "interface": "public interface IMyInterface\n{\n    /// <summary>\n    /// Method description\n    /// </summary>\n    /// <param name=\"param\">Description of param</param>\n    /// <returns>Description of return value</returns>\n    int MyMethod(int param);\n}"
            }
        }
        
        return templates.get(language, {})