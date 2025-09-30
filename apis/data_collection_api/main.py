"""
Data Collection API for International Space Law AI Assistant
Web scrapes international space law statutes, treaties, and space events
"""
import asyncio
import logging
from datetime import datetime
from typing import List, Dict, Any, Optional
import uvicorn
from fastapi import FastAPI, HTTPException, BackgroundTasks, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import httpx
from bs4 import BeautifulSoup
import json
import uuid
import sys
import os

# Add parent directories to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from shared.models import SpaceLawDocument, SpaceEvent, APIResponse, LawType, Jurisdiction, DocumentStatus
from database.connection import db_manager

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Space Law Data Collection API",
    description="API for collecting international space law documents and events",
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


class ScrapingRequest(BaseModel):
    """Request model for scraping operations"""
    urls: List[str]
    categories: List[str] = ["treaties", "statutes", "events"]
    max_documents: int = 100
    jurisdiction_filter: Optional[str] = None


class DocumentResponse(BaseModel):
    """Response model for document operations"""
    document_id: str
    status: str
    message: str


# Space law sources configuration
SPACE_LAW_SOURCES = {
    "treaties": [
        "https://www.unoosa.org/oosa/en/ourwork/spacelaw/treaties.html",
        "https://www.state.gov/space-treaties-and-principles/",
        "https://www.esa.int/About_Us/Law_at_ESA/ESA_and_the_law/International_Space_Law"
    ],
    "statutes": [
        "https://www.faa.gov/space/regulations_policies/",
        "https://www.esa.int/About_Us/Law_at_ESA/ESA_and_the_law",
        "https://www.unoosa.org/oosa/en/ourwork/spacelaw/nationalspacelaw.html"
    ],
    "events": [
        "https://www.space.com/news",
        "https://spacenews.com/",
        "https://www.unoosa.org/oosa/en/informationfor/media/newscentre.html"
    ]
}


class SpaceLawScraper:
    """Space law document scraper"""
    
    def __init__(self):
        self.session = httpx.AsyncClient(timeout=30.0)
    
    async def scrape_document(self, url: str, category: str) -> Optional[SpaceLawDocument]:
        """Scrape a single document"""
        try:
            logger.info(f"Scraping document from: {url}")
            response = await self.session.get(url)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract title
            title = self._extract_title(soup, url)
            
            # Extract content
            content = self._extract_content(soup)
            
            # Determine law type and jurisdiction
            law_type, jurisdiction = self._classify_document(soup, url, category)
            
            # Extract keywords
            keywords = self._extract_keywords(content, title)
            
            # Generate summary
            summary = self._generate_summary(content)
            
            document = SpaceLawDocument(
                id=str(uuid.uuid4()),
                title=title,
                content=content,
                source_url=url,
                law_type=law_type,
                jurisdiction=jurisdiction,
                keywords=keywords,
                summary=summary,
                status=DocumentStatus.COMPLETED,
                metadata={
                    "category": category,
                    "scraped_at": datetime.utcnow().isoformat(),
                    "content_length": len(content)
                }
            )
            
            return document
            
        except Exception as e:
            logger.error(f"Error scraping {url}: {e}")
            return None
    
    def _extract_title(self, soup: BeautifulSoup, url: str) -> str:
        """Extract document title"""
        # Try various title selectors
        title_selectors = [
            'h1', 'title', '.document-title', '.page-title', 
            'h2', '.content-title', '.article-title'
        ]
        
        for selector in title_selectors:
            title_elem = soup.select_one(selector)
            if title_elem and title_elem.get_text(strip=True):
                return title_elem.get_text(strip=True)
        
        # Fallback to URL-based title
        return url.split('/')[-1].replace('-', ' ').replace('_', ' ').title()
    
    def _extract_content(self, soup: BeautifulSoup) -> str:
        """Extract main content from page"""
        # Remove script and style elements
        for script in soup(["script", "style", "nav", "footer", "header"]):
            script.decompose()
        
        # Try to find main content areas
        content_selectors = [
            '.content', '.main-content', '.article-content', 
            '.document-content', 'main', 'article', '.post-content'
        ]
        
        for selector in content_selectors:
            content_elem = soup.select_one(selector)
            if content_elem:
                return content_elem.get_text(strip=True)
        
        # Fallback to body text
        return soup.get_text(strip=True)
    
    def _classify_document(self, soup: BeautifulSoup, url: str, category: str) -> tuple:
        """Classify document type and jurisdiction"""
        text = soup.get_text().lower()
        
        # Determine law type
        if any(word in text for word in ['treaty', 'convention', 'agreement']):
            law_type = LawType.TREATY
        elif any(word in text for word in ['regulation', 'rule', 'policy']):
            law_type = LawType.REGULATORY
        elif any(word in text for word in ['court', 'judgment', 'case']):
            law_type = LawType.CASE_LAW
        else:
            law_type = LawType.DOMESTIC
        
        # Determine jurisdiction
        if 'un' in text or 'united nations' in text or 'unoosa' in text:
            jurisdiction = Jurisdiction.UN
        elif 'usa' in text or 'united states' in text or 'faa' in text:
            jurisdiction = Jurisdiction.US
        elif 'eu' in text or 'european union' in text or 'esa' in text:
            jurisdiction = Jurisdiction.EU
        elif 'russia' in text or 'russian' in text:
            jurisdiction = Jurisdiction.RUSSIA
        elif 'china' in text or 'chinese' in text:
            jurisdiction = Jurisdiction.CHINA
        elif 'international' in text:
            jurisdiction = Jurisdiction.INTERNATIONAL
        else:
            jurisdiction = Jurisdiction.OTHER
        
        return law_type, jurisdiction
    
    def _extract_keywords(self, content: str, title: str) -> List[str]:
        """Extract keywords from content"""
        # Simple keyword extraction (can be enhanced with NLP)
        space_law_keywords = [
            'outer space', 'space law', 'space treaty', 'space debris',
            'satellite', 'launch', 'spacecraft', 'astronaut', 'cosmonaut',
            'space station', 'moon treaty', 'liability convention',
            'registration convention', 'rescue agreement', 'space exploration',
            'space mining', 'space tourism', 'orbital debris', 'space traffic'
        ]
        
        text = (content + ' ' + title).lower()
        found_keywords = [kw for kw in space_law_keywords if kw in text]
        
        return found_keywords[:10]  # Limit to 10 keywords
    
    def _generate_summary(self, content: str) -> str:
        """Generate a simple summary of the content"""
        # Simple extractive summarization (first few sentences)
        sentences = content.split('. ')
        summary_sentences = sentences[:3]  # First 3 sentences
        return '. '.join(summary_sentences) + '.'
    
    async def scrape_space_events(self, urls: List[str]) -> List[SpaceEvent]:
        """Scrape space events from news sources"""
        events = []
        
        for url in urls:
            try:
                response = await self.session.get(url)
                response.raise_for_status()
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Extract event information (implementation depends on source)
                # This is a simplified version
                articles = soup.find_all(['article', '.article', '.news-item'])
                
                for article in articles[:5]:  # Limit to 5 events per source
                    title_elem = article.find(['h1', 'h2', 'h3', '.title', '.headline'])
                    if title_elem:
                        title = title_elem.get_text(strip=True)
                        content = article.get_text(strip=True)
                        
                        event = SpaceEvent(
                            id=str(uuid.uuid4()),
                            title=title,
                            description=content[:500],  # First 500 chars
                            event_type="space_news",
                            date_occurred=datetime.utcnow(),
                            metadata={"source_url": url}
                        )
                        events.append(event)
                        
            except Exception as e:
                logger.error(f"Error scraping events from {url}: {e}")
        
        return events
    
    async def close(self):
        """Close the HTTP session"""
        await self.session.aclose()


# Global scraper instance
scraper = SpaceLawScraper()


@app.on_event("startup")
async def startup_event():
    """Initialize database on startup"""
    try:
        db_manager.initialize_database()
        logger.info("Data Collection API started successfully")
    except Exception as e:
        logger.error(f"Startup error: {e}")


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    await scraper.close()


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "timestamp": datetime.utcnow()}


@app.post("/scrape/documents", response_model=APIResponse)
async def scrape_documents(request: ScrapingRequest, background_tasks: BackgroundTasks):
    """Scrape space law documents from specified URLs"""
    try:
        # Start scraping in background
        background_tasks.add_task(process_documents, request.urls, request.categories)
        
        return APIResponse(
            success=True,
            message=f"Started scraping {len(request.urls)} URLs",
            data={"requested_urls": len(request.urls)}
        )
        
    except Exception as e:
        logger.error(f"Error starting scraping: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/scrape/events", response_model=APIResponse)
async def scrape_events(urls: List[str], background_tasks: BackgroundTasks):
    """Scrape space events from news sources"""
    try:
        background_tasks.add_task(process_events, urls)
        
        return APIResponse(
            success=True,
            message=f"Started scraping events from {len(urls)} sources",
            data={"requested_sources": len(urls)}
        )
        
    except Exception as e:
        logger.error(f"Error starting event scraping: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/documents", response_model=APIResponse)
async def get_documents(
    limit: int = 50,
    offset: int = 0,
    law_type: Optional[str] = None,
    jurisdiction: Optional[str] = None
):
    """Get collected documents with optional filters"""
    try:
        with db_manager.get_connection() as conn:
            cursor = conn.cursor()
            
            query = "SELECT * FROM space_law_documents WHERE 1=1"
            params = []
            
            if law_type:
                query += " AND law_type = ?"
                params.append(law_type)
            
            if jurisdiction:
                query += " AND jurisdiction = ?"
                params.append(jurisdiction)
            
            query += " ORDER BY date_collected DESC LIMIT ? OFFSET ?"
            params.extend([limit, offset])
            
            cursor.execute(query, params)
            rows = cursor.fetchall()
            
            documents = []
            for row in rows:
                doc = dict(row)
                # Convert JSON fields back to Python objects
                if doc.get('keywords'):
                    doc['keywords'] = json.loads(doc['keywords'])
                if doc.get('metadata'):
                    doc['metadata'] = json.loads(doc['metadata'])
                documents.append(doc)
            
            return APIResponse(
                success=True,
                message=f"Retrieved {len(documents)} documents",
                data={"documents": documents, "total": len(documents)}
            )
            
    except Exception as e:
        logger.error(f"Error retrieving documents: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/events", response_model=APIResponse)
async def get_events(limit: int = 50, offset: int = 0):
    """Get collected space events"""
    try:
        with db_manager.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM space_events ORDER BY date_occurred DESC LIMIT ? OFFSET ?",
                (limit, offset)
            )
            rows = cursor.fetchall()
            
            events = []
            for row in rows:
                event = dict(row)
                if event.get('participants'):
                    event['participants'] = json.loads(event['participants'])
                if event.get('metadata'):
                    event['metadata'] = json.loads(event['metadata'])
                events.append(event)
            
            return APIResponse(
                success=True,
                message=f"Retrieved {len(events)} events",
                data={"events": events, "total": len(events)}
            )
            
    except Exception as e:
        logger.error(f"Error retrieving events: {e}")
        raise HTTPException(status_code=500, detail=str(e))


async def process_documents(urls: List[str], categories: List[str]):
    """Background task to process document scraping"""
    for url in urls:
        try:
            document = await scraper.scrape_document(url, categories[0] if categories else "general")
            if document:
                # Save to database
                with db_manager.get_connection() as conn:
                    cursor = conn.cursor()
                    cursor.execute("""
                        INSERT INTO space_law_documents 
                        (id, title, content, source_url, law_type, jurisdiction, 
                         date_collected, keywords, summary, status, metadata)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        document.id, document.title, document.content, document.source_url,
                        document.law_type.value, document.jurisdiction.value,
                        document.date_collected, json.dumps(document.keywords),
                        document.summary, document.status.value, json.dumps(document.metadata)
                    ))
                    conn.commit()
                    logger.info(f"Saved document: {document.title}")
        except Exception as e:
            logger.error(f"Error processing document from {url}: {e}")


async def process_events(urls: List[str]):
    """Background task to process event scraping"""
    events = await scraper.scrape_space_events(urls)
    
    for event in events:
        try:
            with db_manager.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO space_events 
                    (id, title, description, event_type, date_occurred, date_collected, 
                     participants, metadata)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    event.id, event.title, event.description, event.event_type,
                    event.date_occurred, event.date_collected,
                    json.dumps(event.participants), json.dumps(event.metadata)
                ))
                conn.commit()
                logger.info(f"Saved event: {event.title}")
        except Exception as e:
            logger.error(f"Error saving event {event.title}: {e}")


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8001,
        reload=True,
        log_level="info"
    )
