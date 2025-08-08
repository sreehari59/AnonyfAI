"""
Quick Installation Script for PII Detection System
Run this script to install all required packages
"""

import subprocess
import sys
import os

def install_package(package):
    """Install a package using pip"""
    try:
        print(f"Installing {package}...")
        result = subprocess.run([sys.executable, "-m", "pip", "install", package], 
                              capture_output=True, text=True, check=True)
        print(f"✅ {package} installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install {package}: {e}")
        return False

def check_package(package):
    """Check if a package is already installed"""
    try:
        __import__(package.split('==')[0])
        print(f"✅ {package} is already installed")
        return True
    except ImportError:
        return False

def main():
    """Main installation function"""
    print("🔒 PII Detection System - Package Installer")
    print("=" * 50)
    
    # Required packages
    packages = [
        "pyodbc",
        "pandas", 
        "streamlit",
        "plotly",
    ]
    
    # Optional packages
    optional_packages = [
        "spacy"
    ]
    
    print("\n📦 Installing required packages...")
    
    failed_packages = []
    
    for package in packages:
        if not check_package(package):
            if not install_package(package):
                failed_packages.append(package)
        
    print("\n📦 Installing optional packages...")
    
    for package in optional_packages:
        if not check_package(package):
            install_package(package)  # Don't fail on optional packages
    
    # Try to download spacy model
    print("\n🧠 Downloading spaCy model (optional)...")
    try:
        subprocess.run([sys.executable, "-m", "spacy", "download", "en_core_web_sm"], 
                      capture_output=True, text=True, check=True)
        print("✅ spaCy model downloaded successfully")
    except:
        print("⚠️ spaCy model download failed (optional)")
    
    print("\n" + "=" * 50)
    
    if failed_packages:
        print("❌ Installation completed with errors:")
        for pkg in failed_packages:
            print(f"  - {pkg}")
        print("\n💡 Try installing manually: pip install " + " ".join(failed_packages))
    else:
        print("✅ All packages installed successfully!")
    
    print("\n🚀 Next steps:")
    print("1. Run: python test_connections.py (to test database connections)")
    print("2. Run: streamlit run app.py (to start the application)")
    
    print("\n🔗 Installation Guide: See installation_guide.md for ODBC driver links")

if __name__ == "__main__":
    main()
