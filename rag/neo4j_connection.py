from neo4j import GraphDatabase
import os
from typing import Optional

class Neo4jConnection:
    """Manages Neo4j database connection"""
    
    def __init__(self, uri: str = "bolt://localhost:7687", user: str = "neo4j", password: str = "password123"):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))
    
    def close(self):
        """Close the driver connection"""
        if self.driver:
            self.driver.close()
    
    def verify_connectivity(self) -> bool:
        """Verify database connection"""
        try:
            self.driver.verify_connectivity()
            return True
        except Exception as e:
            print(f"Connection failed: {e}")
            return False
    
    def create_vector_index(self, index_name: str = "document_embeddings", dimension: int = 384):
        """
        Create a vector index in Neo4j for similarity search
        
        Args:
            index_name: Name of the vector index
            dimension: Dimension of the embedding vectors (384 for all-MiniLM-L6-v2)
        """
        with self.driver.session() as session:
            # Check if index already exists
            result = session.run("SHOW INDEXES")
            existing_indexes = [record["name"] for record in result]
            
            if index_name in existing_indexes:
                print(f"Vector index '{index_name}' already exists")
                return
            
            # Create vector index
            query = f"""
            CREATE VECTOR INDEX {index_name} IF NOT EXISTS
            FOR (d:Document)
            ON d.embedding
            OPTIONS {{
                indexConfig: {{
                    `vector.dimensions`: {dimension},
                    `vector.similarity_function`: 'cosine'
                }}
            }}
            """
            session.run(query)
            print(f"Vector index '{index_name}' created successfully")
    
    def get_driver(self):
        """Return the driver instance"""
        return self.driver

# Singleton instance
_connection: Optional[Neo4jConnection] = None

def get_neo4j_connection() -> Neo4jConnection:
    """Get or create Neo4j connection singleton"""
    global _connection
    if _connection is None:
        _connection = Neo4jConnection()
    return _connection

def close_neo4j_connection():
    """Close the Neo4j connection"""
    global _connection
    if _connection:
        _connection.close()
        _connection = None