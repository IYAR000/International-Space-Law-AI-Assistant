"""
Test script for LLM integration with the legal analysis API endpoints
"""
import requests
import json
from typing import Dict, Any

# API Configuration
DATA_COLLECTION_API = "http://localhost:8001"
LEGAL_ANALYSIS_API = "http://localhost:8002"

# LLM Configuration (add your API key)
OPENAI_API_KEY = ""  # Set your API key here
OPENAI_API_URL = "https://api.openai.com/v1/chat/completions"

# Alternative: Claude/Anthropic
CLAUDE_API_KEY = ""  # Set your API key here
CLAUDE_API_URL = "https://api.anthropic.com/v1/messages"


def test_data_collection_api():
    """Test the data collection API"""
    print("\n" + "="*60)
    print("Testing Data Collection API")
    print("="*60)
    
    # Test health endpoint
    try:
        response = requests.get(f"{DATA_COLLECTION_API}/health")
        print(f"✓ Health Check: {response.status_code}")
        print(f"  Response: {response.json()}")
    except Exception as e:
        print(f"✗ Health Check Failed: {e}")
        return False
    
    # Test docs endpoint
    try:
        response = requests.get(f"{DATA_COLLECTION_API}/docs")
        print(f"✓ API Docs Available: {response.status_code}")
    except Exception as e:
        print(f"✗ API Docs Failed: {e}")
    
    return True


def test_legal_analysis_api():
    """Test the legal analysis API"""
    print("\n" + "="*60)
    print("Testing Legal Analysis API")
    print("="*60)
    
    # Test health endpoint
    try:
        response = requests.get(f"{LEGAL_ANALYSIS_API}/health")
        print(f"✓ Health Check: {response.status_code}")
        print(f"  Response: {response.json()}")
    except Exception as e:
        print(f"✗ Health Check Failed: {e}")
        return False
    
    # Test docs endpoint
    try:
        response = requests.get(f"{LEGAL_ANALYSIS_API}/docs")
        print(f"✓ API Docs Available: {response.status_code}")
    except Exception as e:
        print(f"✗ API Docs Failed: {e}")
    
    return True


def test_analysis_endpoint(sample_text: str):
    """Test the analysis endpoint with sample legal text"""
    print("\n" + "="*60)
    print("Testing Analysis Endpoint")
    print("="*60)
    
    # Create a mock document ID since database might not have real data
    test_request = {
        "document_ids": ["mock-doc-001"],
        "analysis_types": ["customary_vs_treaty"],
        "include_jus_cogens": True
    }
    
    print(f"\nRequest: {json.dumps(test_request, indent=2)}")
    
    try:
        response = requests.post(
            f"{LEGAL_ANALYSIS_API}/analyze/customary-vs-treaty",
            json=test_request,
            headers={"Content-Type": "application/json"}
        )
        print(f"\n✓ Analysis Request: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        return response.json()
    except Exception as e:
        print(f"✗ Analysis Request Failed: {e}")
        return None


def test_llm_integration_with_openai(analysis_result: Dict[str, Any]):
    """Test LLM integration with OpenAI"""
    print("\n" + "="*60)
    print("Testing LLM Integration (OpenAI)")
    print("="*60)
    
    if not OPENAI_API_KEY:
        print("⚠ OPENAI_API_KEY not set. Skipping OpenAI test.")
        print("\nTo test with OpenAI:")
        print("1. Get your API key from https://platform.openai.com/api-keys")
        print("2. Update OPENAI_API_KEY in this script")
        return
    
    # Prepare prompt for LLM
    prompt = f"""
You are an expert in international space law. Based on the following analysis results,
provide a comprehensive legal opinion on the classification of the document:

Analysis Results:
{json.dumps(analysis_result, indent=2)}

Please provide:
1. A summary of the legal classification
2. Key indicators that support this classification
3. Any potential issues or conflicts
4. Recommendations for further analysis
"""
    
    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": "gpt-4",
        "messages": [
            {"role": "system", "content": "You are an expert in international space law."},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.7,
        "max_tokens": 1000
    }
    
    try:
        print("\nSending request to OpenAI GPT-4...")
        response = requests.post(OPENAI_API_URL, json=payload, headers=headers)
        
        if response.status_code == 200:
            result = response.json()
            print(f"✓ LLM Response Received")
            print(f"\nLegal Opinion from GPT-4:")
            print("-" * 60)
            print(result['choices'][0]['message']['content'])
            print("-" * 60)
        else:
            print(f"✗ LLM Request Failed: {response.status_code}")
            print(f"Error: {response.text}")
    except Exception as e:
        print(f"✗ LLM Integration Failed: {e}")


def test_llm_integration_with_claude(analysis_result: Dict[str, Any]):
    """Test LLM integration with Claude/Anthropic"""
    print("\n" + "="*60)
    print("Testing LLM Integration (Claude/Anthropic)")
    print("="*60)
    
    if not CLAUDE_API_KEY:
        print("⚠ CLAUDE_API_KEY not set. Skipping Claude test.")
        print("\nTo test with Claude:")
        print("1. Get your API key from https://console.anthropic.com/")
        print("2. Update CLAUDE_API_KEY in this script")
        return
    
    # Prepare prompt for LLM
    prompt = f"""You are an expert in international space law. Based on the following analysis results,
provide a comprehensive legal opinion on the classification of the document:

Analysis Results:
{json.dumps(analysis_result, indent=2)}

Please provide:
1. A summary of the legal classification
2. Key indicators that support this classification
3. Any potential issues or conflicts
4. Recommendations for further analysis"""
    
    headers = {
        "x-api-key": CLAUDE_API_KEY,
        "anthropic-version": "2023-06-01",
        "content-type": "application/json"
    }
    
    payload = {
        "model": "claude-3-opus-20240229",
        "max_tokens": 1024,
        "messages": [
            {"role": "user", "content": prompt}
        ]
    }
    
    try:
        print("\nSending request to Claude (Anthropic)...")
        response = requests.post(CLAUDE_API_URL, json=payload, headers=headers)
        
        if response.status_code == 200:
            result = response.json()
            print(f"✓ LLM Response Received")
            print(f"\nLegal Opinion from Claude:")
            print("-" * 60)
            print(result['content'][0]['text'])
            print("-" * 60)
        else:
            print(f"✗ LLM Request Failed: {response.status_code}")
            print(f"Error: {response.text}")
    except Exception as e:
        print(f"✗ LLM Integration Failed: {e}")


def main():
    """Main test function"""
    print("\n" + "="*80)
    print("SPACE LAW AI ASSISTANT - LLM INTEGRATION TEST")
    print("="*80)
    
    # Test APIs
    dc_ok = test_data_collection_api()
    la_ok = test_legal_analysis_api()
    
    if not (dc_ok and la_ok):
        print("\n⚠ One or more APIs are not responding. Make sure they are running.")
        print("  Data Collection API: http://localhost:8001")
        print("  Legal Analysis API: http://localhost:8002")
        return
    
    # Test analysis endpoint
    analysis_result = test_analysis_endpoint("")
    
    if analysis_result:
        # Test LLM integration
        print("\n" + "="*80)
        print("LLM INTEGRATION SETUP")
        print("="*80)
        print("\nYou have two options:")
        print("\n1. OpenAI (GPT-4)")
        print("   - Get API key: https://platform.openai.com/api-keys")
        print("   - Set OPENAI_API_KEY variable in this script")
        print("\n2. Claude (Anthropic)")
        print("   - Get API key: https://console.anthropic.com/")
        print("   - Set CLAUDE_API_KEY variable in this script")
        
        test_llm_integration_with_openai(analysis_result)
        test_llm_integration_with_claude(analysis_result)
    
    print("\n" + "="*80)
    print("TEST COMPLETE")
    print("="*80)
    print("\nNext Steps:")
    print("1. Add your LLM API key to this script")
    print("2. Run the test again to verify LLM integration")
    print("3. Review the API documentation at:")
    print(f"   - Data Collection: {DATA_COLLECTION_API}/docs")
    print(f"   - Legal Analysis: {LEGAL_ANALYSIS_API}/docs")


if __name__ == "__main__":
    main()
