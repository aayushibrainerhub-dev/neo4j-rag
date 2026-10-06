# Neo4j RAG System

A complete RAG (Retrieval-Augmented Generation) system using Neo4j as a vector database for storing and retrieving document embeddings.

## Features

- 📄 **Document Ingestion**: Upload and chunk documents with automatic embedding generation
- 🔍 **Vector Similarity Search**: Fast semantic search using Neo4j vector indexes
- 🤖 **RAG Question Answering**: Retrieve relevant context and answer questions
- 🚀 **FastAPI Backend**: RESTful API with automatic documentation
- 🐳 **Docker Support**: Easy deployment with Docker Compose

## Architecture

```
┌─────────────────┐
│   FastAPI App   │
└────────┬────────┘
         │
         ▼
┌─────────────────┐       ┌──────────────────┐
│   RAG Service   │◄─────►│  HuggingFace     │
│                 │       │  Embeddings      │
└────────┬────────┘       └──────────────────┘
         │
         ▼
┌─────────────────┐
│  Neo4j Vector   │
│    Database     │
└─────────────────┘
```

## Prerequisites

- Python 3.11+
- Docker & Docker Compose
- uv (Python package manager)

## Installation

1. **Clone the repository**
   ```bash
   cd /home/brainerhub/Downloads/neo4j-demo
   ```

2. **Install dependencies**
   ```bash
   uv sync
   ```

3. **Start Neo4j database**
   ```bash
   docker-compose up -d
   ```

4. **Access Neo4j Browser**
   - URL: http://localhost:7474
   - Username: `neo4j`
   - Password: `password123`

## Usage

### Start the API Server

```bash
python apps/main.py
```

The server will start at `http://localhost:8000`

### API Documentation

Once the server is running, visit:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### API Endpoints

#### 1. Upload Documents
```bash
curl -X POST "http://localhost:8000/api/v1/documents/upload" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Your document text here...",
    "metadata": {"source": "example"},
    "chunk_size": 500,
    "chunk_overlap": 50
  }'
```

#### 2. Ask Questions
```bash
curl -X POST "http://localhost:8000/api/v1/rag/question" \
  -H "Content-Type: application/json" \
  -d '{
    "question": "What is Neo4j?",
    "top_k": 5
  }'
```

#### 3. Get Statistics
```bash
curl -X GET "http://localhost:8000/api/v1/stats"
```

#### 4. Health Check
```bash
curl -X GET "http://localhost:8000/health"
```

### Test the System

Run the test script to verify everything works:

```bash
python test_rag.py
```

## How It Works

### 1. Document Ingestion
- Text is split into chunks using RecursiveCharacterTextSplitter
- Each chunk is embedded using HuggingFace's `all-MiniLM-L6-v2` model (384 dimensions)
- Embeddings are stored in Neo4j with metadata

### 2. Vector Search
- User query is embedded using the same model
- Neo4j vector index performs cosine similarity search
- Top K most relevant chunks are retrieved

### 3. Answer Generation
- Retrieved chunks provide context
- Context is formatted and returned (ready for LLM integration)

## Neo4j Schema

```cypher
(:Document {
  id: String,              # Unique document ID
  text: String,            # Chunk text content
  embedding: List[Float],  # 384-dimensional embedding vector
  chunk_index: Integer,    # Position in original document
  created_at: DateTime,    # Timestamp
  metadata: Map           # Custom metadata
})
```

## Configuration

### Environment Variables (.env)

```env
HF_TOKEN=your_huggingface_token
HF_EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2
```

### Neo4j Connection (docker-compose.yml)

```yaml
NEO4J_AUTH: neo4j/password123
```

Update `rag/neo4j_connection.py` if you change credentials.

## Extending the System

### Add LLM Integration

Replace the `_generate_answer` method in `rag/rag_service.py` with your preferred LLM:

```python
from openai import OpenAI

def _generate_answer(self, question: str, context: str) -> str:
    client = OpenAI()
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "Answer based on the context."},
            {"role": "user", "content": f"Context: {context}\n\nQuestion: {question}"}
        ]
    )
    return response.choices[0].message.content
```

### Add File Upload Support

```python
from fastapi import UploadFile, File

@app.post("/api/v1/documents/upload-file")
async def upload_file(file: UploadFile = File(...)):
    content = await file.read()
    text = content.decode('utf-8')
    # Process with RAG service
```

### Add Authentication

```python
from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer

security = HTTPBearer()

@app.post("/api/v1/rag/question")
async def ask_question(request: QuestionRequest, token = Depends(security)):
    # Verify token
    # Process request
```

## Troubleshooting

### Neo4j Connection Failed
```bash
# Check if Neo4j is running
docker ps

# View Neo4j logs
docker logs neo4j

# Restart Neo4j
docker-compose restart neo4j
```

### Embedding Model Download Issues
```bash
# Pre-download the model
python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')"
```

### Vector Index Issues
```cypher
// Drop and recreate index in Neo4j Browser
DROP INDEX document_embeddings IF EXISTS;

// Restart the application to recreate
```

## Performance Tips

1. **Chunk Size**: Adjust based on your content (200-1000 tokens)
2. **Overlap**: Use 10-20% of chunk size for better context
3. **Top K**: Start with 3-5 chunks for context
4. **Batch Processing**: Ingest large documents in batches

## License

MIT License

## Contributing

Contributions welcome! Please open an issue or submit a PR.
