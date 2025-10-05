#!/usr/bin/env python3
"""
LazAI Intelligence Hub - Demonstration Script

This script demonstrates the key features of the LazAI Intelligence Hub application.
Run this after starting the main application to see the system in action.
"""

import requests
import json
import time
from typing import Dict, Any

class LazAIDemo:
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.session = requests.Session()
        
    def print_section(self, title: str):
        """Print a formatted section header"""
        print(f"\n{'='*60}")
        print(f"🚀 {title}")
        print(f"{'='*60}")
        
    def print_result(self, title: str, data: Any):
        """Print formatted results"""
        print(f"\n📊 {title}")
        print("-" * 40)
        if isinstance(data, dict):
            print(json.dumps(data, indent=2))
        else:
            print(data)
            
    def test_health_check(self):
        """Test the health check endpoint"""
        self.print_section("Health Check")
        try:
            response = self.session.get(f"{self.base_url}/health")
            self.print_result("Health Status", response.json())
            return True
        except Exception as e:
            print(f"❌ Health check failed: {e}")
            return False
            
    def test_basic_query(self):
        """Test basic RAG query"""
        self.print_section("Basic RAG Query")
        try:
            payload = {
                "file_id": 2346,
                "query": "What are my main skills and expertise?",
                "limit": 3
            }
            response = self.session.post(f"{self.base_url}/query/rag", json=payload)
            self.print_result("Query Results", response.json())
            return True
        except Exception as e:
            print(f"❌ Basic query failed: {e}")
            return False
            
    def test_local_query(self):
        """Test local query functionality"""
        self.print_section("Local Query Test")
        try:
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
            response = self.session.post(f"{self.base_url}/query/local", json=payload)
            self.print_result("Local Query Results", response.json())
            return True
        except Exception as e:
            print(f"❌ Local query failed: {e}")
            return False
            
    def test_analytics_insights(self):
        """Test analytics insights generation"""
        self.print_section("Analytics Insights")
        try:
            # Test different analysis types
            analysis_types = ["summary", "skills", "technologies", "interests"]
            
            for analysis_type in analysis_types:
                payload = {
                    "file_id": 2346,
                    "analysis_type": analysis_type
                }
                response = self.session.post(f"{self.base_url}/analytics/insights", json=payload)
                self.print_result(f"{analysis_type.title()} Analysis", response.json())
                time.sleep(1)  # Rate limiting
                
            return True
        except Exception as e:
            print(f"❌ Analytics insights failed: {e}")
            return False
            
    def test_analytics_trends(self):
        """Test analytics trends endpoint"""
        self.print_section("Analytics Trends")
        try:
            response = self.session.get(f"{self.base_url}/analytics/trends")
            self.print_result("Usage Trends", response.json())
            return True
        except Exception as e:
            print(f"❌ Analytics trends failed: {e}")
            return False
            
    def test_multiple_queries(self):
        """Test multiple queries to simulate real usage"""
        self.print_section("Multiple Query Simulation")
        queries = [
            "What are my main skills?",
            "Summarize my background",
            "What technologies do I work with?",
            "What are my interests and passions?",
            "What programming languages do I know?"
        ]
        
        results = []
        for i, query in enumerate(queries, 1):
            try:
                print(f"\n🔍 Query {i}: {query}")
                payload = {
                    "file_id": 2346,
                    "query": query,
                    "limit": 2
                }
                response = self.session.post(f"{self.base_url}/query/rag", json=payload)
                result = response.json()
                results.append({"query": query, "status": "success", "data_count": len(result.get("data", []))})
                print(f"✅ Success: {len(result.get('data', []))} results")
                time.sleep(0.5)  # Rate limiting
            except Exception as e:
                results.append({"query": query, "status": "failed", "error": str(e)})
                print(f"❌ Failed: {e}")
                
        self.print_result("Query Summary", results)
        return len([r for r in results if r["status"] == "success"]) > 0
        
    def run_full_demo(self):
        """Run the complete demonstration"""
        print("🎯 LazAI Intelligence Hub - Full Demonstration")
        print("=" * 60)
        print("This demo showcases the key features of the LazAI Intelligence Hub")
        print("Make sure the server is running on http://localhost:8000")
        
        # Test sequence
        tests = [
            ("Health Check", self.test_health_check),
            ("Basic RAG Query", self.test_basic_query),
            ("Local Query", self.test_local_query),
            ("Analytics Insights", self.test_analytics_insights),
            ("Analytics Trends", self.test_analytics_trends),
            ("Multiple Queries", self.test_multiple_queries)
        ]
        
        results = []
        for test_name, test_func in tests:
            print(f"\n🧪 Running: {test_name}")
            try:
                success = test_func()
                results.append((test_name, success))
                if success:
                    print(f"✅ {test_name} - PASSED")
                else:
                    print(f"❌ {test_name} - FAILED")
            except Exception as e:
                print(f"❌ {test_name} - ERROR: {e}")
                results.append((test_name, False))
                
        # Summary
        self.print_section("Demo Summary")
        passed = sum(1 for _, success in results if success)
        total = len(results)
        
        print(f"📊 Tests Passed: {passed}/{total}")
        print(f"📈 Success Rate: {(passed/total)*100:.1f}%")
        
        print("\n🎉 Demo completed!")
        print("\nNext steps:")
        print("1. Open http://localhost:8000/ui in your browser")
        print("2. Try the interactive web interface")
        print("3. Upload your own data files")
        print("4. Explore the analytics dashboard")
        
        return passed == total

def main():
    """Main demonstration function"""
    demo = LazAIDemo()
    
    print("🚀 Starting LazAI Intelligence Hub Demonstration...")
    print("⏳ Waiting 2 seconds for server to be ready...")
    time.sleep(2)
    
    success = demo.run_full_demo()
    
    if success:
        print("\n🎊 All tests passed! The LazAI Intelligence Hub is working perfectly.")
    else:
        print("\n⚠️  Some tests failed. Check the server logs for details.")
        
    return success

if __name__ == "__main__":
    main()
