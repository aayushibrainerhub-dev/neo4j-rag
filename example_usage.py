"""
Example usage of the Neo4j RAG system
This script demonstrates all the key features
"""
import time
from rag.rag_service import get_rag_service
from rag.neo4j_connection import get_neo4j_connection

def main():
    print("=" * 70)
    print("Neo4j RAG System - Example Usage")
    print("=" * 70)
    print()
    
    # 1. Check connection
    print("1. Checking Neo4j connection...")
    conn = get_neo4j_connection()
    if conn.verify_connectivity():
        print("   ✓ Connected to Neo4j successfully")
    else:
        print("   ✗ Failed to connect to Neo4j")
        return
    print()
    
    # 2. Initialize RAG service
    print("2. Initializing RAG service...")
    rag_service = get_rag_service()
    print("   ✓ RAG service initialized")
    print(f"   Current documents in database: {rag_service.get_document_count()}")
    print()
    
    # 3. Ingest sample documents
    print("3. Ingesting sample documents...")
    
    documents = [
        {
            "text": """
            Neo4j is a graph database management system developed by Neo4j, Inc. 
            Described by its developers as an ACID-compliant transactional database with native 
            graph storage and processing. Neo4j is available in a community edition and an 
            enterprise edition. The community edition is free and open-source software, while 
            the enterprise edition is commercial software.
            
            Neo4j stores data in nodes connected by directed, typed relationships with properties 
            on both. It uses the property graph data model. Both nodes and relationships can 
            contain properties, which are key-value pairs that store data.
            
            Cypher is Neo4j's graph query language that allows users to store and retrieve data 
            from the graph database. Cypher's syntax provides a visual and logical way to match 
            patterns of nodes and relationships in the graph.
            """,
            "metadata": {"source": "neo4j_overview", "topic": "database"}
        },
        {
            "text": """
            Vector databases are specialized databases designed to store and query high-dimensional 
            vectors efficiently. These vectors typically represent embeddings of data like text, 
            images, or audio. Vector databases enable similarity search, where you can find items 
            similar to a query vector.
            
            Common use cases for vector databases include:
            - Semantic search: Finding documents based on meaning rather than keywords
            - Recommendation systems: Finding similar products or content
            - RAG (Retrieval-Augmented Generation): Providing context to language models
            - Anomaly detection: Finding outliers in high-dimensional data
            
            Neo4j supports vector indexing and similarity search through its vector index feature,
            combining graph relationships with vector similarity for powerful hybrid queries.
            """,
            "metadata": {"source": "vector_databases", "topic": "embeddings"}
        },
        {
            "text": """
            Retrieval-Augmented Generation (RAG) is a technique that combines information retrieval 
            with text generation. It works by:
            
            1. Retrieving relevant documents from a knowledge base using semantic search
            2. Providing these documents as context to a language model
            3. Generating an answer based on the retrieved context
            
            RAG has several advantages:
            - Reduces hallucinations by grounding responses in real data
            - Allows models to access up-to-date information beyond training data
            - Enables transparency by showing source documents
            - More cost-effective than fine-tuning for many use cases
            
            Neo4j is particularly well-suited for RAG applications because it can store both 
            document embeddings and maintain relationships between entities, enabling more 
            sophisticated retrieval strategies.
            """,
            "metadata": {"source": "rag_explanation", "topic": "ai"}
        }
    ]
    
    for i, doc in enumerate(documents, 1):
        result = rag_service.ingest_documents(
            text=doc["text"],
            metadata=doc["metadata"],
            chunk_size=400,
            chunk_overlap=50
        )
        print(f"   ✓ Document {i} ingested: {result['num_chunks']} chunks created")
        time.sleep(0.5)  # Small delay for demo purposes
    
    print()
    print(f"   Total documents in database: {rag_service.get_document_count()}")
    print()
    
    # 4. Perform similarity searches
    print("4. Performing similarity searches...")
    print()
    
    queries = [
        "What is Neo4j and how does it store data?",
        "Explain vector databases and their use cases",
        "How does RAG work?",
        "What query language does Neo4j use?",
    ]
    
    for query in queries:
        print(f"   Query: {query}")
        print("   " + "-" * 66)
        
        results = rag_service.similarity_search(query, top_k=3)
        
        for j, result in enumerate(results, 1):
            print(f"   Result {j} (score: {result['score']:.4f}):")
            print(f"   Topic: {result['metadata'].get('topic', 'N/A')}")
            print(f"   Text: {result['text'][:150]}...")
            print()
        
        print()
    
    # 5. Ask questions with RAG
    print("5. Asking questions using RAG...")
    print()
    
    questions = [
        "What makes Neo4j different from other databases?",
        "What are the benefits of using RAG?",
        "How can vector databases be used?",
    ]
    
    for question in questions:
        print(f"   Question: {question}")
        print("   " + "-" * 66)
        
        answer_result = rag_service.answer_question(question, top_k=3)
        
        print(f"   Answer: {answer_result['answer'][:300]}...")
        print(f"   Sources used: {len(answer_result['sources'])}")
        print()
    
    # 6. Statistics
    print("6. Final Statistics")
    print("   " + "-" * 66)
    print(f"   Total document chunks: {rag_service.get_document_count()}")
    print()
    
    print("=" * 70)
    print("Demo completed successfully!")
    print("=" * 70)
    print()
    print("Next steps:")
    print("  - Start the API: python apps/main.py")
    print("  - View docs: http://localhost:8000/docs")
    print("  - Run tests: python test_rag.py")
    print()


if __name__ == "__main__":
    main()
