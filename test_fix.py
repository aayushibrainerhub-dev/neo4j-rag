"""
Quick test to verify the metadata fix
"""
import requests
import json

BASE_URL = "http://localhost:8000"

def test_upload_with_metadata():
    """Test document upload with various metadata types"""
    print("Testing document upload with metadata...")
    print("=" * 60)
    
    # Test 1: Simple flat metadata (should work)
    print("\n1. Testing with simple flat metadata...")
    payload1 = {
        "text": "Neo4j is a graph database.",
        "metadata": {
            "source": "docs",
            "author": "John Doe",
            "version": "1.0"
        }
    }
    
    response = requests.post(f"{BASE_URL}/api/v1/documents/upload", json=payload1)
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        print("✓ Success!")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
    else:
        print(f"✗ Failed: {response.text}")
    
    # Test 2: Nested metadata (will be flattened)
    print("\n2. Testing with nested metadata (will be flattened)...")
    payload2 = {
        "text": "Python is a programming language.",
        "metadata": {
            "source": "wikipedia",
            "details": {
                "author": "Guido van Rossum",
                "year": 1991
            }
        }
    }
    
    response = requests.post(f"{BASE_URL}/api/v1/documents/upload", json=payload2)
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        print("✓ Success!")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
    else:
        print(f"✗ Failed: {response.text}")
    
    # Test 3: Empty metadata
    print("\n3. Testing with empty metadata...")
    payload3 = {
        "text": "FastAPI is a modern web framework.",
        "metadata": {}
    }
    
    response = requests.post(f"{BASE_URL}/api/v1/documents/upload", json=payload3)
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        print("✓ Success!")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
    else:
        print(f"✗ Failed: {response.text}")
    
    print("\n" + "=" * 60)
    print("Test completed!")

def test_search():
    """Test search after upload"""
    print("\n\nTesting search...")
    print("=" * 60)
    
    payload = {
        "question": "What is Neo4j?",
        "top_k": 3
    }
    
    response = requests.post(f"{BASE_URL}/api/v1/rag/question", json=payload)
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        result = response.json()
        print("✓ Success!")
        print(f"Answer: {result['answer'][:200]}...")
        print(f"Sources: {len(result['sources'])}")
    else:
        print(f"✗ Failed: {response.text}")

if __name__ == "__main__":
    try:
        test_upload_with_metadata()
        test_search()
    except requests.exceptions.ConnectionError:
        print("❌ Error: Could not connect to the server.")
        print("Make sure the server is running: python apps/main.py")
    except Exception as e:
        print(f"❌ Error: {e}")
