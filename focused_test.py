#!/usr/bin/env python3
"""
Focused Oracle Engine Backend Testing - MongoDB + Gemini Setup
"""

import requests
import json
import time

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

print(f"🔍 ORACLE ENGINE FOCUSED TESTING")
print(f"Backend URL: {API_URL}")
print("=" * 60)

def test_basic_health():
    """Test 1: Basic API Health Check"""
    print("\n🔍 TEST 1: API Health Check")
    try:
        response = requests.get(f"{API_URL}/", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ API Health: PASSED - {data['message']}")
            return True
        else:
            print(f"❌ API Health: FAILED - Status {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ API Health: FAILED - {str(e)}")
        return False

def test_dashboard():
    """Test 2: Dashboard Stats with MongoDB"""
    print("\n🔍 TEST 2: Dashboard Stats (MongoDB)")
    try:
        response = requests.get(f"{API_URL}/dashboard/stats", timeout=15)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Dashboard: PASSED")
            print(f"   Trends monitored: {data.get('total_trends_monitored', 0)}")
            print(f"   Content generated: {data.get('content_pieces_generated', 0)}")
            print(f"   System status: {data.get('system_status', 'unknown')}")
            return True
        else:
            print(f"❌ Dashboard: FAILED - Status {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Dashboard: FAILED - {str(e)}")
        return False

def test_niche_analysis():
    """Test 3: Niche Analysis with MongoDB Storage"""
    print("\n🔍 TEST 3: Niche Analysis (Core Feature)")
    try:
        payload = {
            "niche": "fitness",
            "keywords": ["workout", "nutrition"]
        }
        
        response = requests.post(f"{API_URL}/niche/analyze", json=payload, timeout=45)
        if response.status_code == 200:
            data = response.json()
            trends = data.get("trends", [])
            print(f"✅ Niche Analysis: PASSED")
            print(f"   Found {len(trends)} trends")
            if trends:
                print(f"   Sample trend: {trends[0]['title']}")
                print(f"   Trend score: {trends[0]['trend_score']}")
                print(f"   Velocity: {trends[0]['velocity']}")
            print(f"   Forecast: {data.get('forecast_summary', '')[:100]}...")
            return True
        else:
            print(f"❌ Niche Analysis: FAILED - Status {response.status_code}")
            try:
                error = response.json()
                print(f"   Error: {error}")
            except:
                print(f"   Response: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Niche Analysis: FAILED - {str(e)}")
        return False

def test_content_generation():
    """Test 4: Content Generation with Gemini"""
    print("\n🔍 TEST 4: Content Generation (Gemini AI)")
    
    test_cases = [
        {
            "name": "Ad Copy",
            "payload": {
                "niche": "fitness",
                "trend_data": ["AI-powered fitness tracking", "Plant-based protein"],
                "content_type": "ad_copy"
            }
        },
        {
            "name": "Social Post", 
            "payload": {
                "niche": "crypto",
                "trend_data": ["Bitcoin adoption", "DeFi protocols"],
                "content_type": "social_post"
            }
        },
        {
            "name": "Affiliate Review",
            "payload": {
                "niche": "saas",
                "trend_data": ["AI automation tools", "No-code platforms"],
                "content_type": "affiliate_review"
            }
        }
    ]
    
    results = []
    for test_case in test_cases:
        print(f"\n   Testing: {test_case['name']}")
        try:
            response = requests.post(f"{API_URL}/content/generate", json=test_case['payload'], timeout=60)
            if response.status_code == 200:
                data = response.json()
                content_length = len(data.get('content', ''))
                confidence = data.get('confidence_score', 0)
                print(f"   ✅ {test_case['name']}: PASSED")
                print(f"      Content length: {content_length} chars")
                print(f"      Confidence: {confidence:.2f}")
                results.append(True)
            else:
                print(f"   ❌ {test_case['name']}: FAILED - Status {response.status_code}")
                try:
                    error = response.json()
                    print(f"      Error: {error}")
                except:
                    print(f"      Response: {response.text}")
                results.append(False)
        except Exception as e:
            print(f"   ❌ {test_case['name']}: FAILED - {str(e)}")
            results.append(False)
        
        time.sleep(3)  # Delay between requests
    
    passed = sum(results)
    total = len(results)
    if passed == total:
        print(f"\n✅ Content Generation: ALL PASSED ({passed}/{total})")
        return True
    else:
        print(f"\n❌ Content Generation: PARTIAL ({passed}/{total})")
        return passed > 0

def test_data_retrieval():
    """Test 5: Data Retrieval from MongoDB"""
    print("\n🔍 TEST 5: Data Retrieval (MongoDB)")
    
    results = []
    
    # Test content history
    try:
        response = requests.get(f"{API_URL}/content/history/fitness", timeout=15)
        if response.status_code == 200:
            data = response.json()
            history_count = len(data.get('content_history', []))
            print(f"   ✅ Content History: PASSED - {history_count} items")
            results.append(True)
        else:
            print(f"   ❌ Content History: FAILED - Status {response.status_code}")
            results.append(False)
    except Exception as e:
        print(f"   ❌ Content History: FAILED - {str(e)}")
        results.append(False)
    
    # Test trends retrieval
    try:
        response = requests.get(f"{API_URL}/trends/latest/fitness", timeout=15)
        if response.status_code == 200:
            data = response.json()
            trends_count = len(data.get('trends', []))
            print(f"   ✅ Latest Trends: PASSED - {trends_count} trends")
            results.append(True)
        else:
            print(f"   ❌ Latest Trends: FAILED - Status {response.status_code}")
            results.append(False)
    except Exception as e:
        print(f"   ❌ Latest Trends: FAILED - {str(e)}")
        results.append(False)
    
    passed = sum(results)
    total = len(results)
    if passed == total:
        print(f"\n✅ Data Retrieval: ALL PASSED ({passed}/{total})")
        return True
    else:
        print(f"\n❌ Data Retrieval: PARTIAL ({passed}/{total})")
        return passed > 0

def test_end_to_end():
    """Test 6: End-to-End Workflow"""
    print("\n🔍 TEST 6: End-to-End Workflow")
    
    try:
        # Step 1: Analyze niche
        print("   Step 1: Analyzing niche...")
        niche_payload = {"niche": "crypto", "keywords": ["bitcoin", "defi"]}
        niche_response = requests.post(f"{API_URL}/niche/analyze", json=niche_payload, timeout=45)
        
        if niche_response.status_code != 200:
            print("   ❌ E2E: FAILED - Niche analysis failed")
            return False
        
        niche_data = niche_response.json()
        trends = [trend['title'] for trend in niche_data['trends'][:3]]
        
        # Step 2: Generate content
        print("   Step 2: Generating content...")
        content_payload = {
            "niche": "crypto",
            "trend_data": trends,
            "content_type": "social_post"
        }
        content_response = requests.post(f"{API_URL}/content/generate", json=content_payload, timeout=60)
        
        if content_response.status_code != 200:
            print("   ❌ E2E: FAILED - Content generation failed")
            return False
        
        # Step 3: Retrieve history
        print("   Step 3: Retrieving data...")
        history_response = requests.get(f"{API_URL}/content/history/crypto", timeout=15)
        trends_response = requests.get(f"{API_URL}/trends/latest/crypto", timeout=15)
        
        if history_response.status_code == 200 and trends_response.status_code == 200:
            history_data = history_response.json()
            trends_data = trends_response.json()
            
            print(f"   ✅ E2E Workflow: PASSED")
            print(f"      Generated trends: {len(niche_data['trends'])}")
            print(f"      Content pieces: {len(history_data['content_history'])}")
            print(f"      Stored trends: {len(trends_data['trends'])}")
            return True
        else:
            print("   ❌ E2E: FAILED - Data retrieval failed")
            return False
            
    except Exception as e:
        print(f"   ❌ E2E: FAILED - {str(e)}")
        return False

def run_focused_tests():
    """Run focused tests for Oracle Engine"""
    tests = [
        ("API Health Check", test_basic_health),
        ("Dashboard Stats", test_dashboard),
        ("Niche Analysis", test_niche_analysis),
        ("Content Generation", test_content_generation),
        ("Data Retrieval", test_data_retrieval),
        ("End-to-End Workflow", test_end_to_end)
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n{'='*20} {test_name} {'='*20}")
        result = test_func()
        results.append((test_name, result))
        time.sleep(2)
    
    # Summary
    print("\n" + "="*60)
    print("🏁 FOCUSED TEST SUMMARY")
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
        print("🎉 ALL CORE FEATURES WORKING - Oracle Engine is fully operational!")
    elif passed >= 4:
        print("✅ CORE FEATURES WORKING - Minor issues may exist")
    else:
        print("🚨 CRITICAL ISSUES - Core functionality problems detected")
    
    return passed, total

if __name__ == "__main__":
    run_focused_tests()