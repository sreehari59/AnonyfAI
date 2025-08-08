#!/usr/bin/env python3
"""
PII Detection System - Streamlit Runner
Run this script to start the Streamlit application
"""

import subprocess
import sys
import os

def main():
    # Set up the environment
    script_dir = os.path.dirname(os.path.abspath(__file__))
    src_dir = os.path.join(script_dir, 'src')
    core_dir = os.path.join(src_dir, 'core')
    database_dir = os.path.join(src_dir, 'database')
    ui_dir = os.path.join(src_dir, 'ui')
    app_path = os.path.join(ui_dir, 'app.py')
    
    # Add all necessary paths to Python path
    env = os.environ.copy()
    python_paths = [src_dir, core_dir, database_dir, ui_dir]
    
    if 'PYTHONPATH' in env:
        env['PYTHONPATH'] = os.pathsep.join(python_paths) + os.pathsep + env['PYTHONPATH']
    else:
        env['PYTHONPATH'] = os.pathsep.join(python_paths)
    
    # Run streamlit
    cmd = [sys.executable, '-m', 'streamlit', 'run', app_path]
    print(f"Starting PII Detection System...")
    print(f"Running: {' '.join(cmd)}")
    
    try:
        subprocess.run(cmd, env=env, check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error running application: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
