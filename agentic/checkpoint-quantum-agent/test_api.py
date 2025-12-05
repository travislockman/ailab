#!/usr/bin/env python3
"""Test script to verify Check Point Smart-1 Cloud API authentication."""

import os
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get credentials
api_key = os.getenv("CHECKPOINT_API_KEY")
cloud_token = os.getenv("CHECKPOINT_CLOUD_INFRA_TOKEN")
server = os.getenv("CHECKPOINT_SERVER")

print(f"Testing API connection to: {server}")
print(f"API Key: {api_key[:10]}..." if api_key else "No API key found")
print(f"Cloud Token: {cloud_token[:10] if cloud_token and cloud_token != 'your_cloud_infra_token_here' else 'Not set'}...")
print()

# Test 1: Try show-session with API key as X-chkp-sid
print("Test 1: Using API key directly as X-chkp-sid header")
headers = {
    "Content-Type": "application/json",
    "X-chkp-sid": api_key
}

try:
    response = requests.post(
        f"{server}/show-session",
        headers=headers,
        json={},
        timeout=10
    )
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.text[:500]}")
except Exception as e:
    print(f"Error: {e}")

print("\n" + "="*50 + "\n")

# Test 2: Try login endpoint with API key in Authorization header
print("Test 2: Using API key in Authorization Bearer header")
headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {api_key}"
}
payload = {}

try:
    response = requests.post(
        f"{server}/login",
        headers=headers,
        json=payload,
        timeout=10
    )
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.text[:500]}")
except Exception as e:
    print(f"Error: {e}")

print("\n" + "="*50 + "\n")

# Test 3: Try show-gateways directly with API key
print("Test 3: Calling show-gateways-and-servers directly")
headers = {
    "Content-Type": "application/json",
    "X-chkp-sid": api_key
}

try:
    response = requests.post(
        f"{server}/show-gateways-and-servers",
        headers=headers,
        json={},
        timeout=10
    )
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.text[:500]}")
    
    if response.status_code == 200:
        data = response.json()
        if "objects" in data:
            print(f"\n✅ SUCCESS! Found {len(data['objects'])} gateways:")
            for gw in data['objects']:
                print(f"  - {gw.get('name', 'Unknown')}")
except Exception as e:
    print(f"Error: {e}")

print("\n" + "="*50 + "\n")

# Test 4: Try with BOTH API key and Cloud Infra Token
if cloud_token and cloud_token != 'your_cloud_infra_token_here':
    print("Test 4: Using BOTH X-chkp-sid AND X-chkp-cloud-infra-token")
    headers = {
        "Content-Type": "application/json",
        "X-chkp-sid": api_key,
        "X-chkp-cloud-infra-token": cloud_token
    }

    try:
        response = requests.post(
            f"{server}/show-gateways-and-servers",
            headers=headers,
            json={},
            timeout=10
        )
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text[:500]}")
        
        if response.status_code == 200:
            data = response.json()
            if "objects" in data:
                print(f"\n✅ SUCCESS! Found {len(data['objects'])} gateways:")
                for gw in data['objects']:
                    print(f"  - {gw.get('name', 'Unknown')}")
    except Exception as e:
        print(f"Error: {e}")
else:
    print("Test 4: Skipped - No Cloud Infra Token configured")
    print("You might need to add CHECKPOINT_CLOUD_INFRA_TOKEN to your .env file")

