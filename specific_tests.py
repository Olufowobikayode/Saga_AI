#!/usr/bin/env python3
"""
Specific Test Cases from Review Request
"""

import requests
import json

BASE_URL = "https://0ca9a8d3-d30b-4ce2-abe9-68649d5bfd53.preview.emergentagent.com/api"

print("🔍 SPECIFIC REVIEW REQUEST TESTS")
print("=" * 50)

def test_specific_niches():
    """Test specific niches from review request"""
    
    test_cases = [
        {
            "name": "Fitness with keywords",
            "payload": {"niche": "fitness", "keywords": ["workout", "nutrition"]}
        },
        {
            "name": "Crypto with keywords", 
            "payload": {"niche": "crypto", "keywords": ["bitcoin", "defi"]}
        },
        {
            "name": "SaaS without keywords",
            "payload": {"niche": "saas"}
        }
    ]
    
    for test_case in test_cases:
        print(f"\n🔍 Testing: {test_case['name']}")
        try:
            response = requests.post(f"{BASE_URL}/niche/analyze", json=test_case['payload'], timeout=45)
            if response.status_code == 200:
                data = response.json()
                trends = data.get('trends', [])
                print(f"✅ {test_case['name']}: PASSED")
                print(f"   Trends found: {len(trends)}")
                print(f"   Trend score range: {min(t['trend_score'] for t in trends):.3f} - {max(t['trend_score'] for t in trends):.3f}")
                print(f"   Velocity range: {min(t['velocity'] for t in trends):.3f} - {max(t['velocity'] for t in trends):.3f}")
                print(f"   Forecast summary: {data.get('forecast_summary', '')[:100]}...")
            else:
                print(f"❌ {test_case['name']}: FAILED - Status {response.status_code}")
        except Exception as e:
            print(f"❌ {test_case['name']}: FAILED - {str(e)}")

def test_all_content_types():
    """Test all content types with Gemini"""
    
    content_types = ["ad_copy", "social_post", "affiliate_review"]
    
    for content_type in content_types:
        print(f"\n🔍 Testing Content Type: {content_type}")
        payload = {
            "niche": "fitness",
            "trend_data": ["AI fitness tracking", "Plant-based nutrition"],
            "content_type": content_type
        }
        
        try:
            response = requests.post(f"{BASE_URL}/content/generate", json=payload, timeout=60)
            if response.status_code == 200:
                data = response.json()
                print(f"✅ {content_type}: PASSED")
                print(f"   Content length: {len(data.get('content', ''))} chars")
                print(f"   Confidence score: {data.get('confidence_score', 0):.3f}")
                print(f"   Title: {data.get('title', '')}")
            else:
                print(f"❌ {content_type}: FAILED - Status {response.status_code}")
        except Exception as e:
            print(f"❌ {content_type}: FAILED - {str(e)}")

if __name__ == "__main__":
    test_specific_niches()
    print("\n" + "="*50)
    test_all_content_types()