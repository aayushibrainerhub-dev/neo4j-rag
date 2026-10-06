from pydantic import BaseModel, Field
from typing import Optional, Dict, Any


class DocumentUploadRequest(BaseModel):
    text: str
    metadata: Optional[Dict[str, Any]] = Field(
        default_factory=dict,
        description="Metadata for the document. Nested objects will be flattened. Example: {'source': 'docs', 'author': 'John'}"
    )
    chunk_size: Optional[int] = 500
    chunk_overlap: Optional[int] = 50
    
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "text": "Your document text here...",
                    "metadata": {
                        "source": "documentation",
                        "author": "John Doe",
                        "version": "1.0"
                    },
                    "chunk_size": 500,
                    "chunk_overlap": 50
                }
            ]
        }
    }


class DocumentUploadResponse(BaseModel):
    message: str
    num_chunks: int
    document_ids: list[str]


class QuestionRequest(BaseModel):
    question: str
    upload_id: Optional[str] = None
    session_id: Optional[str] = None
    user_name: Optional[str] = None
    user_id: Optional[str] = None
    top_k: Optional[int] = 5


class QuestionResponse(BaseModel):
    answer: str
    sources: list[str]
    session_id: Optional[str] = None
    upload_id: Optional[str] = None
    user_name: Optional[str] = None
    user_id: Optional[str] = None
    available_users: list[dict[str, str]] = Field(default_factory=list)
    context_chunks: list[dict] = Field(default_factory=list)