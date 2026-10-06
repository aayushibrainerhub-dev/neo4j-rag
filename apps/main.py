from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from schemas.rag import (
    DocumentUploadRequest,
    DocumentUploadResponse,
    QuestionRequest,
    QuestionResponse
)
from rag.rag_service import RAGServiceManager


# Initialize RAG service manager
rag_manager = RAGServiceManager()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifecycle manager for FastAPI app"""
    # Startup
    print("Starting up...")
    rag_manager.startup()
    
    yield
    
    # Shutdown
    print("Shutting down...")
    rag_manager.shutdown()


app = FastAPI(
    title="Neo4j RAG API",
    description="RAG system using Neo4j for vector storage",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Neo4j RAG API",
        "version": "1.0.0",
        "endpoints": {
            "health": "/health",
            "upload": "/api/v1/documents/upload",
            "question": "/api/v1/rag/question",
            "stats": "/api/v1/stats",
            "delete_all": "/api/v1/documents/delete-all"
        }
    }


@app.get("/health")
async def health():
    """Health check endpoint"""
    return rag_manager.health_check()


@app.post("/api/v1/documents/upload", response_model=DocumentUploadResponse)
async def upload_document(request: DocumentUploadRequest):
    """
    Upload and process documents into the RAG system
    
    Args:
        request: Document upload request with text and metadata
        
    Returns:
        Upload response with document IDs
    """
    try:
        result = rag_manager.upload_document(
            text=request.text,
            metadata=request.metadata,
            chunk_size=request.chunk_size or 500,
            chunk_overlap=request.chunk_overlap or 50
        )
        return DocumentUploadResponse(**result)
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to upload document: {str(e)}")


@app.post("/api/v1/rag/question", response_model=QuestionResponse)
async def ask_question(request: QuestionRequest):
    """
    Ask a question and get an answer using RAG
    
    Args:
        request: Question request
        
    Returns:
        Answer with sources and context
    """
    try:
        user_context = {
            "session_id": request.session_id,
            "user_id": request.user_id,
            "user_name": request.user_name,
            "upload_id": request.upload_id
        }
        
        result = rag_manager.ask_question(
            question=request.question,
            top_k=request.top_k or 5,
            user_context=user_context
        )
        
        return QuestionResponse(
            answer=result["answer"],
            sources=result["sources"],
            context_chunks=result.get("context_chunks", []),
            session_id=request.session_id,
            upload_id=request.upload_id,
            user_name=request.user_name,
            user_id=request.user_id
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to answer question: {str(e)}")


@app.get("/api/v1/stats")
async def get_stats():
    """Get statistics about the RAG system"""
    try:
        return rag_manager.get_stats()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get stats: {str(e)}")


@app.delete("/api/v1/documents/delete-all")
async def delete_all_documents():
    """Delete all documents from the database (use with caution!)"""
    try:
        return rag_manager.delete_all_documents()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete documents: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
