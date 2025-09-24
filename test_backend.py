#!/usr/bin/env python3
"""
Simple test script to verify the backend works locally
"""
import requests
import json

def test_backend():
    base_url = "https://interviewbot-rjsi.onrender.com"
    
    print("🔍 Testing backend endpoints...")
    
    # Test 1: Health check
    print("\n1. Testing health endpoint...")
    try:
        response = requests.get(f"{base_url}/health")
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.json()}")
    except Exception as e:
        print(f"   Error: {e}")
    
    # Test 2: Interview health
    print("\n2. Testing interview health endpoint...")
    try:
        response = requests.get(f"{base_url}/api/interview/health")
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.json()}")
    except Exception as e:
        print(f"   Error: {e}")
    
    # Test 3: Start interview
    print("\n3. Testing interview start endpoint...")
    payload = {
        "position": "Software Engineer",
        "difficulty": "medium", 
        "question_types": ["behavioral", "technical"],
        "duration": 30
    }
    
    try:
        response = requests.post(
            f"{base_url}/api/interview/start",
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   Session ID: {data.get('session_id', 'Missing')}")
            print(f"   Question: {data.get('question', {}).get('text', 'Missing')[:100]}...")
            return data.get('session_id')
        else:
            print(f"   Error Response: {response.text}")
            return None
    except Exception as e:
        print(f"   Error: {e}")
        return None

if __name__ == "__main__":
    test_backend()
