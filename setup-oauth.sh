#!/bin/bash

# OAuth setup script for Google Analytics MCP
# This script helps set up Application Default Credentials

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}Google Analytics MCP OAuth Setup${NC}"

# Check if gcloud is installed
if ! command -v gcloud &> /dev/null; then
    echo -e "${RED}ERROR: gcloud CLI not found. Please install it first:${NC}"
    echo -e "${YELLOW}https://cloud.google.com/sdk/docs/install${NC}"
    exit 1
fi

# Check if user is authenticated
if ! gcloud auth list --filter=status:ACTIVE --format="value(account)" | grep -q .; then
    echo -e "${YELLOW}Please authenticate with gcloud first:${NC}"
    gcloud auth login
fi

# Check if project is set
PROJECT_ID=$(gcloud config get-value project)
if [ -z "$PROJECT_ID" ]; then
    echo -e "${YELLOW}Please set your default project:${NC}"
    gcloud config set project YOUR_PROJECT_ID
    echo -e "${YELLOW}Replace YOUR_PROJECT_ID with your actual project ID${NC}"
    exit 1
fi

echo -e "${GREEN}Using project: ${PROJECT_ID}${NC}"

# Check if OAuth client file exists
if [ -f "client_secret_*.json" ]; then
    CLIENT_FILE=$(ls client_secret_*.json | head -n1)
    echo -e "${GREEN}Found OAuth client file: ${CLIENT_FILE}${NC}"
else
    echo -e "${YELLOW}WARNING: No OAuth client file found.${NC}"
    echo -e "${YELLOW}Please download your OAuth 2.0 client credentials from:${NC}"
    echo -e "${YELLOW}https://console.cloud.google.com/apis/credentials${NC}"
    echo -e "${YELLOW}And place the JSON file in this directory as 'client_secret_*.json'${NC}"
    exit 1
fi

# Set up Application Default Credentials
echo -e "${YELLOW}Setting up Application Default Credentials...${NC}"
gcloud auth application-default login \
  --client-id-file="${CLIENT_FILE}" \
  --scopes="https://www.googleapis.com/auth/analytics.readonly,https://www.googleapis.com/auth/cloud-platform"

echo -e "${GREEN}OAuth setup completed!${NC}"
echo -e "${YELLOW}Next steps:${NC}"
echo -e "1. Run './test-local.sh' to test locally"
echo -e "2. Run './deploy.sh' to deploy to Cloud Run"
echo -e "3. Add the Cloud Run URL to your Claude Desktop config"
