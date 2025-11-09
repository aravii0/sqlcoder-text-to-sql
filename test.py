#!/usr/bin/env python3
"""
Test script for SQLCoder Text-to-SQL application
Basic functionality tests
"""

import requests
import json
import time
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.append(str(project_root))

API_BASE_URL = "http://localhost:8000"

def test_api_connection():
    """Test if API is accessible"""
    try:
        response = requests.get(f"{API_BASE_URL}/", timeout=10)
        return response.status_code == 200
    except:
        return False

def test_sql_generation():
    """Test SQL query generation"""
    test_questions = [
        "Show me all customers",
        "What is the total revenue by city?",
        "List customers from Mumbai",
        "Show all products sorted by price"
    ]

    results = []
    for question in test_questions:
        try:
            response = requests.post(
                f"{API_BASE_URL}/generate-sql",
                json={"question": question},
                timeout=30
            )
            if response.status_code == 200:
                data = response.json()
                results.append({
                    "question": question,
                    "success": True,
                    "sql": data.get("sql_query", ""),
                    "time": data.get("execution_time", 0)
                })
            else:
                results.append({
                    "question": question,
                    "success": False,
                    "error": f"HTTP {response.status_code}"
                })
        except Exception as e:
            results.append({
                "question": question,
                "success": False,
                "error": str(e)
            })

    return results

def test_query_execution():
    """Test query execution"""
    test_question = "Show me all customers limit 5"

    try:
        response = requests.post(
            f"{API_BASE_URL}/execute-query",
            json={"question": test_question},
            timeout=60
        )
        if response.status_code == 200:
            data = response.json()
            return {
                "success": True,
                "results_count": len(data.get("results", [])),
                "execution_time": data.get("execution_time", 0)
            }
        else:
            return {"success": False, "error": f"HTTP {response.status_code}"}
    except Exception as e:
        return {"success": False, "error": str(e)}

def main():
    """Run all tests"""
    print("🧪 SQLCoder Text-to-SQL Application Tests")
    print("=" * 50)

    # Test 1: API Connection
    print("\n1. Testing API connection...")
    if test_api_connection():
        print("✅ API is accessible")
    else:
        print("❌ API is not accessible. Make sure backend is running.")
        return False

    # Test 2: SQL Generation
    print("\n2. Testing SQL generation...")
    gen_results = test_sql_generation()

    successful_generations = sum(1 for r in gen_results if r["success"])
    print(f"✅ {successful_generations}/{len(gen_results)} questions generated SQL successfully")

    for result in gen_results:
        if result["success"]:
            print(f"   ✓ '{result['question']}' -> Generated in {result['time']:.3f}s")
        else:
            print(f"   ✗ '{result['question']}' -> Error: {result['error']}")

    # Test 3: Query Execution
    print("\n3. Testing query execution...")
    exec_result = test_query_execution()

    if exec_result["success"]:
        print(f"✅ Query executed successfully")
        print(f"   Results: {exec_result['results_count']} rows")
        print(f"   Time: {exec_result['execution_time']:.3f}s")
    else:
        print(f"❌ Query execution failed: {exec_result['error']}")

    # Summary
    print("\n" + "=" * 50)
    total_success = successful_generations + (1 if exec_result["success"] else 0)
    total_tests = len(gen_results) + 1

    if total_success == total_tests:
        print("🎉 All tests passed!")
        return True
    else:
        print(f"⚠️  {total_success}/{total_tests} tests passed")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
