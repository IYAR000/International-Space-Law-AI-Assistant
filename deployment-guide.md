# Deployment Guide - International Space Law AI Assistant APIs

This guide provides detailed instructions for deploying the International Space Law AI Assistant APIs to various cloud platforms.

## Prerequisites

- Docker installed
- Cloud platform account (AWS, Azure, GCP, or Kubernetes cluster)
- Basic knowledge of containerization and cloud services

## Cloud Platform Selection Guide

### AWS (Amazon Web Services)
**Best for**: Enterprise applications, high availability, extensive service integration
- **Services**: ECS, Fargate, Lambda, RDS, ElastiCache
- **Pros**: Mature ecosystem, extensive documentation, auto-scaling
- **Cons**: Can be complex, potentially expensive

### Azure (Microsoft Azure)
**Best for**: Microsoft ecosystem integration, hybrid cloud scenarios
- **Services**: Container Instances, App Service, Azure Database, Redis Cache
- **Pros**: Good integration with Microsoft tools, hybrid cloud support
- **Cons**: Smaller third-party ecosystem compared to AWS

### Google Cloud Platform (GCP)
**Best for**: AI/ML workloads, container-native applications
- **Services**: Cloud Run, GKE, Cloud SQL, Memorystore
- **Pros**: Excellent for containers, competitive pricing, good AI services
- **Cons**: Smaller enterprise adoption, less third-party integrations

### Kubernetes (Any Cloud)
**Best for**: Multi-cloud deployments, maximum flexibility
- **Services**: Any Kubernetes cluster (EKS, AKS, GKE, on-premises)
- **Pros**: Cloud-agnostic, maximum control, standard deployment
- **Cons**: Higher complexity, requires Kubernetes expertise

## Quick Start - Local Development

```bash
# 1. Clone and setup
git clone <your-repo>
cd International-Space-Law-AI-Assistant

# 2. Configure environment
cp config.env.example .env
# Edit .env with your database settings

# 3. Start with Docker Compose
docker-compose up --build

# 4. Test APIs
curl http://localhost:8001/health
curl http://localhost:8002/health
```

## AWS Deployment

### Option 1: AWS ECS with Fargate

```bash
# 1. Create ECS cluster
aws ecs create-cluster --cluster-name space-law-ai

# 2. Build and push Docker images to ECR
aws ecr create-repository --repository-name space-law-data-collection
aws ecr create-repository --repository-name space-law-legal-analysis

# Build and tag images
docker build -t data-collection-api ./apis/data_collection_api/
docker tag data-collection-api:latest <account>.dkr.ecr.<region>.amazonaws.com/space-law-data-collection:latest

# Push to ECR
aws ecr get-login-password --region <region> | docker login --username AWS --password-stdin <account>.dkr.ecr.<region>.amazonaws.com
docker push <account>.dkr.ecr.<region>.amazonaws.com/space-law-data-collection:latest

# 3. Create task definitions (see aws/task-definitions/)
# 4. Create services
aws ecs create-service --cluster space-law-ai --service-name data-collection-api --task-definition space-law-data-collection
```

### Option 2: AWS Lambda (Serverless)

```bash
# Install serverless framework
npm install -g serverless

# Deploy data collection API
cd apis/data_collection_api
serverless deploy --stage prod

# Deploy legal analysis API
cd ../legal_analysis_api
serverless deploy --stage prod
```

### AWS Infrastructure (Terraform)

```hcl
# main.tf
provider "aws" {
  region = var.aws_region
}

# ECS Cluster
resource "aws_ecs_cluster" "space_law_ai" {
  name = "space-law-ai"
}

# RDS Database
resource "aws_db_instance" "postgres" {
  identifier     = "space-law-db"
  engine         = "postgres"
  engine_version = "15.4"
  instance_class = "db.t3.micro"
  allocated_storage = 20
  
  db_name  = "space_law_db"
  username = "space_law_user"
  password = var.db_password
  
  vpc_security_group_ids = [aws_security_group.rds.id]
  db_subnet_group_name   = aws_db_subnet_group.main.name
  
  skip_final_snapshot = true
}

# ECS Service for Data Collection API
resource "aws_ecs_service" "data_collection_api" {
  name            = "data-collection-api"
  cluster         = aws_ecs_cluster.space_law_ai.id
  task_definition = aws_ecs_task_definition.data_collection_api.arn
  desired_count   = 2
  
  load_balancer {
    target_group_arn = aws_lb_target_group.data_collection_api.arn
    container_name   = "data-collection-api"
    container_port   = 8001
  }
}
```

## Azure Deployment

### Option 1: Azure Container Instances

```bash
# 1. Create resource group
az group create --name space-law-ai-rg --location eastus

# 2. Create Azure Database for PostgreSQL
az postgres flexible-server create \
  --resource-group space-law-ai-rg \
  --name space-law-db \
  --admin-user space_law_user \
  --admin-password <password> \
  --sku-name Standard_B1ms

# 3. Deploy container instances
az container create \
  --resource-group space-law-ai-rg \
  --name data-collection-api \
  --image <your-registry>/data-collection-api:latest \
  --ports 8001 \
  --environment-variables \
    DB_TYPE=postgresql \
    DB_HOST=space-law-db.postgres.database.azure.com \
    DB_NAME=space_law_db \
    DB_USER=space_law_user \
    DB_PASSWORD=<password>
```

### Option 2: Azure App Service

```bash
# Create App Service plan
az appservice plan create \
  --name space-law-ai-plan \
  --resource-group space-law-ai-rg \
  --sku B1 \
  --is-linux

# Deploy data collection API
az webapp create \
  --resource-group space-law-ai-rg \
  --plan space-law-ai-plan \
  --name space-law-data-collection \
  --deployment-container-image-name <your-registry>/data-collection-api:latest

# Configure app settings
az webapp config appsettings set \
  --resource-group space-law-ai-rg \
  --name space-law-data-collection \
  --settings \
    DB_TYPE=postgresql \
    DB_HOST=space-law-db.postgres.database.azure.com \
    DB_NAME=space_law_db \
    DB_USER=space_law_user \
    DB_PASSWORD=<password>
```

## Google Cloud Deployment

### Option 1: Cloud Run (Serverless Containers)

```bash
# 1. Set project
gcloud config set project <your-project-id>

# 2. Enable APIs
gcloud services enable run.googleapis.com
gcloud services enable sqladmin.googleapis.com

# 3. Create Cloud SQL instance
gcloud sql instances create space-law-db \
  --database-version=POSTGRES_15 \
  --tier=db-f1-micro \
  --region=us-central1

# 4. Create database
gcloud sql databases create space_law_db --instance=space-law-db

# 5. Deploy to Cloud Run
cd apis/data_collection_api
gcloud run deploy data-collection-api \
  --source . \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars DB_TYPE=postgresql,DB_HOST=/cloudsql/<project>:<region>:space-law-db
```

### Option 2: Google Kubernetes Engine (GKE)

```bash
# 1. Create GKE cluster
gcloud container clusters create space-law-cluster \
  --num-nodes 3 \
  --zone us-central1-a \
  --machine-type e2-medium

# 2. Get cluster credentials
gcloud container clusters get-credentials space-law-cluster --zone us-central1-a

# 3. Deploy with kubectl
kubectl apply -f k8s/
```

## Kubernetes Deployment

### Create Kubernetes Manifests

```yaml
# k8s/namespace.yaml
apiVersion: v1
kind: Namespace
metadata:
  name: space-law-ai

---
# k8s/configmap.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: space-law-config
  namespace: space-law-ai
data:
  DB_TYPE: "postgresql"
  DB_NAME: "space_law_db"
  DB_USER: "space_law_user"

---
# k8s/deployment-data-collection.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: data-collection-api
  namespace: space-law-ai
spec:
  replicas: 2
  selector:
    matchLabels:
      app: data-collection-api
  template:
    metadata:
      labels:
        app: data-collection-api
    spec:
      containers:
      - name: data-collection-api
        image: <your-registry>/data-collection-api:latest
        ports:
        - containerPort: 8001
        env:
        - name: DB_HOST
          value: "postgres-service"
        envFrom:
        - configMapRef:
            name: space-law-config
        - secretRef:
            name: space-law-secrets

---
# k8s/service-data-collection.yaml
apiVersion: v1
kind: Service
metadata:
  name: data-collection-service
  namespace: space-law-ai
spec:
  selector:
    app: data-collection-api
  ports:
  - port: 8001
    targetPort: 8001
  type: LoadBalancer
```

### Deploy to Kubernetes

```bash
# Apply all manifests
kubectl apply -f k8s/

# Check deployment status
kubectl get pods -n space-law-ai
kubectl get services -n space-law-ai

# Access services
kubectl port-forward service/data-collection-service 8001:8001 -n space-law-ai
```

## Environment-Specific Configuration

### Production Environment Variables

```bash
# Production .env
DB_TYPE=postgresql
DB_HOST=your-production-db-host
DB_PORT=5432
DB_NAME=space_law_db
DB_USER=space_law_user
DB_PASSWORD=secure_production_password

# Security
API_SECRET_KEY=your_secure_api_key
JWT_SECRET=your_jwt_secret

# Monitoring
LOG_LEVEL=INFO
ENABLE_METRICS=true

# Cloud-specific
AWS_REGION=us-east-1
AZURE_STORAGE_ACCOUNT=your_storage_account
GOOGLE_CLOUD_PROJECT=your_project_id
```

### Staging Environment

```bash
# Staging .env
DB_TYPE=postgresql
DB_HOST=staging-db-host
DB_NAME=space_law_db_staging
LOG_LEVEL=DEBUG
ENABLE_METRICS=true
```

## Monitoring and Observability

### Health Checks

Both APIs include health check endpoints:
- Data Collection API: `GET /health`
- Legal Analysis API: `GET /health`

### Logging

```bash
# View logs in production
docker-compose logs -f data-collection-api
docker-compose logs -f legal-analysis-api

# Kubernetes logs
kubectl logs -f deployment/data-collection-api -n space-law-ai
```

### Metrics Collection

The APIs log performance metrics to the `api_logs` table:
- Request/response times
- Status codes
- Error messages
- Processing times

## Security Best Practices

1. **Environment Variables**: Never commit secrets to version control
2. **Database Security**: Use strong passwords, enable SSL connections
3. **Network Security**: Configure proper firewall rules and VPC settings
4. **Container Security**: Use non-root users, keep images updated
5. **API Security**: Implement rate limiting, input validation, and authentication

## Scaling Considerations

### Horizontal Scaling

```yaml
# Kubernetes HPA
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: data-collection-hpa
  namespace: space-law-ai
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: data-collection-api
  minReplicas: 2
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
```

### Database Scaling

- Use read replicas for read-heavy workloads
- Implement connection pooling
- Consider database sharding for large datasets

## Troubleshooting

### Common Issues

1. **Database Connection Errors**
   ```bash
   # Check database connectivity
   docker-compose exec postgres psql -U space_law_user -d space_law_db -c "SELECT 1;"
   ```

2. **API Not Responding**
   ```bash
   # Check container status
   docker-compose ps
   docker-compose logs api-name
   ```

3. **Memory Issues**
   ```bash
   # Monitor resource usage
   docker stats
   kubectl top pods -n space-law-ai
   ```

### Performance Optimization

1. **Database Indexing**: Ensure proper indexes are created
2. **Caching**: Implement Redis caching for frequent queries
3. **Connection Pooling**: Use connection pooling for database connections
4. **Async Processing**: Use background tasks for heavy operations

## Cost Optimization

### Cloud Platform Cost Comparison

| Platform | Service | Estimated Monthly Cost (Small Scale) |
|----------|---------|-------------------------------------|
| AWS | ECS + RDS | $50-100 |
| Azure | Container Instances + Database | $40-80 |
| GCP | Cloud Run + Cloud SQL | $30-60 |
| Kubernetes | Any cluster + database | $20-50 |

### Cost Optimization Tips

1. Use appropriate instance sizes
2. Implement auto-scaling
3. Use spot instances where possible
4. Monitor and optimize database queries
5. Implement caching to reduce database load

## Support and Maintenance

### Regular Maintenance Tasks

1. **Database Maintenance**
   - Regular backups
   - Index optimization
   - Query performance monitoring

2. **Application Updates**
   - Security patches
   - Feature updates
   - Dependency updates

3. **Monitoring**
   - Health check monitoring
   - Performance metrics
   - Error rate monitoring

For additional support, please refer to the main README.md or create an issue in the repository.


