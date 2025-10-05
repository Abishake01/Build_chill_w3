#!/usr/bin/env python3
"""
LazAI Intelligence Hub - Complete Demonstration
This script demonstrates all features of the LazAI Data Query application
"""

import os
import sys
import time
import subprocess
import requests
import json
from pathlib import Path

class LazAIDemo:
    def __init__(self):
        self.base_url = "http://localhost:8000"
        self.server_process = None
        
    def print_banner(self):
        """Print demo banner"""
        print("🚀 LazAI Intelligence Hub - Complete Demonstration")
        print("=" * 60)
        print("Privacy-Preserving Data Query Application")
        print("Built with LazAI SDK and FastAPI")
        print("=" * 60)
        
    def print_section(self, title: str):
        """Print section header"""
        print(f"\n🎯 {title}")
        print("-" * 40)
        
    def check_environment(self):
        """Check if environment is properly set up"""
        self.print_section("Environment Check")
        
        # Check if .env file exists
        env_file = Path(".env")
        if not env_file.exists():
            print("⚠️  .env file not found. Please run setup.py first.")
            return False
            
        print("✅ .env file found")
        
        # Check if virtual environment exists
        venv_path = Path("venv")
        if not venv_path.exists():
            print("⚠️  Virtual environment not found. Please run setup.py first.")
            return False
            
        print("✅ Virtual environment found")
        
        # Check if main.py exists
        if not Path("main.py").exists():
            print("❌ main.py not found")
            return False
            
        print("✅ Application files found")
        return True
        
    def start_server(self):
        """Start the FastAPI server"""
        self.print_section("Starting Server")
        
        try:
            # Get Python executable from venv
            if os.name == 'nt':  # Windows
                python_exe = Path("venv/Scripts/python.exe")
            else:  # Unix-like
                python_exe = Path("venv/bin/python")
                
            if not python_exe.exists():
                print("❌ Virtual environment Python not found")
                return False
                
            print("🚀 Starting LazAI server...")
            self.server_process = subprocess.Popen([
                str(python_exe), "main.py", "--host", "0.0.0.0", "--port", "8000"
            ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            
            # Wait for server to start
            print("⏳ Waiting for server to start...")
            time.sleep(8)
            
            # Test server
            try:
                response = requests.get(f"{self.base_url}/health", timeout=10)
                if response.status_code == 200:
                    print("✅ Server started successfully")
                    return True
                else:
                    print(f"❌ Server health check failed: {response.status_code}")
                    return False
            except requests.exceptions.RequestException as e:
                print(f"❌ Server not responding: {e}")
                return False
                
        except Exception as e:
            print(f"❌ Failed to start server: {e}")
            return False
            
    def stop_server(self):
        """Stop the server"""
        if self.server_process:
            print("\n🛑 Stopping server...")
            self.server_process.terminate()
            self.server_process.wait()
            print("✅ Server stopped")
            
    def test_basic_functionality(self):
        """Test basic functionality"""
        self.print_section("Testing Basic Functionality")
        
        try:
            # Test health endpoint
            response = requests.get(f"{self.base_url}/health")
            if response.status_code == 200:
                print("✅ Health check passed")
            else:
                print(f"❌ Health check failed: {response.status_code}")
                return False
                
            # Test demo query
            payload = {"query": "What are my main skills?"}
            response = requests.post(f"{self.base_url}/demo/query", json=payload)
            
            if response.status_code == 200:
                data = response.json()
                if "data" in data and len(data["data"]) > 0:
                    print("✅ Demo query successful")
                    print(f"   Results: {len(data['data'])} items")
                else:
                    print("❌ Demo query returned no data")
                    return False
            else:
                print(f"❌ Demo query failed: {response.status_code}")
                return False
                
            return True
            
        except Exception as e:
            print(f"❌ Basic functionality test failed: {e}")
            return False
            
    def test_advanced_features(self):
        """Test advanced features"""
        self.print_section("Testing Advanced Features")
        
        try:
            # Test local query
            sample_content = """
            I am a passionate developer with expertise in Python, Django, React, and AI technologies.
            I love building full-stack applications and have experience with Web3 and blockchain development.
            My interests include machine learning, voice-based AI systems, and teaching programming.
            """
            
            payload = {
                "content": sample_content,
                "query": "What technologies and skills are mentioned?",
                "collection": "demo_collection"
            }
            
            response = requests.post(f"{self.base_url}/query/local", json=payload)
            
            if response.status_code == 200:
                data = response.json()
                if "data" in data:
                    print("✅ Local query successful")
                    print(f"   Results: {len(data['data'])} items")
                else:
                    print("❌ Local query returned no data")
                    return False
            else:
                print(f"❌ Local query failed: {response.status_code}")
                return False
                
            # Test analytics trends
            response = requests.get(f"{self.base_url}/analytics/trends")
            
            if response.status_code == 200:
                data = response.json()
                if "popular_queries" in data:
                    print("✅ Analytics trends successful")
                    print(f"   Trends: {len(data['popular_queries'])} items")
                else:
                    print("❌ Analytics trends returned no data")
                    return False
            else:
                print(f"❌ Analytics trends failed: {response.status_code}")
                return False
                
            return True
            
        except Exception as e:
            print(f"❌ Advanced features test failed: {e}")
            return False
            
    def test_web_interface(self):
        """Test web interface"""
        self.print_section("Testing Web Interface")
        
        try:
            response = requests.get(f"{self.base_url}/ui")
            
            if response.status_code == 200:
                content = response.text
                if "LazAI Intelligence Hub" in content:
                    print("✅ Web interface accessible")
                    print("   URL: http://localhost:8000/ui")
                else:
                    print("❌ Web interface content not found")
                    return False
            else:
                print(f"❌ Web interface failed: {response.status_code}")
                return False
                
            return True
            
        except Exception as e:
            print(f"❌ Web interface test failed: {e}")
            return False
            
    def run_interactive_demo(self):
        """Run interactive demo"""
        self.print_section("Interactive Demo")
        
        print("🎮 Interactive demo mode")
        print("You can now test the application interactively:")
        print("1. Open http://localhost:8000/ui in your browser")
        print("2. Try the chat interface")
        print("3. Upload files and test queries")
        print("4. Explore the analytics dashboard")
        print("\nPress Ctrl+C to stop the demo")
        
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n👋 Demo stopped by user")
            
    def print_summary(self, success: bool):
        """Print demo summary"""
        self.print_section("Demo Summary")
        
        if success:
            print("🎉 Demo completed successfully!")
            print("\n📋 What you've seen:")
            print("✅ LazAI Data Query server running")
            print("✅ Privacy-preserving data queries")
            print("✅ AI-powered analytics and insights")
            print("✅ Interactive web interface")
            print("✅ Multiple query modes (RAG, Local, Demo)")
            print("✅ Real-time analytics dashboard")
            
            print("\n🚀 Next steps:")
            print("1. Configure your .env file with LazAI credentials")
            print("2. Register your server with LazAI admins")
            print("3. Upload your encrypted data files")
            print("4. Start querying your private data!")
            
            print("\n📚 Resources:")
            print("- README.md: Complete documentation")
            print("- lazai_client.py: Interactive client")
            print("- test_application.py: Comprehensive tests")
            print("- setup.py: Automated setup")
            
        else:
            print("❌ Demo encountered issues")
            print("Please check the errors above and try again")
            
    def run_complete_demo(self):
        """Run the complete demonstration"""
        self.print_banner()
        
        # Check environment
        if not self.check_environment():
            print("\n❌ Environment check failed. Please run setup.py first.")
            return False
            
        # Start server
        if not self.start_server():
            print("\n❌ Failed to start server")
            return False
            
        try:
            # Run tests
            tests = [
                ("Basic Functionality", self.test_basic_functionality),
                ("Advanced Features", self.test_advanced_features),
                ("Web Interface", self.test_web_interface)
            ]
            
            passed = 0
            total = len(tests)
            
            for test_name, test_func in tests:
                try:
                    success = test_func()
                    if success:
                        passed += 1
                        print(f"✅ {test_name} - PASSED")
                    else:
                        print(f"❌ {test_name} - FAILED")
                except Exception as e:
                    print(f"❌ {test_name} - ERROR: {e}")
                    
            # Print results
            print(f"\n📊 Test Results: {passed}/{total} passed")
            
            if passed == total:
                print("\n🎊 All tests passed! Starting interactive demo...")
                self.run_interactive_demo()
                return True
            else:
                print(f"\n⚠️  {total - passed} tests failed. Check the details above.")
                return False
                
        finally:
            # Stop server
            self.stop_server()
            
    def run_quick_demo(self):
        """Run a quick demonstration without interactive mode"""
        self.print_banner()
        
        if not self.check_environment():
            return False
            
        if not self.start_server():
            return False
            
        try:
            success = (self.test_basic_functionality() and 
                      self.test_advanced_features() and 
                      self.test_web_interface())
            
            self.print_summary(success)
            return success
            
        finally:
            self.stop_server()

def main():
    """Main function"""
    import argparse
    
    parser = argparse.ArgumentParser(description="LazAI Intelligence Hub Demo")
    parser.add_argument("--mode", choices=["full", "quick"], default="full",
                       help="Demo mode: full (interactive) or quick")
    
    args = parser.parse_args()
    
    demo = LazAIDemo()
    
    if args.mode == "full":
        success = demo.run_complete_demo()
    else:
        success = demo.run_quick_demo()
        
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())
