"""
Shared data models for International Space Law AI Assistant
"""
from datetime import datetime
from typing import Optional, List, Dict, Any
from enum import Enum
from pydantic import BaseModel, Field


class LawType(str, Enum):
    """Types of space law"""
    TREATY = "treaty"
    CUSTOMARY = "customary"
    DOMESTIC = "domestic"
    REGULATORY = "regulatory"
    CASE_LAW = "case_law"


class Jurisdiction(str, Enum):
    """Space law jurisdictions"""
    INTERNATIONAL = "international"
    UN = "un"
    US = "us"
    EU = "eu"
    RUSSIA = "russia"
    CHINA = "china"
    OTHER = "other"


class DocumentStatus(str, Enum):
    """Processing status of documents"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class SpaceLawDocument(BaseModel):
    """Model for space law documents"""
    id: Optional[str] = None
    title: str
    content: str
    source_url: str
    law_type: LawType
    jurisdiction: Jurisdiction
    date_published: Optional[datetime] = None
    date_collected: datetime = Field(default_factory=datetime.utcnow)
    keywords: List[str] = []
    summary: Optional[str] = None
    status: DocumentStatus = DocumentStatus.PENDING
    metadata: Dict[str, Any] = {}
    
    class Config:
        use_enum_values = True


class SpaceEvent(BaseModel):
    """Model for space events"""
    id: Optional[str] = None
    title: str
    description: str
    event_type: str  # launch, incident, treaty_signature, etc.
    date_occurred: datetime
    date_collected: datetime = Field(default_factory=datetime.utcnow)
    participants: List[str] = []
    location: Optional[str] = None
    legal_implications: Optional[str] = None
    metadata: Dict[str, Any] = {}


class LegalAnalysis(BaseModel):
    """Model for legal analysis results"""
    id: Optional[str] = None
    document_id: str
    analysis_type: str  # customary_vs_treaty, jurisdictional_analysis, etc.
    results: Dict[str, Any]
    confidence_score: float = Field(ge=0.0, le=1.0)
    date_analyzed: datetime = Field(default_factory=datetime.utcnow)
    methodology: str
    analyst_notes: Optional[str] = None


class JurisdictionalBoundary(BaseModel):
    """Model for jurisdictional boundary analysis"""
    id: Optional[str] = None
    jurisdiction: Jurisdiction
    boundary_type: str  # territorial, functional, etc.
    description: str
    legal_basis: List[str] = []
    conflicts: List[str] = []
    confidence_score: float = Field(ge=0.0, le=1.0)
    date_analyzed: datetime = Field(default_factory=datetime.utcnow)


class JusCogensRecommendation(BaseModel):
    """Model for jus cogens recommendations"""
    id: Optional[str] = None
    principle: str
    description: str
    legal_basis: List[str] = []
    supporting_documents: List[str] = []
    opposition_arguments: List[str] = []
    recommendation_strength: float = Field(ge=0.0, le=1.0)
    implementation_guidance: Optional[str] = None
    date_generated: datetime = Field(default_factory=datetime.utcnow)


class APIResponse(BaseModel):
    """Standard API response format"""
    success: bool
    message: str
    data: Optional[Dict[str, Any]] = None
    errors: Optional[List[str]] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)


