# Google Analytics MCP Server Deployment Steps

## Prerequisites
- Google Cloud Project with billing enabled
- `gcloud` CLI installed and authenticated
- Docker installed and running
- OAuth credentials configured

## Step 1: Authentication Setup
```bash
# Set the correct account
gcloud config set account your-email@gmail.com

# Login and set up ADC
gcloud auth login
gcloud auth application-default login

# Verify project
gcloud config get-value project
```

## Step 2: Enable Required APIs
```bash
gcloud services enable \
  analyticsdata.googleapis.com \
  analyticsadmin.googleapis.com \
  run.googleapis.com \
  artifactregistry.googleapis.com \
  secretmanager.googleapis.com \
  webmasters.googleapis.com \
  content.googleapis.com
```

## Step 3: Store Credentials in Secret Manager
```bash
# Create secret if it doesn't exist
gcloud secrets create mcp_adc_credentials --replication-policy=automatic

# Add new version
gcloud secrets versions add mcp_adc_credentials \
  --data-file="$HOME/.config/gcloud/application_default_credentials.json"

# Grant access to App Engine default service account
PROJECT_ID=$(gcloud config get-value project)
gcloud secrets add-iam-policy-binding mcp_adc_credentials \
  --member="serviceAccount:${PROJECT_ID}@appspot.gserviceaccount.com" \
  --role="roles/secretmanager.secretAccessor"
```

## Step 4: Create Artifact Registry Repository
```bash
gcloud artifacts repositories create mcp-repo \
  --repository-format=docker --location=us-central1
```

## Step 5: Build and Push Docker Image
```bash
# Configure Docker authentication
gcloud auth configure-docker us-central1-docker.pkg.dev

# Build image with correct platform for Cloud Run
docker build --platform linux/amd64 -t us-central1-docker.pkg.dev/$(gcloud config get-value project)/mcp-repo/ga4-mcp:latest .

# Push to Artifact Registry
docker push us-central1-docker.pkg.dev/$(gcloud config get-value project)/mcp-repo/ga4-mcp:latest
```

## Step 6: Deploy to Cloud Run
```bash
PROJECT_ID=$(gcloud config get-value project)

gcloud run deploy ga4-mcp \
  --image=us-central1-docker.pkg.dev/${PROJECT_ID}/mcp-repo/ga4-mcp:latest \
  --region=us-central1 \
  --allow-unauthenticated \
  --memory=2Gi \
  --cpu=2 \
  --execution-environment=gen2 \
  --set-env-vars="GOOGLE_PROJECT_ID=${PROJECT_ID},GOOGLE_CLOUD_PROJECT=${PROJECT_ID}" \
  --update-secrets="/secrets/adc/credentials.json=mcp_adc_credentials:latest" \
  --service-account="${PROJECT_ID}@appspot.gserviceaccount.com"
```

## Step 7: Verify Deployment
```bash
# Get service URL
SERVICE_URL=$(gcloud run services describe ga4-mcp --region us-central1 --format='value(status.url)')

# Test health endpoint
curl "$SERVICE_URL/health"

# Expected response: {"status":"healthy","service":"Google Analytics MCP Server"}
```

## Troubleshooting

### Common Issues:

1. **Authentication Error**: Make sure you're using the correct Google account
2. **Permission Denied**: Ensure the account has proper IAM roles
3. **Architecture Error**: Always build with `--platform linux/amd64`
4. **Environment Variable Conflict**: Remove conflicting env vars before redeploying
5. **Secret Access**: Verify the service account has Secret Manager access

### Useful Commands:

```bash
# Check current authentication
gcloud auth list

# Check project
gcloud config get-value project

# Check service status
gcloud run services describe ga4-mcp --region us-central1

# View logs
gcloud run services logs read ga4-mcp --region us-central1

# Update service
gcloud run services update ga4-mcp --region us-central1 --memory=4Gi
```

## Claude Desktop Configuration

Add to `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "ga4-mcp": {
      "transport": {
        "type": "http",
        "url": "https://ga4-mcp-265267513550.us-central1.run.app/mcp"
      },
      "env": {
        "GOOGLE_PROJECT_ID": "continual-rhino-472501-i6"
      }
    }
  }
}
```

## Available Tools

### GA4 Tools (20 tools)
- `run_report` - Run custom GA4 reports
- `run_realtime_report` - Get real-time data
- `get_account_summaries` - List GA4 accounts
- `list_conversion_events` - List conversion events
- `list_data_streams` - List data streams
- `list_custom_dimensions` - List custom dimensions
- `list_custom_metrics` - List custom metrics
- And more...

### GSC Tools (3 tools)
- `gsc_sites_list` - List Search Console sites
- `gsc_sitemaps_list` - List sitemaps
- `gsc_search_analytics_query` - Query search performance

### GMC Tools (5 tools)
- `gmc_accounts_list` - List Merchant Center accounts
- `gmc_accounts_get` - Get account details
- `gmc_products_list` - List products
- `gmc_products_get` - Get product details
- `gmc_accounts_issues_list` - List account issues

## Notes
- Always use `--platform linux/amd64` for Docker builds
- The service uses Content API v2.1 for Merchant Center (not deprecated)
- OAuth scopes include GA4, GSC, and GMC read-only access
- Service runs on port 8080 internally
- Health check endpoint: `/health`
- MCP endpoint: `/mcp`
