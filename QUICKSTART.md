# Quick Start Guide

## Step-by-Step Setup

### 1. Start Neo4j Database

```bash
docker-compose up -d
```

Wait a few seconds for Neo4j to start, then verify it's running:
```bash
docker ps
```

You should see the `neo4j` container running.

### 2. Verify Neo4j is Accessible

Open your browser and go to: http://localhost:7474

- **Username**: `neo4j`
- **Password**: `password123`

### 3. Start the RAG API Server

```bash
python apps/main.py
```

You should see output like:
```
Starting up...
✓ Connected to Neo4j
✓ RAG service initialized
  Documents in database: 0
INFO:     Started server process [xxxxx]
INFO:     Uvicorn running on http://0.0.0.0:8000
```

### 4. Test the System

Open a new terminal and run:

```bash
python test_rag.py
```

This will:
1. Check health status
2. Upload a sample document about Neo4j
3. Show statistics
4. Ask several questions and display answers

## Manual Testing with curl

### Upload a Document

```bash
curl -X POST "http://localhost:8000/api/v1/documents/upload" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Python is a high-level programming language. It was created by Guido van Rossum and released in 1991. Python emphasizes code readability with its notable use of significant indentation.",
    "metadata": {"source": "python_intro", "language": "en"}
  }'
```

### Ask a Question

```bash
curl -X POST "http://localhost:8000/api/v1/rag/question" \
  -H "Content-Type: application/json" \
  -d '{
    "question": "Who created Python?",
    "top_k": 3
  }'
```

### Check Statistics

```bash
curl -X GET "http://localhost:8000/api/v1/stats"
```

## Access API Documentation

Open your browser:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## Verify in Neo4j Browser

1. Go to http://localhost:7474
2. Run this Cypher query:

```cypher
MATCH (d:Document)
RETURN d.text, d.chunk_index, d.metadata
LIMIT 10
```

You should see your uploaded documents!

## Common Issues

### Neo4j won't start
```bash
# Stop and remove containers
docker-compose down

# Remove volumes
docker volume rm neo4j-demo_neo4j_data neo4j-demo_neo4j_logs

# Start again
docker-compose up -d
```

### Port already in use
```bash
# Check what's using port 8000
lsof -i :8000

# Kill the process or change port in apps/main.py
uvicorn.run(app, host="0.0.0.0", port=8001)
```

### Connection refused
- Make sure Neo4j is running: `docker ps`
- Check Neo4j logs: `docker logs neo4j`
- Wait 10-15 seconds after starting Neo4j

## Next Steps

1. **Integrate an LLM**: Modify `_generate_answer()` in `rag/rag_service.py` to use OpenAI, Anthropic, or local models
2. **Add file upload**: Support PDF, DOCX, TXT files
3. **Add user authentication**: Secure your endpoints
4. **Deploy to production**: Use Docker container for the API

## Stop Everything

```bash
# Stop the API (Ctrl+C in the terminal)

# Stop Neo4j
docker-compose down
```

Enjoy building with Neo4j RAG! 🚀
