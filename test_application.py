#!/usr/bin/env python3
"""
LazAI Intelligence Hub - Application Test Suite
Comprehensive testing script for the LazAI Data Query application
"""

import requests
import json
import time
import sys
from typing import Dict, Any, List
import subprocess
import threading
import os

class LazAITestSuite:
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.session = requests.Session()
        self.test_results = []
        self.server_process = None
        
    def print_test_header(self, test_name: str):
        """Print test header"""
        print(f"\n🧪 {test_name}")
        print("-" * 50)
        
    def print_test_result(self, test_name: str, success: bool, message: str = ""):
        """Print test result"""
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}")
        if message:
            print(f"   {message}")
        
        self.test_results.append({
            "test": test_name,
            "success": success,
            "message": message
        })
        
    def start_server(self):
        """Start the FastAPI server in background"""
        print("🚀 Starting LazAI server...")
        try:
            # Start server in background
            self.server_process = subprocess.Popen([
                sys.executable, "main.py", "--host", "0.0.0.0", "--port", "8000"
            ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            
            # Wait for server to start
            print("⏳ Waiting for server to start...")
            time.sleep(5)
            
            # Check if server is running
            try:
                response = requests.get(f"{self.base_url}/health", timeout=5)
                if response.status_code == 200:
                    print("✅ Server started successfully")
                    return True
                else:
                    print(f"❌ Server health check failed: {response.status_code}")
                    return False
            except requests.exceptions.RequestException:
                print("❌ Server not responding")
                return False
                
        except Exception as e:
            print(f"❌ Failed to start server: {e}")
            return False
            
    def stop_server(self):
        """Stop the FastAPI server"""
        if self.server_process:
            print("🛑 Stopping server...")
            self.server_process.terminate()
            self.server_process.wait()
            print("✅ Server stopped")
            
    def test_health_endpoint(self):
        """Test health check endpoint"""
        self.print_test_header("Health Check")
        try:
            response = self.session.get(f"{self.base_url}/health")
            if response.status_code == 200:
                data = response.json()
                self.print_test_result("Health Check", True, f"Status: {data.get('status')}")
                return True
            else:
                self.print_test_result("Health Check", False, f"HTTP {response.status_code}")
                return False
        except Exception as e:
            self.print_test_result("Health Check", False, str(e))
            return False
            
    def test_root_endpoint(self):
        """Test root endpoint"""
        self.print_test_header("Root Endpoint")
        try:
            response = self.session.get(f"{self.base_url}/")
            if response.status_code == 200:
                data = response.json()
                self.print_test_result("Root Endpoint", True, f"Message: {data.get('message')}")
                return True
            else:
                self.print_test_result("Root Endpoint", False, f"HTTP {response.status_code}")
                return False
        except Exception as e:
            self.print_test_result("Root Endpoint", False, str(e))
            return False
            
    def test_demo_query(self):
        """Test demo query endpoint"""
        self.print_test_header("Demo Query")
        try:
            payload = {"query": "What are my main skills?"}
            response = self.session.post(f"{self.base_url}/demo/query", json=payload)
            
            if response.status_code == 200:
                data = response.json()
                if "data" in data and len(data["data"]) > 0:
                    self.print_test_result("Demo Query", True, f"Returned {len(data['data'])} results")
                    return True
                else:
                    self.print_test_result("Demo Query", False, "No data returned")
                    return False
            else:
                self.print_test_result("Demo Query", False, f"HTTP {response.status_code}")
                return False
        except Exception as e:
            self.print_test_result("Demo Query", False, str(e))
            return False
            
    def test_local_query(self):
        """Test local query endpoint"""
        self.print_test_header("Local Query")
        try:
            sample_content = "I am a developer with expertise in Python, AI, and Web3 technologies."
            payload = {
                "content": sample_content,
                "query": "What technologies are mentioned?",
                "collection": "test_collection"
            }
            response = self.session.post(f"{self.base_url}/query/local", json=payload)
            
            if response.status_code == 200:
                data = response.json()
                if "data" in data:
                    self.print_test_result("Local Query", True, f"Returned {len(data['data'])} results")
                    return True
                else:
                    self.print_test_result("Local Query", False, "No data returned")
                    return False
            else:
                self.print_test_result("Local Query", False, f"HTTP {response.status_code}")
                return False
        except Exception as e:
            self.print_test_result("Local Query", False, str(e))
            return False
            
    def test_analytics_trends(self):
        """Test analytics trends endpoint"""
        self.print_test_header("Analytics Trends")
        try:
            response = self.session.get(f"{self.base_url}/analytics/trends")
            
            if response.status_code == 200:
                data = response.json()
                if "popular_queries" in data:
                    self.print_test_result("Analytics Trends", True, f"Returned {len(data['popular_queries'])} trends")
                    return True
                else:
                    self.print_test_result("Analytics Trends", False, "Invalid response format")
                    return False
            else:
                self.print_test_result("Analytics Trends", False, f"HTTP {response.status_code}")
                return False
        except Exception as e:
            self.print_test_result("Analytics Trends", False, str(e))
            return False
            
    def test_web_interface(self):
        """Test web interface accessibility"""
        self.print_test_header("Web Interface")
        try:
            response = self.session.get(f"{self.base_url}/ui")
            
            if response.status_code == 200:
                content = response.text
                if "LazAI Intelligence Hub" in content:
                    self.print_test_result("Web Interface", True, "UI loaded successfully")
                    return True
                else:
                    self.print_test_result("Web Interface", False, "UI content not found")
                    return False
            else:
                self.print_test_result("Web Interface", False, f"HTTP {response.status_code}")
                return False
        except Exception as e:
            self.print_test_result("Web Interface", False, str(e))
            return False
            
    def test_multiple_queries(self):
        """Test multiple queries to simulate real usage"""
        self.print_test_header("Multiple Queries")
        queries = [
            "What are my skills?",
            "What technologies do I use?",
            "Summarize my background",
            "What are my interests?"
        ]
        
        success_count = 0
        for i, query in enumerate(queries, 1):
            try:
                payload = {"query": query}
                response = self.session.post(f"{self.base_url}/demo/query", json=payload)
                
                if response.status_code == 200:
                    data = response.json()
                    if "data" in data:
                        success_count += 1
                        print(f"   Query {i}: ✅ Success")
                    else:
                        print(f"   Query {i}: ❌ No data")
                else:
                    print(f"   Query {i}: ❌ HTTP {response.status_code}")
                    
                time.sleep(0.5)  # Rate limiting
                
            except Exception as e:
                print(f"   Query {i}: ❌ Error: {e}")
        
        success_rate = (success_count / len(queries)) * 100
        self.print_test_result("Multiple Queries", success_count > 0, 
                             f"{success_count}/{len(queries)} queries successful ({success_rate:.1f}%)")
        return success_count > 0
        
    def test_error_handling(self):
        """Test error handling"""
        self.print_test_header("Error Handling")
        
        # Test invalid query
        try:
            payload = {"query": ""}  # Empty query
            response = self.session.post(f"{self.base_url}/demo/query", json=payload)
            
            if response.status_code == 400:
                self.print_test_result("Error Handling", True, "Properly handles empty query")
                return True
            else:
                self.print_test_result("Error Handling", False, f"Unexpected status: {response.status_code}")
                return False
        except Exception as e:
            self.print_test_result("Error Handling", False, str(e))
            return False
            
    def test_performance(self):
        """Test basic performance metrics"""
        self.print_test_header("Performance Test")
        
        try:
            start_time = time.time()
            payload = {"query": "What are my main skills?"}
            response = self.session.post(f"{self.base_url}/demo/query", json=payload)
            end_time = time.time()
            
            response_time = (end_time - start_time) * 1000  # Convert to milliseconds
            
            if response.status_code == 200 and response_time < 5000:  # Less than 5 seconds
                self.print_test_result("Performance Test", True, f"Response time: {response_time:.0f}ms")
                return True
            else:
                self.print_test_result("Performance Test", False, 
                                     f"Response time: {response_time:.0f}ms (too slow)")
                return False
        except Exception as e:
            self.print_test_result("Performance Test", False, str(e))
            return False
            
    def run_all_tests(self):
        """Run all tests"""
        print("🚀 LazAI Intelligence Hub - Test Suite")
        print("=" * 60)
        
        # Start server
        if not self.start_server():
            print("❌ Cannot run tests without server")
            return False
            
        try:
            # Run all tests
            tests = [
                ("Health Check", self.test_health_endpoint),
                ("Root Endpoint", self.test_root_endpoint),
                ("Demo Query", self.test_demo_query),
                ("Local Query", self.test_local_query),
                ("Analytics Trends", self.test_analytics_trends),
                ("Web Interface", self.test_web_interface),
                ("Multiple Queries", self.test_multiple_queries),
                ("Error Handling", self.test_error_handling),
                ("Performance", self.test_performance)
            ]
            
            passed = 0
            total = len(tests)
            
            for test_name, test_func in tests:
                try:
                    success = test_func()
                    if success:
                        passed += 1
                except Exception as e:
                    print(f"❌ {test_name} - Exception: {e}")
            
            # Print summary
            print(f"\n📊 Test Summary")
            print("=" * 30)
            print(f"Total Tests: {total}")
            print(f"Passed: {passed}")
            print(f"Failed: {total - passed}")
            print(f"Success Rate: {(passed/total)*100:.1f}%")
            
            if passed == total:
                print("\n🎉 All tests passed! Application is working correctly.")
            else:
                print(f"\n⚠️  {total - passed} tests failed. Check the details above.")
                
            return passed == total
            
        finally:
            # Stop server
            self.stop_server()
            
    def generate_report(self):
        """Generate test report"""
        report = {
            "timestamp": time.time(),
            "total_tests": len(self.test_results),
            "passed_tests": len([r for r in self.test_results if r["success"]]),
            "failed_tests": len([r for r in self.test_results if not r["success"]]),
            "success_rate": (len([r for r in self.test_results if r["success"]]) / len(self.test_results)) * 100,
            "results": self.test_results
        }
        
        with open("test_report.json", "w") as f:
            json.dump(report, f, indent=2)
            
        print(f"\n📄 Test report saved to test_report.json")

def main():
    """Main test function"""
    import argparse
    
    parser = argparse.ArgumentParser(description="LazAI Intelligence Hub Test Suite")
    parser.add_argument("--url", default="http://localhost:8000",
                       help="Base URL of the LazAI server")
    parser.add_argument("--report", action="store_true",
                       help="Generate test report")
    
    args = parser.parse_args()
    
    test_suite = LazAITestSuite(base_url=args.url)
    
    try:
        success = test_suite.run_all_tests()
        
        if args.report:
            test_suite.generate_report()
            
        return 0 if success else 1
        
    except KeyboardInterrupt:
        print("\n🛑 Tests interrupted by user")
        return 1
    except Exception as e:
        print(f"\n❌ Test suite failed: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
