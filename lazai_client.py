#!/usr/bin/env python3
"""
LazAI Data Query Client
This script demonstrates how to interact with the LazAI Data Query system
"""

import os
import sys
import json
import time
import requests
from typing import Dict, Any, Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class LazAIClient:
    """Client for interacting with LazAI Data Query system"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.session = requests.Session()
        self.query_history = []
        
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
            
    def test_connection(self) -> bool:
        """Test connection to the LazAI server"""
        try:
            response = self.session.get(f"{self.base_url}/health")
            if response.status_code == 200:
                print("✅ Successfully connected to LazAI server")
                return True
            else:
                print(f"❌ Server returned status {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Connection failed: {e}")
            return False
    
    def query_rag(self, file_id: int, query: str, limit: int = 3) -> Dict[str, Any]:
        """Query the RAG endpoint with LazAI encryption"""
        try:
            payload = {
                "file_id": file_id,
                "query": query,
                "limit": limit
            }
            
            print(f"🔍 Querying file {file_id}: {query}")
            response = self.session.post(f"{self.base_url}/query/rag", json=payload)
            
            if response.status_code == 200:
                result = response.json()
                self.query_history.append({
                    "type": "rag",
                    "file_id": file_id,
                    "query": query,
                    "timestamp": time.time(),
                    "success": True
                })
                return result
            else:
                print(f"❌ RAG query failed: {response.status_code}")
                return {"error": f"HTTP {response.status_code}"}
                
        except Exception as e:
            print(f"❌ RAG query error: {e}")
            return {"error": str(e)}
    
    def query_local(self, content: str, query: str, collection: str = "local_demo") -> Dict[str, Any]:
        """Query local content without LazAI encryption"""
        try:
            payload = {
                "content": content,
                "query": query,
                "collection": collection
            }
            
            print(f"🔍 Local query: {query}")
            response = self.session.post(f"{self.base_url}/query/local", json=payload)
            
            if response.status_code == 200:
                result = response.json()
                self.query_history.append({
                    "type": "local",
                    "query": query,
                    "timestamp": time.time(),
                    "success": True
                })
                return result
            else:
                print(f"❌ Local query failed: {response.status_code}")
                return {"error": f"HTTP {response.status_code}"}
                
        except Exception as e:
            print(f"❌ Local query error: {e}")
            return {"error": str(e)}
    
    def get_analytics_insights(self, file_id: int, analysis_type: str = "summary") -> Dict[str, Any]:
        """Get AI-powered insights from data"""
        try:
            payload = {
                "file_id": file_id,
                "analysis_type": analysis_type
            }
            
            print(f"📈 Getting {analysis_type} insights for file {file_id}")
            response = self.session.post(f"{self.base_url}/analytics/insights", json=payload)
            
            if response.status_code == 200:
                return response.json()
            else:
                print(f"❌ Analytics failed: {response.status_code}")
                return {"error": f"HTTP {response.status_code}"}
                
        except Exception as e:
            print(f"❌ Analytics error: {e}")
            return {"error": str(e)}
    
    def get_analytics_trends(self) -> Dict[str, Any]:
        """Get query trends and patterns"""
        try:
            print("📊 Getting analytics trends")
            response = self.session.get(f"{self.base_url}/analytics/trends")
            
            if response.status_code == 200:
                return response.json()
            else:
                print(f"❌ Trends failed: {response.status_code}")
                return {"error": f"HTTP {response.status_code}"}
                
        except Exception as e:
            print(f"❌ Trends error: {e}")
            return {"error": str(e)}
    
    def demo_query(self, query: str) -> Dict[str, Any]:
        """Use the demo endpoint for testing without LazAI encryption"""
        try:
            payload = {"query": query}
            
            print(f"🎯 Demo query: {query}")
            response = self.session.post(f"{self.base_url}/demo/query", json=payload)
            
            if response.status_code == 200:
                result = response.json()
                self.query_history.append({
                    "type": "demo",
                    "query": query,
                    "timestamp": time.time(),
                    "success": True
                })
                return result
            else:
                print(f"❌ Demo query failed: {response.status_code}")
                return {"error": f"HTTP {response.status_code}"}
                
        except Exception as e:
            print(f"❌ Demo query error: {e}")
            return {"error": str(e)}
    
    def run_comprehensive_demo(self):
        """Run a comprehensive demonstration of all features"""
        self.print_section("LazAI Data Query - Comprehensive Demo")
        
        # Test connection
        if not self.test_connection():
            print("❌ Cannot proceed without server connection")
            return False
        
        # Demo queries for different scenarios
        demo_queries = [
            "What are my main skills and expertise?",
            "What technologies do I work with?",
            "Summarize my background and interests",
            "What are my programming languages?",
            "What are my main interests and passions?"
        ]
        
        print("\n🎯 Testing Demo Queries (No LazAI encryption required)")
        for i, query in enumerate(demo_queries, 1):
            print(f"\n--- Query {i} ---")
            result = self.demo_query(query)
            if "error" not in result:
                self.print_result(f"Demo Query {i} Results", result.get("data", []))
            else:
                print(f"❌ Query {i} failed: {result['error']}")
        
        # Test local content query
        print("\n📝 Testing Local Content Query")
        sample_content = """
        I am a passionate developer with expertise in Python, Django, React, and AI technologies.
        I love building full-stack applications and have experience with Web3 and blockchain development.
        My interests include machine learning, voice-based AI systems, and teaching programming.
        I enjoy working on creative projects that combine technology with real-world applications.
        """
        
        local_result = self.query_local(
            content=sample_content,
            query="What are the main technologies and skills mentioned?",
            collection="demo_content"
        )
        
        if "error" not in local_result:
            self.print_result("Local Query Results", local_result.get("data", []))
        else:
            print(f"❌ Local query failed: {local_result['error']}")
        
        # Test analytics
        print("\n📊 Testing Analytics Features")
        trends = self.get_analytics_trends()
        if "error" not in trends:
            self.print_result("Usage Trends", trends)
        else:
            print(f"❌ Trends failed: {trends['error']}")
        
        # Summary
        self.print_section("Demo Summary")
        successful_queries = len([q for q in self.query_history if q.get("success", False)])
        total_queries = len(self.query_history)
        
        print(f"📊 Successful Queries: {successful_queries}/{total_queries}")
        print(f"📈 Success Rate: {(successful_queries/total_queries)*100:.1f}%" if total_queries > 0 else "No queries executed")
        
        return successful_queries > 0
    
    def interactive_mode(self):
        """Run in interactive mode for user queries"""
        self.print_section("LazAI Interactive Mode")
        print("Enter your queries (type 'quit' to exit, 'help' for commands)")
        
        while True:
            try:
                query = input("\n🔍 Enter your query: ").strip()
                
                if query.lower() == 'quit':
                    print("👋 Goodbye!")
                    break
                elif query.lower() == 'help':
                    print("\n📖 Available commands:")
                    print("  - Ask any question about your data")
                    print("  - 'demo <query>' - Use demo endpoint")
                    print("  - 'local <query>' - Query local content")
                    print("  - 'trends' - Show analytics trends")
                    print("  - 'history' - Show query history")
                    print("  - 'quit' - Exit")
                    continue
                elif query.lower() == 'trends':
                    trends = self.get_analytics_trends()
                    self.print_result("Analytics Trends", trends)
                    continue
                elif query.lower() == 'history':
                    self.print_result("Query History", self.query_history)
                    continue
                elif query.startswith('demo '):
                    demo_query = query[5:].strip()
                    result = self.demo_query(demo_query)
                    self.print_result("Demo Results", result.get("data", []))
                    continue
                elif query.startswith('local '):
                    local_query = query[6:].strip()
                    # Use sample content for local queries
                    sample_content = "Sample content about AI, Web3, and Python development."
                    result = self.query_local(sample_content, local_query)
                    self.print_result("Local Results", result.get("data", []))
                    continue
                else:
                    # Default to demo query
                    result = self.demo_query(query)
                    if "data" in result:
                        self.print_result("Query Results", result["data"])
                    else:
                        print(f"❌ Query failed: {result.get('error', 'Unknown error')}")
                        
            except KeyboardInterrupt:
                print("\n👋 Goodbye!")
                break
            except Exception as e:
                print(f"❌ Error: {e}")

def main():
    """Main function"""
    import argparse
    
    parser = argparse.ArgumentParser(description="LazAI Data Query Client")
    parser.add_argument("--mode", choices=["demo", "interactive"], default="demo",
                       help="Run mode: demo or interactive")
    parser.add_argument("--url", default="http://localhost:8000",
                       help="Base URL of the LazAI server")
    
    args = parser.parse_args()
    
    client = LazAIClient(base_url=args.url)
    
    if args.mode == "demo":
        success = client.run_comprehensive_demo()
        if success:
            print("\n🎊 Demo completed successfully!")
        else:
            print("\n⚠️  Demo had some issues. Check server logs.")
    else:
        client.interactive_mode()

if __name__ == "__main__":
    main()
