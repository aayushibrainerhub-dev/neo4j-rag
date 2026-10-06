"""
Test script for Neo4j RAG system
Run this to test the RAG functionality
"""
import requests
import json

BASE_URL = "http://localhost:8000"


def test_health():
    """Test health endpoint"""
    print("=" * 50)
    print("Testing Health Endpoint")
    print("=" * 50)
    response = requests.get(f"{BASE_URL}/health")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    print()


def test_upload_document():
    """Test document upload"""
    print("=" * 50)
    print("Testing Document Upload")
    print("=" * 50)
    
    # Sample document
    sample_text = """
    Neo4j is a graph database management system developed by Neo4j, Inc.
    It is an ACID-compliant transactional database with native graph storage and processing.
    Neo4j is available in both open-source and commercial versions.
    
    The core of Neo4j is written in Java, and it provides a web interface and APIs for various programming languages.
    Neo4j uses the property graph data model, where nodes and relationships can have properties.
    
    Neo4j supports the Cypher query language, which is a declarative graph query language.
    Cypher allows users to express graph patterns and traverse the graph efficiently.
    
    Neo4j is widely used for social networks, recommendation engines, fraud detection, and knowledge graphs.
    """
    
    payload = {
        "text": sample_text,
        "metadata": {
            "source": "neo4j_info",
            "topic": "database"
        },
        "chunk_size": 300,
        "chunk_overlap": 50
    }
    
    response = requests.post(f"{BASE_URL}/api/v1/documents/upload", json=payload)
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    print()


def test_stats():
    """Test stats endpoint"""
    print("=" * 50)
    print("Testing Stats Endpoint")
    print("=" * 50)
    response = requests.get(f"{BASE_URL}/api/v1/stats")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    print()


def test_ask_question():
    """Test question answering"""
    print("=" * 50)
    print("Testing Question Answering")
    print("=" * 50)
    
    questions = [
        "What is Neo4j?",
        "What query language does Neo4j use?",
        "What are some use cases for Neo4j?",
    ]
    
    for question in questions:
        print(f"\nQuestion: {question}")
        print("-" * 50)
        
        payload = {
            "question": question,
            "top_k": 3
        }
        
        response = requests.post(f"{BASE_URL}/api/v1/rag/question", json=payload)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"Answer: {result['answer']}")
            print(f"Number of sources: {len(result['sources'])}")
            print(f"Context chunks: {len(result['context_chunks'])}")
        else:
            print(f"Error: {response.text}")
        print()


def main():
    """Run all tests"""
    try:
        # Test health
        test_health()
        
        # Upload document
        test_upload_document()
        
        # Check stats
        test_stats()
        
        # Ask questions
        test_ask_question()
        
        print("=" * 50)
        print("All tests completed!")
        print("=" * 50)
        
    except requests.exceptions.ConnectionError:
        print("❌ Error: Could not connect to the server.")
        print("Make sure the server is running: python apps/main.py")
    except Exception as e:
        print(f"❌ Error: {e}")


if __name__ == "__main__":
    main()
