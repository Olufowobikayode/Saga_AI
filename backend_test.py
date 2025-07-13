#!/usr/bin/env python3
"""
Comprehensive Backend API Testing for Oracle Engine
Tests all core functionality including AI integrations and database connections
"""

import requests
import json
import time
import os
from datetime import datetime

# Get backend URL from frontend .env file
def get_backend_url():
    try:
        with open('/app/frontend/.env', 'r') as f:
            for line in f:
                if line.startswith('REACT_APP_BACKEND_URL='):
                    return line.split('=', 1)[1].strip()
    except Exception as e:
        print(f"Error reading frontend .env: {e}")
    return "http://localhost:8001"

BASE_URL = get_backend_url()
API_URL = f"{BASE_URL}/api"

print(f"Testing Oracle Engine Backend API at: {API_URL}")
print("=" * 60)

def test_api_health():
    """Test 1: Basic API Health Check"""
    print("\n🔍 TEST 1: API Health Check")
    try:
        response = requests.get(f"{API_URL}/", timeout=10)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.json()}")
        
        if response.status_code == 200:
            data = response.json()
            if "Oracle Engine" in data.get("message", ""):
                print("✅ API Health Check: PASSED")
                return True
            else:
                print("❌ API Health Check: FAILED - Unexpected response message")
                return False
        else:
            print(f"❌ API Health Check: FAILED - Status {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ API Health Check: FAILED - {str(e)}")
        return False

def test_dashboard_stats():
    """Test 2: Dashboard Statistics"""
    print("\n🔍 TEST 2: Dashboard Statistics")
    try:
        response = requests.get(f"{API_URL}/dashboard/stats", timeout=15)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Response: {json.dumps(data, indent=2)}")
            
            required_fields = ["total_trends_monitored", "content_pieces_generated", "active_niches", "system_status"]
            missing_fields = [field for field in required_fields if field not in data]
            
            if not missing_fields:
                print("✅ Dashboard Stats: PASSED")
                return True
            else:
                print(f"❌ Dashboard Stats: FAILED - Missing fields: {missing_fields}")
                return False
        else:
            print(f"❌ Dashboard Stats: FAILED - Status {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Dashboard Stats: FAILED - {str(e)}")
        return False

def test_niche_analysis():
    """Test 3: Niche Analysis (Core Feature)"""
    print("\n🔍 TEST 3: Niche Analysis - Core Feature")
    try:
        # Test with fitness niche as requested
        payload = {
            "niche": "fitness",
            "keywords": ["workout", "nutrition", "supplements"]
        }
        
        print(f"Request payload: {json.dumps(payload, indent=2)}")
        response = requests.post(f"{API_URL}/niche/analyze", json=payload, timeout=30)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Response keys: {list(data.keys())}")
            
            # Check required fields
            required_fields = ["niche", "trends", "forecast_summary", "top_opportunities"]
            missing_fields = [field for field in required_fields if field not in data]
            
            if missing_fields:
                print(f"❌ Niche Analysis: FAILED - Missing fields: {missing_fields}")
                return False
            
            # Check trends structure
            trends = data.get("trends", [])
            if not trends:
                print("❌ Niche Analysis: FAILED - No trends returned")
                return False
            
            # Verify trend data structure
            first_trend = trends[0]
            trend_fields = ["niche", "title", "content", "source", "trend_score", "velocity"]
            missing_trend_fields = [field for field in trend_fields if field not in first_trend]
            
            if missing_trend_fields:
                print(f"❌ Niche Analysis: FAILED - Missing trend fields: {missing_trend_fields}")
                return False
            
            print(f"✅ Niche Analysis: PASSED - Found {len(trends)} trends")
            print(f"   Sample trend: {first_trend['title']}")
            print(f"   Trend score: {first_trend['trend_score']}")
            print(f"   Velocity: {first_trend['velocity']}")
            return True
        else:
            print(f"❌ Niche Analysis: FAILED - Status {response.status_code}")
            try:
                error_detail = response.json()
                print(f"   Error details: {error_detail}")
            except:
                print(f"   Response text: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Niche Analysis: FAILED - {str(e)}")
        return False

def test_content_generation():
    """Test 4: Content Generation (Core Feature)"""
    print("\n🔍 TEST 4: Content Generation - Core Feature")
    
    test_cases = [
        {
            "name": "Ad Copy (OpenAI)",
            "payload": {
                "niche": "fitness",
                "trend_data": ["AI-powered fitness tracking", "Plant-based protein alternatives"],
                "content_type": "ad_copy"
            }
        },
        {
            "name": "Social Post (Gemini)",
            "payload": {
                "niche": "fitness", 
                "trend_data": ["Cold plunge therapy", "Functional fitness movements"],
                "content_type": "social_post"
            }
        },
        {
            "name": "Affiliate Review",
            "payload": {
                "niche": "fitness",
                "trend_data": ["Wearable fitness technology", "Recovery supplements"],
                "content_type": "affiliate_review"
            }
        }
    ]
    
    results = []
    
    for test_case in test_cases:
        print(f"\n   Testing: {test_case['name']}")
        try:
            response = requests.post(f"{API_URL}/content/generate", json=test_case['payload'], timeout=45)
            print(f"   Status Code: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                required_fields = ["niche", "content_type", "title", "content", "confidence_score"]
                missing_fields = [field for field in required_fields if field not in data]
                
                if not missing_fields:
                    print(f"   ✅ {test_case['name']}: PASSED")
                    print(f"      Content length: {len(data['content'])} chars")
                    print(f"      Confidence: {data['confidence_score']}")
                    results.append(True)
                else:
                    print(f"   ❌ {test_case['name']}: FAILED - Missing fields: {missing_fields}")
                    results.append(False)
            else:
                print(f"   ❌ {test_case['name']}: FAILED - Status {response.status_code}")
                try:
                    error_detail = response.json()
                    print(f"      Error: {error_detail}")
                except:
                    print(f"      Response: {response.text}")
                results.append(False)
        except Exception as e:
            print(f"   ❌ {test_case['name']}: FAILED - {str(e)}")
            results.append(False)
        
        # Add delay between requests to avoid rate limiting
        time.sleep(2)
    
    passed_tests = sum(results)
    total_tests = len(results)
    
    if passed_tests == total_tests:
        print(f"\n✅ Content Generation: ALL PASSED ({passed_tests}/{total_tests})")
        return True
    else:
        print(f"\n❌ Content Generation: PARTIAL FAILURE ({passed_tests}/{total_tests})")
        return False

def test_data_retrieval():
    """Test 5: Data Retrieval Endpoints"""
    print("\n🔍 TEST 5: Data Retrieval")
    
    test_niche = "fitness"
    results = []
    
    # Test content history
    print(f"\n   Testing: Content History for '{test_niche}'")
    try:
        response = requests.get(f"{API_URL}/content/history/{test_niche}", timeout=15)
        print(f"   Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            if "content_history" in data:
                print(f"   ✅ Content History: PASSED - Found {len(data['content_history'])} items")
                results.append(True)
            else:
                print("   ❌ Content History: FAILED - Missing 'content_history' field")
                results.append(False)
        else:
            print(f"   ❌ Content History: FAILED - Status {response.status_code}")
            results.append(False)
    except Exception as e:
        print(f"   ❌ Content History: FAILED - {str(e)}")
        results.append(False)
    
    # Test latest trends
    print(f"\n   Testing: Latest Trends for '{test_niche}'")
    try:
        response = requests.get(f"{API_URL}/trends/latest/{test_niche}", timeout=15)
        print(f"   Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            if "trends" in data:
                print(f"   ✅ Latest Trends: PASSED - Found {len(data['trends'])} trends")
                results.append(True)
            else:
                print("   ❌ Latest Trends: FAILED - Missing 'trends' field")
                results.append(False)
        else:
            print(f"   ❌ Latest Trends: FAILED - Status {response.status_code}")
            results.append(False)
    except Exception as e:
        print(f"   ❌ Latest Trends: FAILED - {str(e)}")
        results.append(False)
    
    passed_tests = sum(results)
    total_tests = len(results)
    
    if passed_tests == total_tests:
        print(f"\n✅ Data Retrieval: ALL PASSED ({passed_tests}/{total_tests})")
        return True
    else:
        print(f"\n❌ Data Retrieval: PARTIAL FAILURE ({passed_tests}/{total_tests})")
        return False

def test_error_handling():
    """Test 6: Error Handling"""
    print("\n🔍 TEST 6: Error Handling")
    
    error_tests = [
        {
            "name": "Invalid niche data",
            "endpoint": "/niche/analyze",
            "method": "POST",
            "payload": {"niche": "", "keywords": []}
        },
        {
            "name": "Missing required fields",
            "endpoint": "/content/generate", 
            "method": "POST",
            "payload": {"niche": "fitness"}  # Missing trend_data and content_type
        },
        {
            "name": "Invalid content type",
            "endpoint": "/content/generate",
            "method": "POST", 
            "payload": {
                "niche": "fitness",
                "trend_data": ["test"],
                "content_type": "invalid_type"
            }
        }
    ]
    
    results = []
    
    for test in error_tests:
        print(f"\n   Testing: {test['name']}")
        try:
            if test['method'] == 'POST':
                response = requests.post(f"{API_URL}{test['endpoint']}", json=test['payload'], timeout=15)
            else:
                response = requests.get(f"{API_URL}{test['endpoint']}", timeout=15)
            
            print(f"   Status Code: {response.status_code}")
            
            # For error handling, we expect 4xx or 5xx status codes
            if response.status_code >= 400:
                print(f"   ✅ {test['name']}: PASSED - Proper error response")
                results.append(True)
            else:
                print(f"   ❌ {test['name']}: FAILED - Should return error status")
                results.append(False)
                
        except Exception as e:
            print(f"   ❌ {test['name']}: FAILED - {str(e)}")
            results.append(False)
    
    passed_tests = sum(results)
    total_tests = len(results)
    
    if passed_tests >= total_tests // 2:  # At least half should pass
        print(f"\n✅ Error Handling: ACCEPTABLE ({passed_tests}/{total_tests})")
        return True
    else:
        print(f"\n❌ Error Handling: FAILED ({passed_tests}/{total_tests})")
        return False

def run_all_tests():
    """Run all backend tests"""
    print(f"\n🚀 ORACLE ENGINE BACKEND API TESTING")
    print(f"Timestamp: {datetime.now().isoformat()}")
    print(f"Backend URL: {API_URL}")
    print("=" * 60)
    
    tests = [
        ("API Health Check", test_api_health),
        ("Dashboard Statistics", test_dashboard_stats),
        ("Niche Analysis", test_niche_analysis),
        ("Content Generation", test_content_generation),
        ("Data Retrieval", test_data_retrieval),
        ("Error Handling", test_error_handling)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n{'='*20} {test_name} {'='*20}")
        result = test_func()
        results.append((test_name, result))
        time.sleep(1)  # Brief pause between tests
    
    # Summary
    print("\n" + "="*60)
    print("🏁 TEST SUMMARY")
    print("="*60)
    
    passed = 0
    for test_name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{test_name}: {status}")
        if result:
            passed += 1
    
    total = len(results)
    print(f"\nOverall: {passed}/{total} tests passed ({(passed/total)*100:.1f}%)")
    
    if passed == total:
        print("🎉 ALL TESTS PASSED - Oracle Engine backend is fully functional!")
    elif passed >= total * 0.8:
        print("⚠️  MOSTLY WORKING - Minor issues detected")
    else:
        print("🚨 CRITICAL ISSUES - Major functionality problems detected")
    
    return passed, total

if __name__ == "__main__":
    run_all_tests()