#!/usr/bin/env python3
"""
Setup script for SQLCoder Text-to-SQL application
Automates the complete setup process
"""

import subprocess
import sys
import os
from pathlib import Path
import shutil

def run_command(command, cwd=None, check=True):
    """Run a system command"""
    print(f"Running: {command}")
    try:
        result = subprocess.run(
            command, 
            shell=True, 
            cwd=cwd, 
            check=check,
            capture_output=True,
            text=True
        )
        if result.stdout:
            print(result.stdout)
        return result.returncode == 0
    except subprocess.CalledProcessError as e:
        print(f"Error running command: {e}")
        if e.stderr:
            print(e.stderr)
        return False

def check_python_version():
    """Check if Python version is compatible"""
    version = sys.version_info
    if version.major != 3 or version.minor < 8:
        print("❌ Python 3.8 or higher is required")
        return False
    print(f"✅ Python {version.major}.{version.minor}.{version.micro} detected")
    return True

def setup_virtual_environment():
    """Create and activate virtual environment"""
    print("\n🔧 Setting up virtual environment...")

    venv_path = Path("venv")
    if venv_path.exists():
        print("Virtual environment already exists")
        return True

    # Create virtual environment
    if not run_command(f"{sys.executable} -m venv venv"):
        print("❌ Failed to create virtual environment")
        return False

    print("✅ Virtual environment created")
    return True

def install_dependencies():
    """Install Python dependencies"""
    print("\n📦 Installing dependencies...")

    # Determine pip path
    if os.name == 'nt':  # Windows
        pip_path = "venv/Scripts/pip"
        python_path = "venv/Scripts/python"
    else:  # Unix/Linux/macOS
        pip_path = "venv/bin/pip"
        python_path = "venv/bin/python"

    # Upgrade pip
    if not run_command(f"{python_path} -m pip install --upgrade pip"):
        print("❌ Failed to upgrade pip")
        return False

    # Install main requirements
    if not run_command(f"{pip_path} install -r requirements.txt"):
        print("❌ Failed to install requirements")
        return False

    # Try to install SQLCoder (may fail if not available)
    print("\n🤖 Installing SQLCoder...")
    sqlcoder_success = run_command(f"{pip_path} install 'sqlcoder[transformers]'", check=False)
    if not sqlcoder_success:
        print("⚠️  SQLCoder installation failed. You may need to install it manually.")
        print("   Run: pip install 'sqlcoder[transformers]'")
    else:
        print("✅ SQLCoder installed successfully")

    print("✅ Dependencies installed")
    return True

def initialize_database():
    """Initialize the database"""
    print("\n🗃️ Initializing database...")

    # Change to database directory and run init script
    db_dir = Path("database")
    if not db_dir.exists():
        print("❌ Database directory not found")
        return False

    # Determine python path
    if os.name == 'nt':  # Windows
        python_path = "../venv/Scripts/python"
    else:  # Unix/Linux/macOS
        python_path = "../venv/bin/python"

    # Run database initialization
    if not run_command(f"{python_path} init_db.py --force --test", cwd=db_dir):
        print("❌ Failed to initialize database")
        return False

    print("✅ Database initialized successfully")
    return True

def create_startup_scripts():
    """Create startup scripts for easy execution"""
    print("\n📝 Creating startup scripts...")

    # Determine script extensions and paths
    if os.name == 'nt':  # Windows
        backend_script = "start_backend.bat"
        frontend_script = "start_frontend.bat"
        python_path = "venv\\Scripts\\python"
        streamlit_path = "venv\\Scripts\\streamlit"

        backend_content = f"""@echo off
echo Starting SQLCoder Backend API...
cd backend
{python_path} main.py
pause
"""

        frontend_content = f"""@echo off
echo Starting SQLCoder Frontend...
cd frontend
{streamlit_path} run app.py
pause
"""
    else:  # Unix/Linux/macOS
        backend_script = "start_backend.sh"
        frontend_script = "start_frontend.sh"
        python_path = "venv/bin/python"
        streamlit_path = "venv/bin/streamlit"

        backend_content = f"""#!/bin/bash
echo "Starting SQLCoder Backend API..."
cd backend
{python_path} main.py
"""

        frontend_content = f"""#!/bin/bash
echo "Starting SQLCoder Frontend..."
cd frontend
{streamlit_path} run app.py
"""

    # Write backend script
    with open(backend_script, 'w') as f:
        f.write(backend_content)

    # Write frontend script
    with open(frontend_script, 'w') as f:
        f.write(frontend_content)

    # Make scripts executable on Unix-like systems
    if os.name != 'nt':
        os.chmod(backend_script, 0o755)
        os.chmod(frontend_script, 0o755)

    print(f"✅ Created {backend_script} and {frontend_script}")
    return True

def main():
    """Main setup function"""
    print("🚀 SQLCoder Text-to-SQL Application Setup")
    print("=" * 50)

    # Check Python version
    if not check_python_version():
        return False

    # Setup virtual environment
    if not setup_virtual_environment():
        return False

    # Install dependencies
    if not install_dependencies():
        return False

    # Initialize database
    if not initialize_database():
        return False

    # Create startup scripts
    if not create_startup_scripts():
        return False

    print("\n" + "=" * 50)
    print("✅ Setup completed successfully!")
    print("\n📖 Next steps:")
    print("1. Activate the virtual environment:")
    if os.name == 'nt':
        print("   venv\\Scripts\\activate")
        print("2. Start the backend: start_backend.bat")
        print("3. Start the frontend: start_frontend.bat")
    else:
        print("   source venv/bin/activate")
        print("2. Start the backend: ./start_backend.sh")
        print("3. Start the frontend: ./start_frontend.sh")

    print("4. Open http://localhost:8501 in your browser")
    print("\n🎉 Happy querying with SQLCoder!")
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
