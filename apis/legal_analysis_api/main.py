"""
Legal Analysis API for International Space Law AI Assistant
Processes classified data to distinguish customary from treaty law and identify jurisdictional boundaries
"""
import asyncio
import logging
from datetime import datetime
from typing import List, Dict, Any, Optional, Tuple
import uvicorn
from fastapi import FastAPI, HTTPException, BackgroundTasks, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import json
import uuid
import sys
import os
import re
from collections import defaultdict, Counter

# Add parent directories to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from shared.models import (
    SpaceLawDocument, LegalAnalysis, JurisdictionalBoundary, 
    JusCogensRecommendation, APIResponse, LawType, Jurisdiction
)
from database.connection import db_manager

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Space Law Legal Analysis API",
    description="API for analyzing space law documents and identifying legal patterns",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class AnalysisRequest(BaseModel):
    """Request model for analysis operations"""
    document_ids: List[str]
    analysis_types: List[str] = ["customary_vs_treaty", "jurisdictional_analysis"]
    include_jus_cogens: bool = True


class JurisdictionalAnalysisRequest(BaseModel):
    """Request model for jurisdictional analysis"""
    jurisdiction: str
    boundary_type: str = "territorial"


class CustomaryLawIndicators:
    """Indicators for identifying customary international law"""
    
    CUSTOMARY_INDICATORS = [
        "state practice", "opinio juris", "general practice", "accepted as law",
        "consistent practice", "widespread acceptance", "universal recognition",
        "long-standing practice", "established custom", "international custom"
    ]
    
    TREATY_INDICATORS = [
        "treaty", "convention", "agreement", "protocol", "signed", "ratified",
        "entered into force", "signatory", "party to", "binding obligation"
    ]
    
    JUS_COGENS_INDICATORS = [
        "peremptory norm", "jus cogens", "fundamental principle", "non-derogable",
        "absolute prohibition", "universal prohibition", "overriding norm",
        "hierarchy of norms", "superior norm"
    ]


class LegalAnalyzer:
    """Legal analysis engine for space law documents"""
    
    def __init__(self):
        self.customary_indicators = CustomaryLawIndicators()
    
    async def analyze_customary_vs_treaty(self, document: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze whether a document represents customary or treaty law"""
        content = (document.get('content', '') + ' ' + document.get('title', '')).lower()
        
        # Count indicators
        customary_count = sum(1 for indicator in self.customary_indicators.CUSTOMARY_INDICATORS 
                            if indicator in content)
        treaty_count = sum(1 for indicator in self.customary_indicators.TREATY_INDICATORS 
                         if indicator in content)
        
        # Analyze patterns
        patterns = self._analyze_legal_patterns(content)
        
        # Determine classification
        if treaty_count > customary_count and treaty_count > 2:
            classification = "treaty_law"
            confidence = min(0.9, 0.6 + (treaty_count * 0.1))
        elif customary_count > treaty_count and customary_count > 1:
            classification = "customary_law"
            confidence = min(0.9, 0.6 + (customary_count * 0.1))
        else:
            classification = "mixed_or_uncertain"
            confidence = 0.5
        
        # Check for jus cogens indicators
        jus_cogens_score = self._calculate_jus_cogens_score(content)
        
        return {
            "classification": classification,
            "confidence_score": confidence,
            "customary_indicators_found": customary_count,
            "treaty_indicators_found": treaty_count,
            "jus_cogens_score": jus_cogens_score,
            "legal_patterns": patterns,
            "reasoning": self._generate_reasoning(classification, customary_count, treaty_count)
        }
    
    def _analyze_legal_patterns(self, content: str) -> Dict[str, Any]:
        """Analyze legal language patterns"""
        patterns = {
            "binding_language": len(re.findall(r'\b(shall|must|obliged|required|binding)\b', content)),
            "recommendatory_language": len(re.findall(r'\b(should|may|encouraged|recommended)\b', content)),
            "prohibitive_language": len(re.findall(r'\b(prohibited|forbidden|not allowed|shall not)\b', content)),
            "rights_language": len(re.findall(r'\b(right|entitled|privilege|freedom)\b', content)),
            "duty_language": len(re.findall(r'\b(duty|obligation|responsibility|liability)\b', content))
        }
        
        return patterns
    
    def _calculate_jus_cogens_score(self, content: str) -> float:
        """Calculate jus cogens score for the content"""
        jus_cogens_count = sum(1 for indicator in self.customary_indicators.JUS_COGENS_INDICATORS 
                             if indicator in content)
        
        # Base score on presence of jus cogens indicators
        if jus_cogens_count >= 3:
            return 0.8
        elif jus_cogens_count >= 2:
            return 0.6
        elif jus_cogens_count >= 1:
            return 0.4
        else:
            return 0.2
    
    def _generate_reasoning(self, classification: str, customary_count: int, treaty_count: int) -> str:
        """Generate reasoning for the classification"""
        if classification == "treaty_law":
            return f"Document classified as treaty law based on {treaty_count} treaty indicators found, indicating formal international agreement."
        elif classification == "customary_law":
            return f"Document classified as customary law based on {customary_count} customary law indicators, suggesting established state practice."
        else:
            return f"Mixed classification due to similar indicators for both treaty ({treaty_count}) and customary ({customary_count}) law."
    
    async def analyze_jurisdictional_boundaries(self, documents: List[Dict[str, Any]]) -> List[JurisdictionalBoundary]:
        """Analyze jurisdictional boundaries from documents"""
        boundaries = []
        
        # Group documents by jurisdiction
        jurisdiction_docs = defaultdict(list)
        for doc in documents:
            jurisdiction_docs[doc.get('jurisdiction', 'other')].append(doc)
        
        # Analyze each jurisdiction
        for jurisdiction, docs in jurisdiction_docs.items():
            boundary = await self._analyze_jurisdiction_boundary(jurisdiction, docs)
            boundaries.append(boundary)
        
        return boundaries
    
    async def _analyze_jurisdiction_boundary(self, jurisdiction: str, documents: List[Dict[str, Any]]) -> JurisdictionalBoundary:
        """Analyze boundary for a specific jurisdiction"""
        all_content = ' '.join([doc.get('content', '') + ' ' + doc.get('title', '') 
                               for doc in documents])
        
        # Extract legal basis
        legal_basis = self._extract_legal_basis(all_content)
        
        # Identify conflicts
        conflicts = self._identify_jurisdictional_conflicts(all_content, jurisdiction)
        
        # Calculate confidence based on document count and content quality
        confidence = min(0.9, 0.5 + (len(documents) * 0.05) + (len(legal_basis) * 0.1))
        
        boundary = JurisdictionalBoundary(
            id=str(uuid.uuid4()),
            jurisdiction=Jurisdiction(jurisdiction),
            boundary_type="functional",  # Default to functional boundaries
            description=f"Jurisdictional analysis for {jurisdiction} based on {len(documents)} documents",
            legal_basis=legal_basis,
            conflicts=conflicts,
            confidence_score=confidence
        )
        
        return boundary
    
    def _extract_legal_basis(self, content: str) -> List[str]:
        """Extract legal basis from content"""
        # Look for references to specific treaties, laws, or principles
        legal_references = re.findall(r'\b[A-Z][a-z]+ (?:\w+ )*(?:Treaty|Convention|Agreement|Act|Law|Code)\b', content)
        legal_principles = re.findall(r'\b(?:principle|rule|norm) (?:of|for) [a-z\s]+\b', content)
        
        return list(set(legal_references + legal_principles))[:10]  # Limit to 10
    
    def _identify_jurisdictional_conflicts(self, content: str, jurisdiction: str) -> List[str]:
        """Identify potential jurisdictional conflicts"""
        conflicts = []
        
        # Look for conflict indicators
        conflict_keywords = ['conflict', 'dispute', 'overlap', 'contradiction', 'incompatible']
        for keyword in conflict_keywords:
            if keyword in content.lower():
                # Extract context around the conflict
                pattern = rf'.{{0,50}}{keyword}.{{0,50}}'
                matches = re.findall(pattern, content, re.IGNORECASE)
                conflicts.extend(matches[:3])  # Limit to 3 conflicts
        
        return conflicts
    
    async def generate_jus_cogens_recommendations(self, documents: List[Dict[str, Any]]) -> List[JusCogensRecommendation]:
        """Generate jus cogens recommendations based on document analysis"""
        recommendations = []
        
        # Analyze all documents for jus cogens patterns
        all_content = ' '.join([doc.get('content', '') for doc in documents])
        
        # Identify potential jus cogens principles
        principles = self._identify_jus_cogens_principles(all_content)
        
        for principle in principles:
            recommendation = await self._create_jus_cogens_recommendation(principle, documents)
            recommendations.append(recommendation)
        
        return recommendations
    
    def _identify_jus_cogens_principles(self, content: str) -> List[str]:
        """Identify potential jus cogens principles from content"""
        principles = []
        
        # Common space law principles that might qualify as jus cogens
        space_principles = [
            "peaceful use of outer space",
            "non-appropriation of outer space",
            "freedom of exploration and use",
            "benefit and interests of all countries",
            "international cooperation",
            "state responsibility for national activities",
            "avoidance of harmful contamination"
        ]
        
        for principle in space_principles:
            if principle in content.lower():
                principles.append(principle)
        
        return principles
    
    async def _create_jus_cogens_recommendation(self, principle: str, documents: List[Dict[str, Any]]) -> JusCogensRecommendation:
        """Create a jus cogens recommendation for a specific principle"""
        # Find supporting documents
        supporting_docs = [doc['id'] for doc in documents if principle in doc.get('content', '').lower()]
        
        # Calculate recommendation strength
        strength = min(0.9, 0.3 + (len(supporting_docs) * 0.1))
        
        recommendation = JusCogensRecommendation(
            id=str(uuid.uuid4()),
            principle=principle.title(),
            description=f"Recommendation for recognizing '{principle}' as a peremptory norm of international space law",
            legal_basis=[f"Found in {len(supporting_docs)} documents"],
            supporting_documents=supporting_docs,
            opposition_arguments=["Requires further state practice analysis"],
            recommendation_strength=strength,
            implementation_guidance="Monitor state practice and opinio juris for this principle"
        )
        
        return recommendation


# Global analyzer instance
analyzer = LegalAnalyzer()


@app.on_event("startup")
async def startup_event():
    """Initialize on startup"""
    logger.info("Legal Analysis API started successfully")


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "timestamp": datetime.utcnow()}


@app.post("/analyze/customary-vs-treaty", response_model=APIResponse)
async def analyze_customary_vs_treaty(request: AnalysisRequest):
    """Analyze documents to distinguish customary from treaty law"""
    try:
        results = []
        
        with db_manager.get_connection() as conn:
            cursor = conn.cursor()
            
            for doc_id in request.document_ids:
                cursor.execute("SELECT * FROM space_law_documents WHERE id = ?", (doc_id,))
                row = cursor.fetchone()
                
                if row:
                    document = dict(row)
                    # Convert JSON fields
                    if document.get('keywords'):
                        document['keywords'] = json.loads(document['keywords'])
                    if document.get('metadata'):
                        document['metadata'] = json.loads(document['metadata'])
                    
                    analysis = await analyzer.analyze_customary_vs_treaty(document)
                    
                    # Save analysis to database
                    analysis_record = LegalAnalysis(
                        id=str(uuid.uuid4()),
                        document_id=doc_id,
                        analysis_type="customary_vs_treaty",
                        results=analysis,
                        confidence_score=analysis['confidence_score'],
                        methodology="Pattern-based legal analysis"
                    )
                    
                    cursor.execute("""
                        INSERT INTO legal_analyses 
                        (id, document_id, analysis_type, results, confidence_score, methodology)
                        VALUES (?, ?, ?, ?, ?, ?)
                    """, (
                        analysis_record.id, analysis_record.document_id,
                        analysis_record.analysis_type, json.dumps(analysis_record.results),
                        analysis_record.confidence_score, analysis_record.methodology
                    ))
                    
                    results.append({
                        "document_id": doc_id,
                        "analysis": analysis
                    })
            
            conn.commit()
        
        return APIResponse(
            success=True,
            message=f"Analyzed {len(results)} documents",
            data={"analyses": results}
        )
        
    except Exception as e:
        logger.error(f"Error in customary vs treaty analysis: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/analyze/jurisdictional-boundaries", response_model=APIResponse)
async def analyze_jurisdictional_boundaries(request: JurisdictionalAnalysisRequest):
    """Analyze jurisdictional boundaries"""
    try:
        with db_manager.get_connection() as conn:
            cursor = conn.cursor()
            
            # Get documents for the specified jurisdiction
            cursor.execute("""
                SELECT * FROM space_law_documents 
                WHERE jurisdiction = ? OR jurisdiction = 'international'
                ORDER BY date_collected DESC
            """, (request.jurisdiction,))
            
            rows = cursor.fetchall()
            documents = [dict(row) for row in rows]
            
            # Convert JSON fields
            for doc in documents:
                if doc.get('keywords'):
                    doc['keywords'] = json.loads(doc['keywords'])
                if doc.get('metadata'):
                    doc['metadata'] = json.loads(doc['metadata'])
            
            # Analyze boundaries
            boundaries = await analyzer.analyze_jurisdictional_boundaries(documents)
            
            # Save boundaries to database
            for boundary in boundaries:
                cursor.execute("""
                    INSERT INTO jurisdictional_boundaries 
                    (id, jurisdiction, boundary_type, description, legal_basis, 
                     conflicts, confidence_score, date_analyzed)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    boundary.id, boundary.jurisdiction.value, boundary.boundary_type,
                    boundary.description, json.dumps(boundary.legal_basis),
                    json.dumps(boundary.conflicts), boundary.confidence_score,
                    boundary.date_analyzed
                ))
            
            conn.commit()
        
        return APIResponse(
            success=True,
            message=f"Analyzed jurisdictional boundaries for {request.jurisdiction}",
            data={"boundaries": [boundary.dict() for boundary in boundaries]}
        )
        
    except Exception as e:
        logger.error(f"Error in jurisdictional analysis: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/generate/jus-cogens-recommendations", response_model=APIResponse)
async def generate_jus_cogens_recommendations(background_tasks: BackgroundTasks):
    """Generate jus cogens recommendations"""
    try:
        background_tasks.add_task(process_jus_cogens_recommendations)
        
        return APIResponse(
            success=True,
            message="Started generating jus cogens recommendations",
            data={"status": "processing"}
        )
        
    except Exception as e:
        logger.error(f"Error generating jus cogens recommendations: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/analyses", response_model=APIResponse)
async def get_analyses(
    analysis_type: Optional[str] = None,
    limit: int = 50,
    offset: int = 0
):
    """Get legal analyses"""
    try:
        with db_manager.get_connection() as conn:
            cursor = conn.cursor()
            
            query = "SELECT * FROM legal_analyses WHERE 1=1"
            params = []
            
            if analysis_type:
                query += " AND analysis_type = ?"
                params.append(analysis_type)
            
            query += " ORDER BY date_analyzed DESC LIMIT ? OFFSET ?"
            params.extend([limit, offset])
            
            cursor.execute(query, params)
            rows = cursor.fetchall()
            
            analyses = []
            for row in rows:
                analysis = dict(row)
                if analysis.get('results'):
                    analysis['results'] = json.loads(analysis['results'])
                analyses.append(analysis)
            
            return APIResponse(
                success=True,
                message=f"Retrieved {len(analyses)} analyses",
                data={"analyses": analyses}
            )
            
    except Exception as e:
        logger.error(f"Error retrieving analyses: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/boundaries", response_model=APIResponse)
async def get_jurisdictional_boundaries(limit: int = 50, offset: int = 0):
    """Get jurisdictional boundaries"""
    try:
        with db_manager.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM jurisdictional_boundaries 
                ORDER BY date_analyzed DESC LIMIT ? OFFSET ?
            """, (limit, offset))
            
            rows = cursor.fetchall()
            boundaries = []
            
            for row in rows:
                boundary = dict(row)
                if boundary.get('legal_basis'):
                    boundary['legal_basis'] = json.loads(boundary['legal_basis'])
                if boundary.get('conflicts'):
                    boundary['conflicts'] = json.loads(boundary['conflicts'])
                boundaries.append(boundary)
            
            return APIResponse(
                success=True,
                message=f"Retrieved {len(boundaries)} boundaries",
                data={"boundaries": boundaries}
            )
            
    except Exception as e:
        logger.error(f"Error retrieving boundaries: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/recommendations", response_model=APIResponse)
async def get_jus_cogens_recommendations(limit: int = 50, offset: int = 0):
    """Get jus cogens recommendations"""
    try:
        with db_manager.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM jus_cogens_recommendations 
                ORDER BY date_generated DESC LIMIT ? OFFSET ?
            """, (limit, offset))
            
            rows = cursor.fetchall()
            recommendations = []
            
            for row in rows:
                rec = dict(row)
                if rec.get('legal_basis'):
                    rec['legal_basis'] = json.loads(rec['legal_basis'])
                if rec.get('supporting_documents'):
                    rec['supporting_documents'] = json.loads(rec['supporting_documents'])
                if rec.get('opposition_arguments'):
                    rec['opposition_arguments'] = json.loads(rec['opposition_arguments'])
                recommendations.append(rec)
            
            return APIResponse(
                success=True,
                message=f"Retrieved {len(recommendations)} recommendations",
                data={"recommendations": recommendations}
            )
            
    except Exception as e:
        logger.error(f"Error retrieving recommendations: {e}")
        raise HTTPException(status_code=500, detail=str(e))


async def process_jus_cogens_recommendations():
    """Background task to generate jus cogens recommendations"""
    try:
        with db_manager.get_connection() as conn:
            cursor = conn.cursor()
            
            # Get all documents for analysis
            cursor.execute("SELECT * FROM space_law_documents WHERE status = 'completed'")
            rows = cursor.fetchall()
            documents = [dict(row) for row in rows]
            
            # Convert JSON fields
            for doc in documents:
                if doc.get('keywords'):
                    doc['keywords'] = json.loads(doc['keywords'])
                if doc.get('metadata'):
                    doc['metadata'] = json.loads(doc['metadata'])
            
            # Generate recommendations
            recommendations = await analyzer.generate_jus_cogens_recommendations(documents)
            
            # Save recommendations
            for rec in recommendations:
                cursor.execute("""
                    INSERT INTO jus_cogens_recommendations 
                    (id, principle, description, legal_basis, supporting_documents,
                     opposition_arguments, recommendation_strength, implementation_guidance, date_generated)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    rec.id, rec.principle, rec.description,
                    json.dumps(rec.legal_basis), json.dumps(rec.supporting_documents),
                    json.dumps(rec.opposition_arguments), rec.recommendation_strength,
                    rec.implementation_guidance, rec.date_generated
                ))
            
            conn.commit()
            logger.info(f"Generated {len(recommendations)} jus cogens recommendations")
            
    except Exception as e:
        logger.error(f"Error processing jus cogens recommendations: {e}")


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8002,
        reload=True,
        log_level="info"
    )
