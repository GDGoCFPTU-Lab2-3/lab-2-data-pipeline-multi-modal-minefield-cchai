from pydantic import BaseModel, Field, field_validator, ConfigDict
from typing import Optional, Literal, Dict, Any
from datetime import datetime, timezone

# ==========================================
# ROLE 1: LEAD DATA ARCHITECT
# ==========================================
# Your task is to define the Unified Schema for all sources.
# This is v1. Note: A breaking change is coming at 11:00 AM!

class UnifiedDocument(BaseModel):
    """
    Unified Schema for all data sources (PDF, CSV, HTML, Video/Transcript, Code).
    This is v1 of the schema. Be prepared for v2 migration at 11:00 AM!
    """
    model_config = ConfigDict(extra='ignore')  # Ignore unknown fields safely

    document_id: str = Field(..., description="Unique ID for the document")
    content: str = Field(..., description="The main text content, summary, or cleaned transcript")
    source_type: Literal['PDF', 'CSV', 'HTML', 'Transcript', 'Video', 'Code'] = Field(
        ..., description="Strict validation for source types"
    )
    author: Optional[str] = Field("Unknown", description="Author of the document if available")
    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="Processing timestamp in UTC"
    )

    # Primary flexible metadata dict
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Source-specific metadata")

    # Alias for backward compat with forensic_agent (reads 'source_metadata')
    source_metadata: Dict[str, Any] = Field(default_factory=dict, description="Alias of metadata for forensic agent")

    # Schema Versioning
    schema_version: str = Field("v1", description="Current version of the schema")

    @field_validator('content')
    @classmethod
    def strip_whitespace(cls, v: str) -> str:
        """Automatically clean leading/trailing whitespace from content."""
        return v.strip() if isinstance(v, str) else v