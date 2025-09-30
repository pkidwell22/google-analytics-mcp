#!/bin/bash

# Google Analytics MCP Cloud Run Deployment Script
# This script deploys the GA4 MCP server to Google Cloud Run

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
PROJECT_ID=$(gcloud config get-value project)
REGION="us-central1"
SERVICE_NAME="ga4-mcp"
REPOSITORY_NAME="mcp-repo"
IMAGE_NAME="ga4-mcp"
SECRET_NAME="mcp_adc_credentials"

echo -e "${GREEN}🚀 Starting Google Analytics MCP Cloud Run Deployment${NC}"
echo -e "${YELLOW}Project ID: ${PROJECT_ID}${NC}"
echo -e "${YELLOW}Region: ${REGION}${NC}"
echo -e "${YELLOW}Service: ${SERVICE_NAME}${NC}"

# Check if gcloud is authenticated
if ! gcloud auth list --filter=status:ACTIVE --format="value(account)" | grep -q .; then
    echo -e "${RED}❌ No active gcloud authentication found. Please run 'gcloud auth login' first.${NC}"
    exit 1
fi

# Enable required APIs
echo -e "${YELLOW}📋 Enabling required APIs...${NC}"
gcloud services enable \
    analyticsdata.googleapis.com \
    analyticsadmin.googleapis.com \
    run.googleapis.com \
    artifactregistry.googleapis.com \
    secretmanager.googleapis.com \
    cloudbuild.googleapis.com

# Create Artifact Registry repository if it doesn't exist
echo -e "${YELLOW}📦 Creating Artifact Registry repository...${NC}"
if ! gcloud artifacts repositories describe ${REPOSITORY_NAME} --location=${REGION} >/dev/null 2>&1; then
    gcloud artifacts repositories create ${REPOSITORY_NAME} \
        --repository-format=docker \
        --location=${REGION}
    echo -e "${GREEN}✅ Created Artifact Registry repository${NC}"
else
    echo -e "${GREEN}✅ Artifact Registry repository already exists${NC}"
fi

# Store ADC credentials in Secret Manager if they exist
if [ -f "$HOME/.config/gcloud/application_default_credentials.json" ]; then
    echo -e "${YELLOW}🔐 Storing ADC credentials in Secret Manager...${NC}"
    
    # Create secret if it doesn't exist
    if ! gcloud secrets describe ${SECRET_NAME} >/dev/null 2>&1; then
        gcloud secrets create ${SECRET_NAME} --replication-policy=automatic
    fi
    
    # Add new version
    gcloud secrets versions add ${SECRET_NAME} \
        --data-file="$HOME/.config/gcloud/application_default_credentials.json"
    
    # Grant access to App Engine default service account
    gcloud secrets add-iam-policy-binding ${SECRET_NAME} \
        --member="serviceAccount:${PROJECT_ID}@appspot.gserviceaccount.com" \
        --role="roles/secretmanager.secretAccessor"
    
    echo -e "${GREEN}✅ ADC credentials stored in Secret Manager${NC}"
else
    echo -e "${RED}❌ ADC credentials not found at $HOME/.config/gcloud/application_default_credentials.json${NC}"
    echo -e "${YELLOW}Please run: gcloud auth application-default login${NC}"
    exit 1
fi

# Build and push Docker image
echo -e "${YELLOW}🐳 Building and pushing Docker image...${NC}"
IMAGE_URI="us-central1-docker.pkg.dev/${PROJECT_ID}/${REPOSITORY_NAME}/${IMAGE_NAME}:latest"

gcloud builds submit \
    --tag ${IMAGE_URI} \
    --region=${REGION}

echo -e "${GREEN}✅ Docker image built and pushed${NC}"

# Deploy to Cloud Run
echo -e "${YELLOW}🚀 Deploying to Cloud Run...${NC}"
gcloud run deploy ${SERVICE_NAME} \
    --image=${IMAGE_URI} \
    --region=${REGION} \
    --allow-unauthenticated \
    --memory=2Gi \
    --cpu=2 \
    --execution-environment=gen2 \
    --set-env-vars="GOOGLE_PROJECT_ID=${PROJECT_ID}" \
    --update-secrets="/secrets/adc/credentials.json=${SECRET_NAME}:latest"

# Get service URL
SERVICE_URL=$(gcloud run services describe ${SERVICE_NAME} --region ${REGION} --format='value(status.url)')

echo -e "${GREEN}🎉 Deployment completed successfully!${NC}"
echo -e "${GREEN}Service URL: ${SERVICE_URL}${NC}"

# Test the deployment
echo -e "${YELLOW}🧪 Testing deployment...${NC}"
if curl -s "${SERVICE_URL}/health" >/dev/null; then
    echo -e "${GREEN}✅ Health check passed${NC}"
else
    echo -e "${RED}❌ Health check failed${NC}"
fi

echo -e "${YELLOW}📋 Next steps:${NC}"
echo -e "1. Add this to your Claude Desktop config:"
echo -e "   ${GREEN}\"ga4-mcp\": {${NC}"
echo -e "   ${GREEN}  \"transport\": {${NC}"
echo -e "   ${GREEN}    \"type\": \"http\",${NC}"
echo -e "   ${GREEN}    \"url\": \"${SERVICE_URL}\"${NC}"
echo -e "   ${GREEN}  },${NC}"
echo -e "   ${GREEN}  \"env\": {${NC}"
echo -e "   ${GREEN}    \"GOOGLE_PROJECT_ID\": \"${PROJECT_ID}\"${NC}"
echo -e "   ${GREEN}  }${NC}"
echo -e "   ${GREEN}}{NC}"
echo -e "2. Restart Claude Desktop"
echo -e "3. Test with: 'Use the ga4-mcp server to list my GA4 accounts'"
