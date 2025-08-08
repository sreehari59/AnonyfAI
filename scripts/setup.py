#!/usr/bin/env python3
"""
Setup script for PII Detection System
Helps initialize the environment and check dependencies
"""

import os
import sys
import subprocess
import platform
from pathlib import Path

def print_banner():
    """Print setup banner"""
    print("=" * 70)
    print("🔍 PII Detection System - Setup Script")
    print("=" * 70)
    print()

def check_python_version():
    """Check if Python version is compatible"""
    print("🐍 Checking Python version...")
    version = sys.version_info
    
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("❌ Python 3.8+ is required. Current version:", sys.version)
        return False
    else:
        print(f"✅ Python {version.major}.{version.minor}.{version.micro} is compatible")
        return True

def check_and_create_directories():
    """Create necessary directories"""
    print("\n📁 Creating necessary directories...")
    
    directories = [
        "logs",
        "backups", 
        "exports",
        "data",
        "temp"
    ]
    
    for directory in directories:
        dir_path = Path(directory)
        if not dir_path.exists():
            dir_path.mkdir(parents=True, exist_ok=True)
            print(f"✅ Created directory: {directory}")
        else:
            print(f"📁 Directory already exists: {directory}")

def check_env_file():
    """Check if .env file exists and help create it"""
    print("\n🔧 Checking environment configuration...")
    
    env_path = Path('.env')
    env_example_path = Path('.env.example')
    
    if not env_path.exists():
        if env_example_path.exists():
            print("⚠️  .env file not found but .env.example exists")
            
            response = input("Would you like to create .env from .env.example? (y/n): ")
            if response.lower() in ['y', 'yes']:
                try:
                    import shutil
                    shutil.copy('.env.example', '.env')
                    print("✅ Created .env file from template")
                    print("📝 Please edit .env file with your actual configuration values")
                    return True
                except Exception as e:
                    print(f"❌ Failed to copy .env.example: {e}")
                    return False
            else:
                print("⚠️  You'll need to create .env manually for full functionality")
                return False
        else:
            print("❌ Neither .env nor .env.example found")
            print("💡 Creating a basic .env file...")
            
            # Create basic .env file
            basic_env_content = """# Basic PII Detection System Configuration
ANTHROPIC_API_KEY=your_claude_api_key_here
CONNECTION_MODE=demo
LOG_LEVEL=INFO
DEBUG_MODE=false
"""
            
            try:
                with open('.env', 'w') as f:
                    f.write(basic_env_content)
                print("✅ Created basic .env file")
                print("📝 Please update with your actual API keys and configuration")
                return True
            except Exception as e:
                print(f"❌ Failed to create .env file: {e}")
                return False
    else:
        print("✅ .env file exists")
        return True

def install_dependencies():
    """Install Python dependencies"""
    print("\n📦 Installing Python dependencies...")
    
    requirements_path = Path('requirements.txt')
    if not requirements_path.exists():
        print("❌ requirements.txt not found")
        return False
    
    try:
        # Try to install dependencies
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'])
        print("✅ Dependencies installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install dependencies: {e}")
        print("💡 Try running manually: pip install -r requirements.txt")
        return False

def check_critical_dependencies():
    """Check if critical dependencies are available"""
    print("\n🔍 Checking critical dependencies...")
    
    critical_packages = [
        ('streamlit', 'Streamlit web framework'),
        ('pandas', 'Data manipulation library'),
        ('cryptography', 'Encryption library'),
        ('pyodbc', 'Database connectivity (optional)')
    ]
    
    all_good = True
    
    for package, description in critical_packages:
        try:
            __import__(package)
            print(f"✅ {package} - {description}")
        except ImportError:
            print(f"❌ {package} - {description} (MISSING)")
            if package != 'pyodbc':  # pyodbc is optional
                all_good = False
    
    return all_good

def check_ai_setup():
    """Check AI setup"""
    print("\n🤖 Checking AI configuration...")
    
    try:
        from env_config import env_config
        
        if env_config.anthropic_api_key and env_config.anthropic_api_key != 'your_claude_api_key_here':
            print("✅ Anthropic API key is configured")
            
            # Test AI connection
            try:
                from ai_assistant import AIAssistant
                ai_assistant = AIAssistant(env_config.anthropic_api_key)
                if ai_assistant.is_available():
                    print("✅ AI Assistant is ready")
                else:
                    print("⚠️  AI Assistant configured but connection test failed")
            except Exception as e:
                print(f"⚠️  AI Assistant import failed: {e}")
        else:
            print("⚠️  Anthropic API key not configured")
            print("💡 Add your Claude API key to .env file for AI features")
    except Exception as e:
        print(f"⚠️  Could not check AI configuration: {e}")

def run_system_check():
    """Run a quick system check"""
    print("\n🔧 Running system check...")
    
    # Check if we can import main modules
    modules_to_test = [
        'database_manager',
        'pii_detector', 
        'encryption_manager',
        'results_manager',
        'multi_database_manager'
    ]
    
    for module in modules_to_test:
        try:
            __import__(module)
            print(f"✅ {module}")
        except ImportError as e:
            print(f"❌ {module}: {e}")

def print_next_steps():
    """Print next steps for the user"""
    print("\n🚀 Setup Complete! Next Steps:")
    print("-" * 40)
    print("1. Configure your .env file:")
    print("   - Add your Claude API key for AI features")
    print("   - Update database credentials if using real data")
    print()
    print("2. Run the application:")
    print("   streamlit run app.py")
    print()
    print("3. Access the web interface:")
    print("   http://localhost:8501")
    print()
    print("4. Features available:")
    print("   🤖 AI-powered table discovery")
    print("   🔍 Multi-database PII scanning")
    print("   🛡️  Data encryption and masking")
    print("   📊 Comprehensive reporting")
    print("   💾 Results database storage")
    print()
    print("📚 For help, check README.md or the documentation")
    print("=" * 70)

def main():
    """Main setup function"""
    print_banner()
    
    # Run setup checks
    checks_passed = 0
    total_checks = 6
    
    if check_python_version():
        checks_passed += 1
    
    check_and_create_directories()
    checks_passed += 1
    
    if check_env_file():
        checks_passed += 1
    
    if install_dependencies():
        checks_passed += 1
    
    if check_critical_dependencies():
        checks_passed += 1
    
    check_ai_setup()
    checks_passed += 1
    
    run_system_check()
    
    print(f"\n✅ Setup completed: {checks_passed}/{total_checks} checks passed")
    
    if checks_passed >= total_checks - 1:  # Allow for optional AI setup
        print_next_steps()
    else:
        print("\n⚠️  Some setup issues detected. Please resolve them before running the application.")

if __name__ == '__main__':
    main()
