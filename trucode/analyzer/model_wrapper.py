import os
import json
import tempfile

class ModelWrapper:
    """Wrapper for AI model to analyze code."""
    
    def __init__(self):
        """Initialize the model wrapper."""
        self.model = None
        self.loaded = False
        self.model_name = "Salesforce/codegen-350M-mono"
        self.cache_dir = os.path.join(tempfile.gettempdir(), "trucode_model_cache")
        
        # Create cache directory if it doesn't exist
        if not os.path.exists(self.cache_dir):
            try:
                os.makedirs(self.cache_dir)
            except Exception as e:
                print(f"Could not create cache directory: {e}")
    
    def load_model(self):
        """Load the model if not already loaded."""
        if not self.loaded:
            try:
                print(f"Loading model {self.model_name}... (this may take a minute)")
                
                # Try importing transformers
                try:
                    from transformers import pipeline
                    # Use "cpu" to ensure it works on all systems
                    self.model = pipeline("text-generation", model=self.model_name, device="cpu")
                    self.loaded = True
                    print("Model loaded successfully!")
                except ImportError:
                    print("Transformers library not found. Falling back to rule-based analysis only.")
                    return False
                except Exception as e:
                    print(f"Error loading model: {e}")
                    print("Falling back to rule-based analysis only.")
                    return False
            except Exception as e:
                print(f"Error loading model: {e}")
                print("Falling back to rule-based analysis only.")
                return False
        return self.loaded
    
    def analyze_code(self, code_snippet):
        """
        Analyze code using the AI model.
        
        Args:
            code_snippet: Python code as a string
            
        Returns:
            Dictionary with analysis results
        """
        if not self.load_model():
            # Return basic analysis if model couldn't be loaded
            return {
                "description": "Basic code analysis (AI model not available)",
                "suggestions": [
                    "Consider adding comments to explain complex logic",
                    "Add error handling for robust code",
                    "Break down large functions into smaller ones"
                ]
            }
        
        # Create a cache key from the first 100 chars of the code
        cache_key = hash(code_snippet[:100])
        cache_file = os.path.join(self.cache_dir, f"analysis_{cache_key}.json")
        
        # Check if we have a cached result
        if os.path.exists(cache_file):
            try:
                with open(cache_file, 'r') as f:
                    return json.load(f)
            except Exception:
                # If reading cache fails, proceed with analysis
                pass
        
        try:
            # Construct prompt for the model
            prompt = f"""
            Analyze this Python code and identify issues, improvements, or bugs:
            
            ```python
            {code_snippet[:500]}  # Limit code to avoid token limits
            ```
            
            Analysis:
            """
            
            # Generate response
            result = self.model(
                prompt, 
                max_length=200, 
                num_return_sequences=1, 
                temperature=0.5
            )
            
            # Extract generated text and process it
            generated_text = result[0]['generated_text']
            analysis_part = generated_text.split("Analysis:")[-1].strip()
            
            # Split into lines for easier processing
            lines = [line.strip() for line in analysis_part.split("\n") if line.strip()]
            
            # Extract suggestions
            suggestions = []
            for line in lines:
                # Look for lines that might be suggestions
                if line.startswith("-") or line.startswith("*"):
                    suggestions.append(line[1:].strip())
                elif "should" in line or "could" in line or "consider" in line:
                    suggestions.append(line)
            
            result = {
                "description": "AI-powered code analysis",
                "full_analysis": analysis_part,
                "suggestions": suggestions[:3]  # Limit to top 3 suggestions
            }
            
            # Cache the result
            try:
                with open(cache_file, 'w') as f:
                    json.dump(result, f)
            except Exception as e:
                print(f"Could not cache analysis result: {e}")
                
            return result
            
        except Exception as e:
            print(f"Error during AI analysis: {e}")
            return {
                "description": "Error during AI analysis",
                "suggestions": [
                    "Add proper error handling",
                    "Ensure code follows PEP 8 style guidelines",
                    "Consider adding unit tests"
                ]
            }