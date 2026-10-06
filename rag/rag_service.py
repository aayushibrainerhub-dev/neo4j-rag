from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from typing import List, Dict, Optional
import uuid
import json
import requests
from datetime import datetime
import os
from dotenv import load_dotenv

from rag.neo4j_connection import get_neo4j_connection

load_dotenv()


class RAGService:
    """RAG Service for document ingestion and retrieval using Neo4j"""
    
    def __init__(self):
        """Initialize RAG service with embedding model and Neo4j connection"""
        self.neo4j_conn = get_neo4j_connection()
        
        # Initialize embedding model
        model_name = os.getenv("HF_EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2")
        self.embeddings = HuggingFaceEmbeddings(
            model_name=model_name,
            model_kwargs={'device': 'cpu'},
            encode_kwargs={'normalize_embeddings': True}
        )
        
        # Create vector index if it doesn't exist
        self.neo4j_conn.create_vector_index(index_name="document_embeddings", dimension=384)
    
    def chunk_text(self, text: str, chunk_size: int = 500, chunk_overlap: int = 50) -> List[str]:
        """
        Split text into chunks
        
        Args:
            text: Input text to chunk
            chunk_size: Size of each chunk
            chunk_overlap: Overlap between chunks
            
        Returns:
            List of text chunks
        """
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            length_function=len,
            separators=["\n\n", "\n", " ", ""]
        )
        chunks = text_splitter.split_text(text)
        return chunks
    
    def _flatten_metadata(self, metadata: Dict) -> Dict:
        """
        Flatten nested metadata to ensure Neo4j compatibility
        Neo4j only supports primitive types (string, int, float, bool) or arrays
        
        Args:
            metadata: Dictionary that may contain nested structures
            
        Returns:
            Flattened dictionary with only primitive types
        """
        flattened = {}
        
        def flatten(obj, prefix=''):
            if isinstance(obj, dict):
                for key, value in obj.items():
                    new_key = f"{prefix}{key}" if prefix else key
                    if isinstance(value, (dict, list)):
                        # Convert complex types to JSON string
                        import json
                        flattened[new_key] = json.dumps(value)
                    elif isinstance(value, (str, int, float, bool, type(None))):
                        flattened[new_key] = value
                    else:
                        # Convert other types to string
                        flattened[new_key] = str(value)
            else:
                flattened[prefix.rstrip('_')] = str(obj)
        
        flatten(metadata)
        return flattened
    
    def ingest_documents(
        self,
        text: str,
        metadata: Optional[Dict] = None,
        chunk_size: int = 500,
        chunk_overlap: int = 50
    ) -> Dict:
        """
        Ingest documents into Neo4j with embeddings
        
        Args:
            text: Text content to ingest
            metadata: Optional metadata for the document
            chunk_size: Size of text chunks
            chunk_overlap: Overlap between chunks
            
        Returns:
            Dictionary with ingestion results
        """
        # Chunk the text
        chunks = self.chunk_text(text, chunk_size, chunk_overlap)
        
        # Generate embeddings for all chunks
        embeddings = self.embeddings.embed_documents(chunks)
        
        # Prepare and flatten metadata to ensure Neo4j compatibility
        if metadata is None:
            metadata = {}
        
        # Flatten nested metadata
        flat_metadata = self._flatten_metadata(metadata)
        
        document_ids = []
        driver = self.neo4j_conn.get_driver()
        
        with driver.session() as session:
            for i, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
                doc_id = str(uuid.uuid4())
                document_ids.append(doc_id)
                
                # Create document node with embedding
                # Set metadata properties individually to avoid nested map issues
                query = """
                CREATE (d:Document)
                SET d.id = $id,
                    d.text = $text,
                    d.embedding = $embedding,
                    d.chunk_index = $chunk_index,
                    d.created_at = datetime()
                """
                
                # Add metadata properties dynamically
                params = {
                    "id": doc_id,
                    "text": chunk,
                    "embedding": embedding,
                    "chunk_index": i
                }
                
                # Add each metadata field as a separate property
                if flat_metadata:
                    metadata_sets = []
                    for key, value in flat_metadata.items():
                        # Sanitize key to be Neo4j property name compliant
                        safe_key = key.replace('.', '_').replace(' ', '_')
                        metadata_sets.append(f"d.meta_{safe_key} = ${safe_key}")
                        params[safe_key] = value
                    
                    if metadata_sets:
                        query += ",\n    " + ",\n    ".join(metadata_sets)
                
                session.run(query, **params)
        
        return {
            "message": "Documents ingested successfully",
            "num_chunks": len(chunks),
            "document_ids": document_ids
        }
    
    def similarity_search(self, query: str, top_k: int = 5) -> List[Dict]:
        """
        Perform similarity search on stored documents
        
        Args:
            query: Search query
            top_k: Number of top results to return
            
        Returns:
            List of similar documents with scores
        """
        # Generate embedding for the query
        query_embedding = self.embeddings.embed_query(query)
        
        driver = self.neo4j_conn.get_driver()
        
        with driver.session() as session:
            # Use vector similarity search
            search_query = """
            CALL db.index.vector.queryNodes('document_embeddings', $top_k, $query_embedding)
            YIELD node, score
            RETURN node.id as id,
                   node.text as text,
                   node.chunk_index as chunk_index,
                   properties(node) as all_properties,
                   score
            ORDER BY score DESC
            """
            
            result = session.run(
                search_query,
                query_embedding=query_embedding,
                top_k=top_k
            )
            
            documents = []
            for record in result:
                # Extract metadata from properties (those starting with 'meta_')
                all_props = record["all_properties"]
                metadata = {}
                
                if all_props:
                    for key, value in all_props.items():
                        if key.startswith('meta_'):
                            # Remove 'meta_' prefix and restore original key
                            original_key = key[5:].replace('_', '.')
                            # Try to parse JSON if it looks like JSON
                            if isinstance(value, str) and (value.startswith('{') or value.startswith('[')):
                                try:
                                    import json
                                    metadata[original_key] = json.loads(value)
                                except:
                                    metadata[original_key] = value
                            else:
                                metadata[original_key] = value
                
                documents.append({
                    "id": record["id"],
                    "text": record["text"],
                    "chunk_index": record["chunk_index"],
                    "metadata": metadata,
                    "score": record["score"]
                })
        
        return documents
    
    def answer_question(
        self,
        question: str,
        top_k: int = 5,
        user_context: Optional[Dict] = None
    ) -> Dict:
        """
        Answer a question using RAG
        
        Args:
            question: User question
            top_k: Number of context chunks to retrieve
            user_context: Optional user context
            
        Returns:
            Dictionary with answer and sources
        """
        # Retrieve relevant documents
        relevant_docs = self.similarity_search(question, top_k=top_k)
        
        if not relevant_docs:
            return {
                "answer": "I don't have enough information to answer this question.",
                "sources": [],
                "context_chunks": []
            }
        
        # Build context from retrieved documents
        context = "\n\n".join([doc["text"] for doc in relevant_docs])
        
        # Simple answer generation (you can integrate with an LLM here)
        # For now, we'll return the most relevant chunks
        answer = self._generate_answer(question, context)
        
        sources = [doc["id"] for doc in relevant_docs]
        
        return {
            "answer": answer,
            "sources": sources,
            "context_chunks": relevant_docs
        }
    
    def _generate_answer(self, question: str, context: str) -> str:
        """
        Generate answer from context using OpenRouter LLM
        
        Args:
            question: User question
            context: Retrieved context
            
        Returns:
            Generated answer
        """
        api_key = os.getenv("OPENROUTER_API_KEY")
        model = os.getenv("OPENROUTER_MODEL", "qwen/qwen-2-7b-instruct:free")
        
        if not api_key:
            return f"Based on the retrieved context:\n\n{context[:800]}...\n\nTo get AI-generated answers, configure OPENROUTER_API_KEY in .env"
        
        try:
            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
                "HTTP-Referer": "http://localhost:8000",
                "X-Title": "Neo4j RAG System"
            }
            
            payload = {
                "model": model,
                "messages": [
                    {
                        "role": "system",
                        "content": "You are a helpful assistant that answers questions based on the provided context. Answer concisely and accurately based only on the given information. If the context doesn't contain enough information to answer the question, say so."
                    },
                    {
                        "role": "user",
                        "content": f"Context:\n{context}\n\nQuestion: {question}\n\nAnswer:"
                    }
                ],
                "temperature": 0.7,
                "max_tokens": 500
            }
            
            response = requests.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers=headers,
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                return result["choices"][0]["message"]["content"]
            else:
                error_msg = response.json().get("error", {}).get("message", "Unknown error")
                print(f"OpenRouter API error: {error_msg}")
                return f"Based on the retrieved context:\n\n{context[:800]}..."
                
        except requests.exceptions.RequestException as e:
            print(f"Network error calling OpenRouter: {e}")
            return f"Based on the retrieved context:\n\n{context[:800]}..."
        except Exception as e:
            print(f"Error calling OpenRouter: {e}")
            return f"Based on the retrieved context:\n\n{context[:800]}..."
    
    def delete_all_documents(self):
        """Delete all documents from the database (for testing)"""
        driver = self.neo4j_conn.get_driver()
        with driver.session() as session:
            session.run("MATCH (d:Document) DETACH DELETE d")
        return {"message": "All documents deleted"}
    
    def get_document_count(self) -> int:
        """Get total number of document chunks"""
        driver = self.neo4j_conn.get_driver()
        with driver.session() as session:
            result = session.run("MATCH (d:Document) RETURN count(d) as count")
            record = result.single()
            return record["count"] if record else 0


class RAGServiceManager:
    """
    Manager class that handles all RAG operations and lifecycle
    This encapsulates all the business logic in one place
    """
    
    def __init__(self):
        """Initialize the manager"""
        self._rag_service: Optional[RAGService] = None
        self._neo4j_conn = None
    
    def startup(self):
        """Initialize connections and services on startup"""
        from rag.neo4j_connection import get_neo4j_connection
        
        self._neo4j_conn = get_neo4j_connection()
        if self._neo4j_conn.verify_connectivity():
            print("✓ Connected to Neo4j")
        else:
            print("✗ Failed to connect to Neo4j")
        
        # Initialize RAG service
        self._rag_service = RAGService()
        print(f"✓ RAG service initialized")
        print(f"  Documents in database: {self._rag_service.get_document_count()}")
    
    def shutdown(self):
        """Clean up resources on shutdown"""
        from rag.neo4j_connection import close_neo4j_connection
        close_neo4j_connection()
        self._rag_service = None
        self._neo4j_conn = None
    
    def health_check(self) -> dict:
        """Perform health check"""
        if self._neo4j_conn:
            neo4j_status = self._neo4j_conn.verify_connectivity()
            return {
                "status": "healthy" if neo4j_status else "unhealthy",
                "neo4j": "connected" if neo4j_status else "disconnected"
            }
        return {"status": "unhealthy", "neo4j": "not initialized"}
    
    def upload_document(
        self,
        text: str,
        metadata: Optional[dict] = None,
        chunk_size: int = 500,
        chunk_overlap: int = 50
    ) -> dict:
        """Upload and process a document"""
        if not self._rag_service:
            raise RuntimeError("RAG service not initialized")
        
        return self._rag_service.ingest_documents(
            text=text,
            metadata=metadata,
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap
        )
    
    def ask_question(
        self,
        question: str,
        top_k: int = 5,
        user_context: Optional[dict] = None
    ) -> dict:
        """Ask a question using RAG"""
        if not self._rag_service:
            raise RuntimeError("RAG service not initialized")
        
        return self._rag_service.answer_question(
            question=question,
            top_k=top_k,
            user_context=user_context
        )
    
    def get_stats(self) -> dict:
        """Get system statistics"""
        if not self._rag_service:
            raise RuntimeError("RAG service not initialized")
        
        document_count = self._rag_service.get_document_count()
        return {
            "total_documents": document_count,
            "status": "operational"
        }
    
    def delete_all_documents(self) -> dict:
        """Delete all documents"""
        if not self._rag_service:
            raise RuntimeError("RAG service not initialized")
        
        return self._rag_service.delete_all_documents()


# Legacy singleton support (for backward compatibility with existing scripts)
_rag_service: Optional[RAGService] = None


def get_rag_service() -> RAGService:
    """Get or create RAG service singleton (for backward compatibility)"""
    global _rag_service
    if _rag_service is None:
        _rag_service = RAGService()
    return _rag_service
