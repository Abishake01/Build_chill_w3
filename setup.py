#!/usr/bin/env python3
"""
LazAI Intelligence Hub - Setup Script
Automated setup and installation script for the LazAI Data Query application
"""

import os
import sys
import subprocess
import platform
from pathlib import Path

class LazAISetup:
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.venv_path = self.project_root / "venv"
        self.python_executable = sys.executable
        
    def print_header(self):
        """Print setup header"""
        print("🚀 LazAI Intelligence Hub - Setup")
        print("=" * 50)
        print("Automated setup for LazAI Data Query application")
        print("=" * 50)
        
    def check_python_version(self):
        """Check if Python version is compatible"""
        print("\n🐍 Checking Python version...")
        version = sys.version_info
        if version.major < 3 or (version.major == 3 and version.minor < 8):
            print(f"❌ Python 3.8+ required. Current version: {version.major}.{version.minor}")
            return False
        print(f"✅ Python {version.major}.{version.minor}.{version.micro} - Compatible")
        return True
        
    def create_virtual_environment(self):
        """Create Python virtual environment"""
        print("\n📦 Creating virtual environment...")
        
        if self.venv_path.exists():
            print("✅ Virtual environment already exists")
            return True
            
        try:
            subprocess.run([
                self.python_executable, "-m", "venv", str(self.venv_path)
            ], check=True)
            print("✅ Virtual environment created successfully")
            return True
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to create virtual environment: {e}")
            return False
            
    def get_venv_python(self):
        """Get Python executable path for virtual environment"""
        if platform.system() == "Windows":
            return self.venv_path / "Scripts" / "python.exe"
        else:
            return self.venv_path / "bin" / "python"
            
    def get_venv_pip(self):
        """Get pip executable path for virtual environment"""
        if platform.system() == "Windows":
            return self.venv_path / "Scripts" / "pip.exe"
        else:
            return self.venv_path / "bin" / "pip"
            
    def install_dependencies(self):
        """Install Python dependencies"""
        print("\n📚 Installing dependencies...")
        
        venv_python = self.get_venv_python()
        venv_pip = self.get_venv_pip()
        
        if not venv_python.exists():
            print("❌ Virtual environment Python not found")
            return False
            
        try:
            # Upgrade pip first
            print("⬆️  Upgrading pip...")
            subprocess.run([
                str(venv_python), "-m", "pip", "install", "--upgrade", "pip"
            ], check=True)
            
            # Install requirements
            print("📦 Installing requirements...")
            subprocess.run([
                str(venv_pip), "install", "-r", "requirements.txt"
            ], check=True)
            
            # Install LazAI SDK
            print("🔧 Installing LazAI SDK...")
            subprocess.run([
                str(venv_pip), "install", "alith", "-U"
            ], check=True)
            
            # Install Milvus Lite for local development
            print("🗄️  Installing Milvus Lite...")
            subprocess.run([
                str(venv_pip), "install", '"pymilvus[milvus_lite]"'
            ], check=True)
            
            print("✅ All dependencies installed successfully")
            return True
            
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to install dependencies: {e}")
            return False
            
    def create_env_file(self):
        """Create .env file from template"""
        print("\n⚙️  Setting up environment configuration...")
        
        env_file = self.project_root / ".env"
        env_template = self.project_root / "env_template.txt"
        
        if env_file.exists():
            print("✅ .env file already exists")
            return True
            
        if not env_template.exists():
            print("❌ Environment template not found")
            return False
            
        try:
            # Copy template to .env
            with open(env_template, 'r') as f:
                content = f.read()
            
            with open(env_file, 'w') as f:
                f.write(content)
                
            print("✅ .env file created from template")
            print("⚠️  Please edit .env file with your actual credentials")
            return True
            
        except Exception as e:
            print(f"❌ Failed to create .env file: {e}")
            return False
            
    def create_activation_script(self):
        """Create activation script for easy environment activation"""
        print("\n🔧 Creating activation scripts...")
        
        # Windows batch file
        if platform.system() == "Windows":
            activate_script = self.project_root / "activate.bat"
            with open(activate_script, 'w') as f:
                f.write(f"@echo off\n")
                f.write(f"call {self.venv_path}\\Scripts\\activate.bat\n")
                f.write(f"echo LazAI Intelligence Hub environment activated\n")
                f.write(f"echo Run 'python main.py' to start the server\n")
            
            print("✅ Created activate.bat for Windows")
            
        # Unix shell script
        activate_script = self.project_root / "activate.sh"
        with open(activate_script, 'w') as f:
            f.write("#!/bin/bash\n")
            f.write(f"source {self.venv_path}/bin/activate\n")
            f.write("echo 'LazAI Intelligence Hub environment activated'\n")
            f.write("echo 'Run \"python main.py\" to start the server'\n")
        
        # Make executable
        os.chmod(activate_script, 0o755)
        print("✅ Created activate.sh for Unix systems")
        
    def run_tests(self):
        """Run basic tests to verify installation"""
        print("\n🧪 Running installation tests...")
        
        venv_python = self.get_venv_python()
        
        try:
            # Test imports
            test_script = """
import sys
print(f"Python path: {sys.executable}")

try:
    import fastapi
    print("✅ FastAPI imported successfully")
except ImportError as e:
    print(f"❌ FastAPI import failed: {e}")

try:
    import uvicorn
    print("✅ Uvicorn imported successfully")
except ImportError as e:
    print(f"❌ Uvicorn import failed: {e}")

try:
    import requests
    print("✅ Requests imported successfully")
except ImportError as e:
    print(f"❌ Requests import failed: {e}")

try:
    import dotenv
    print("✅ Python-dotenv imported successfully")
except ImportError as e:
    print(f"❌ Python-dotenv import failed: {e}")

print("✅ Basic imports test completed")
"""
            
            result = subprocess.run([
                str(venv_python), "-c", test_script
            ], capture_output=True, text=True)
            
            print(result.stdout)
            if result.stderr:
                print("Warnings:", result.stderr)
                
            return result.returncode == 0
            
        except Exception as e:
            print(f"❌ Test failed: {e}")
            return False
            
    def print_next_steps(self):
        """Print next steps for the user"""
        print("\n🎉 Setup completed successfully!")
        print("\n📋 Next Steps:")
        print("1. Edit .env file with your credentials:")
        print("   - PRIVATE_KEY: Your wallet private key")
        print("   - RSA_PRIVATE_KEY_BASE64: Your RSA private key")
        print("   - Optional: OPENAI_API_KEY, LLM_API_KEY, etc.")
        
        print("\n2. Activate the virtual environment:")
        if platform.system() == "Windows":
            print("   activate.bat")
        else:
            print("   source activate.sh")
            print("   # or")
            print("   source venv/bin/activate")
        
        print("\n3. Start the server:")
        print("   python main.py")
        
        print("\n4. Access the application:")
        print("   - Web UI: http://localhost:8000/ui")
        print("   - API Docs: http://localhost:8000/docs")
        print("   - Health Check: http://localhost:8000/health")
        
        print("\n5. Run the demo:")
        print("   python lazai_client.py --mode demo")
        
        print("\n📚 Documentation:")
        print("   - README.md: Complete setup and usage guide")
        print("   - lazai_client.py: Interactive client for testing")
        print("   - demo.py: Comprehensive demonstration script")
        
    def run_setup(self):
        """Run the complete setup process"""
        self.print_header()
        
        # Check Python version
        if not self.check_python_version():
            return False
            
        # Create virtual environment
        if not self.create_virtual_environment():
            return False
            
        # Install dependencies
        if not self.install_dependencies():
            return False
            
        # Create environment file
        if not self.create_env_file():
            return False
            
        # Create activation scripts
        self.create_activation_script()
        
        # Run tests
        if not self.run_tests():
            print("⚠️  Some tests failed, but setup may still work")
            
        # Print next steps
        self.print_next_steps()
        
        return True

def main():
    """Main setup function"""
    setup = LazAISetup()
    success = setup.run_setup()
    
    if success:
        print("\n🎊 Setup completed successfully!")
        sys.exit(0)
    else:
        print("\n❌ Setup failed. Please check the errors above.")
        sys.exit(1)

if __name__ == "__main__":
    main()
