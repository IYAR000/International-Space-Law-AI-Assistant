-- International Space Law AI Assistant Database Schema
-- Compatible with PostgreSQL, MySQL, and SQLite

-- Documents table for storing space law documents
CREATE TABLE IF NOT EXISTS space_law_documents (
    id VARCHAR(255) PRIMARY KEY,
    title TEXT NOT NULL,
    content TEXT NOT NULL,
    source_url TEXT NOT NULL,
    law_type VARCHAR(50) NOT NULL,
    jurisdiction VARCHAR(50) NOT NULL,
    date_published TIMESTAMP,
    date_collected TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    keywords JSON,
    summary TEXT,
    status VARCHAR(50) DEFAULT 'pending',
    metadata JSON,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- Space events table
CREATE TABLE IF NOT EXISTS space_events (
    id VARCHAR(255) PRIMARY KEY,
    title TEXT NOT NULL,
    description TEXT NOT NULL,
    event_type VARCHAR(100) NOT NULL,
    date_occurred TIMESTAMP NOT NULL,
    date_collected TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    participants JSON,
    location VARCHAR(255),
    legal_implications TEXT,
    metadata JSON,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- Legal analysis results table
CREATE TABLE IF NOT EXISTS legal_analyses (
    id VARCHAR(255) PRIMARY KEY,
    document_id VARCHAR(255) NOT NULL,
    analysis_type VARCHAR(100) NOT NULL,
    results JSON NOT NULL,
    confidence_score DECIMAL(3,2) CHECK (confidence_score >= 0 AND confidence_score <= 1),
    date_analyzed TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    methodology TEXT,
    analyst_notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (document_id) REFERENCES space_law_documents(id) ON DELETE CASCADE
);

-- Jurisdictional boundaries table
CREATE TABLE IF NOT EXISTS jurisdictional_boundaries (
    id VARCHAR(255) PRIMARY KEY,
    jurisdiction VARCHAR(50) NOT NULL,
    boundary_type VARCHAR(100) NOT NULL,
    description TEXT NOT NULL,
    legal_basis JSON,
    conflicts JSON,
    confidence_score DECIMAL(3,2) CHECK (confidence_score >= 0 AND confidence_score <= 1),
    date_analyzed TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Jus cogens recommendations table
CREATE TABLE IF NOT EXISTS jus_cogens_recommendations (
    id VARCHAR(255) PRIMARY KEY,
    principle TEXT NOT NULL,
    description TEXT NOT NULL,
    legal_basis JSON,
    supporting_documents JSON,
    opposition_arguments JSON,
    recommendation_strength DECIMAL(3,2) CHECK (recommendation_strength >= 0 AND recommendation_strength <= 1),
    implementation_guidance TEXT,
    date_generated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- API logs table for monitoring
CREATE TABLE IF NOT EXISTS api_logs (
    id VARCHAR(255) PRIMARY KEY,
    api_name VARCHAR(100) NOT NULL,
    endpoint VARCHAR(255) NOT NULL,
    method VARCHAR(10) NOT NULL,
    request_data JSON,
    response_data JSON,
    status_code INTEGER,
    processing_time_ms INTEGER,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    error_message TEXT
);

-- Indexes for better performance
CREATE INDEX IF NOT EXISTS idx_documents_law_type ON space_law_documents(law_type);
CREATE INDEX IF NOT EXISTS idx_documents_jurisdiction ON space_law_documents(jurisdiction);
CREATE INDEX IF NOT EXISTS idx_documents_status ON space_law_documents(status);
CREATE INDEX IF NOT EXISTS idx_documents_date_collected ON space_law_documents(date_collected);

CREATE INDEX IF NOT EXISTS idx_events_type ON space_events(event_type);
CREATE INDEX IF NOT EXISTS idx_events_date_occurred ON space_events(date_occurred);

CREATE INDEX IF NOT EXISTS idx_analyses_document_id ON legal_analyses(document_id);
CREATE INDEX IF NOT EXISTS idx_analyses_type ON legal_analyses(analysis_type);

CREATE INDEX IF NOT EXISTS idx_boundaries_jurisdiction ON jurisdictional_boundaries(jurisdiction);
CREATE INDEX IF NOT EXISTS idx_logs_timestamp ON api_logs(timestamp);


