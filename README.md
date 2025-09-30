# International Space Law AI Assistant

A comprehensive system for analyzing international space law through cloud-hosted APIs that collect, process, and analyze space law documents to support strategic legal recommendations and jus cogens establishment.

## System Architecture

The system consists of:

1. **Data Collection API** - Web scrapes international space law statutes, treaties, and space events
2. **Legal Analysis API** - Processes classified data to distinguish customary from treaty law and identify jurisdictional boundaries
3. **Centralized Database** - Stores collected documents, analyses, and recommendations
4. **Local Windows AI Assistant** - Rust executable that communicates with cloud APIs (to be implemented)

## Project Structure

```
International-Space-Law-AI-Assistant/
├── apis/
│   ├── data_collection_api/     # Data collection service
│   └── legal_analysis_api/      # Legal analysis service
├── shared/                      # Shared models and utilities
├── database/                    # Database schema and connection
├── docker-compose.yml          # Container orchestration
└── config.env.example          # Environment configuration
```

## APIs Overview

### Data Collection API (Port 8001)

**Purpose**: Web scrapes international space law statutes, treaties, and space events, categorizing and organizing information in a centralized database.

**Key Features**:
- Web scraping from multiple space law sources
- Document classification (treaty, customary, domestic, regulatory, case law)
- Jurisdiction identification (UN, US, EU, Russia, China, International, Other)
- Automatic keyword extraction and summarization
- Space event monitoring

**Endpoints**:
- `POST /scrape/documents` - Start document scraping
- `POST /scrape/events` - Start event scraping
- `GET /documents` - Retrieve collected documents
- `GET /events` - Retrieve space events
- `GET /health` - Health check

### Legal Analysis API (Port 8002)

**Purpose**: Processes classified data to distinguish customary from treaty law and identify jurisdictional boundaries of international space law.

**Key Features**:
- Customary vs Treaty Law Analysis
- Jurisdictional Boundary Analysis
- Jus Cogens Recommendation Generation
- Legal Pattern Recognition
- Confidence Scoring

**Endpoints**:
- `POST /analyze/customary-vs-treaty` - Analyze legal classification
- `POST /analyze/jurisdictional-boundaries` - Analyze jurisdictional boundaries
- `POST /generate/jus-cogens-recommendations` - Generate jus cogens recommendations
- `GET /analyses` - Retrieve legal analyses
- `GET /boundaries` - Retrieve jurisdictional boundaries
- `GET /recommendations` - Retrieve jus cogens recommendations
- `GET /health` - Health check

## Database Schema

The system uses a centralized database with the following main tables:

- `space_law_documents` - Collected legal documents
- `space_events` - Space-related events and news
- `legal_analyses` - Analysis results
- `jurisdictional_boundaries` - Jurisdictional analysis
- `jus_cogens_recommendations` - Jus cogens recommendations
- `api_logs` - API monitoring and logging

## Deployment Options

### Cloud Platform Agnostic Design

The APIs are designed to be deployed on any major cloud platform:

#### AWS Deployment
```bash
# Using AWS ECS/Fargate
aws ecs create-service --cluster space-law-cluster --service-name data-collection-api

# Using AWS Lambda (serverless)
serverless deploy --stage prod
```

#### Azure Deployment
```bash
# Using Azure Container Instances
az container create --resource-group space-law-rg --name data-collection-api

# Using Azure App Service
az webapp up --name space-law-data-collection --resource-group space-law-rg
```

#### Google Cloud Deployment
```bash
# Using Google Cloud Run
gcloud run deploy data-collection-api --source .

# Using Google Kubernetes Engine
gcloud container clusters create space-law-cluster
```

#### Kubernetes Deployment
```bash
# Deploy with Helm
helm install space-law-ai ./helm-chart

# Direct kubectl deployment
kubectl apply -f k8s/
```

### Local Development

1. **Clone and Setup**:
```bash
git clone <repository-url>
cd International-Space-Law-AI-Assistant
cp config.env.example .env
```

2. **Install Dependencies**:
```bash
# Data Collection API
cd apis/data_collection_api
pip install -r requirements.txt

# Legal Analysis API
cd ../legal_analysis_api
pip install -r requirements.txt
```

3. **Setup Database**:
```bash
# PostgreSQL (recommended)
createdb space_law_db
psql space_law_db < database/schema.sql

# Or use SQLite for development
python -c "from database.connection import db_manager; db_manager.initialize_database()"
```

4. **Run APIs**:
```bash
# Terminal 1 - Data Collection API
cd apis/data_collection_api
python main.py

# Terminal 2 - Legal Analysis API
cd apis/legal_analysis_api
python main.py
```

### Docker Deployment

```bash
# Build and run with Docker Compose
docker-compose up --build

# Individual API containers
docker build -t data-collection-api ./apis/data_collection_api/
docker build -t legal-analysis-api ./apis/legal_analysis_api/
```

## Environment Configuration

Copy `config.env.example` to `.env` and configure:

```env
# Database
DB_TYPE=postgresql  # or mysql, sqlite
DB_HOST=localhost
DB_PORT=5432
DB_NAME=space_law_db
DB_USER=space_law_user
DB_PASSWORD=your_password

# APIs
DATA_COLLECTION_API_PORT=8001
LEGAL_ANALYSIS_API_PORT=8002
```

## API Usage Examples

### Collect Space Law Documents
```bash
curl -X POST "http://localhost:8001/scrape/documents" \
  -H "Content-Type: application/json" \
  -d '{
    "urls": ["https://www.unoosa.org/oosa/en/ourwork/spacelaw/treaties.html"],
    "categories": ["treaties"],
    "max_documents": 50
  }'
```

### Analyze Legal Classification
```bash
curl -X POST "http://localhost:8002/analyze/customary-vs-treaty" \
  -H "Content-Type: application/json" \
  -d '{
    "document_ids": ["doc-uuid-1", "doc-uuid-2"],
    "analysis_types": ["customary_vs_treaty"]
  }'
```

### Generate Jus Cogens Recommendations
```bash
curl -X POST "http://localhost:8002/generate/jus-cogens-recommendations"
```

## Integration with Rust AI Assistant

The APIs are designed to be consumed by a local Windows Rust executable that will:

1. Query the Data Collection API for new documents
2. Request legal analysis from the Legal Analysis API
3. Generate strategic legal recommendations
4. Support establishment and maintenance of jus cogens

## Monitoring and Logging

- API endpoints include health checks
- Database logging for all operations
- Structured logging with timestamps
- Performance metrics collection

## Security Considerations

- CORS enabled for cross-origin requests
- Input validation with Pydantic models
- SQL injection prevention with parameterized queries
- Environment-based configuration management
- Non-root container execution

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For questions or issues, please create an issue in the repository or contact the development team.