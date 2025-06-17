import os
import sys
from dotenv import load_dotenv

def check_python_version():
    """Check if Python version is compatible."""
    print(" Checking Python version...")
    version = sys.version_info
    if version.major >= 3 and version.minor >= 8:
        print(f" Python {version.major}.{version.minor}.{version.micro} - Compatible")
        return True
    else:
        print(f" Python {version.major}.{version.minor}.{version.micro} - Requires Python 3.8+")
        return False

def check_dependencies():
    """Check if all required packages are installed."""
    print("\n Checking dependencies...")
    required_packages = [
        'streamlit',
        'PyPDF2',
        'google.generativeai',
        'tiktoken',
        'sklearn',
        'numpy',
        'python-dotenv'
    ]
    
    missing_packages = []
    for package in required_packages:
        try:
            if package == 'sklearn':
                __import__('sklearn')
            elif package == 'google.generativeai':
                __import__('google.generativeai')
            elif package == 'python-dotenv':
                __import__('dotenv')
            else:
                __import__(package)
            print(f" {package}")
        except ImportError:
            print(f" {package}")
            missing_packages.append(package)
    
    return len(missing_packages) == 0, missing_packages

def check_environment_variables():
    """Check if environment variables are set."""
    print("\n Checking environment variables...")
    load_dotenv()
    
    api_key = os.getenv('GEMINI_API_KEY')
    if api_key and api_key != 'your_gemini_api_key_here':
        print("✅ GEMINI_API_KEY is set")
        return True
    else:
        print(" GEMINI_API_KEY is not set or using default value")
        print("   Please set your Gemini API key in the .env file")
        return False

def check_gemini_api():
    """Test Gemini API connection."""
    print("\n Testing Gemini API connection...")
    try:
        import google.generativeai as genai
        api_key = os.getenv('GEMINI_API_KEY')
        
        if not api_key or api_key == 'your_gemini_api_key_here':
            print("API key not configured")
            return False
            
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content("Hello, this is a test.")
        
        if response.text:
            print(" Gemini API connection successful")
            return True
        else:
            print(" Gemini API returned empty response")
            return False
            
    except Exception as e:
        print(f" Gemini API connection failed: {str(e)}")
        return False

def main():
    """Run all environment checks."""
    print(" Multi-PDF Chatbot Environment Check")
    print("=" * 50)
    
    checks = [
        check_python_version(),
        check_dependencies()[0],
        check_environment_variables(),
        check_gemini_api()
    ]
    
    print("\n" + "=" * 50)
    if all(checks):
        print(" All checks passed! Your environment is ready.")
        print("Run 'python run_app.py' to start the application.")
    else:
        print("Some checks failed. Please fix the issues above.")
        
        _, missing = check_dependencies()
        if missing:
            print(f"\nTo install missing packages, run:")
            print(f"pip install {' '.join(missing)}")

if __name__ == "__main__":
    main()