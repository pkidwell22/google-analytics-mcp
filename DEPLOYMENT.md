# Google Analytics MCP Cloud Run Deployment

This guide will help you deploy the Google Analytics MCP server to Google Cloud Run and connect it to Claude Desktop.

## Prerequisites

1. **Google Cloud Project**: You need a GCP project with billing enabled
2. **gcloud CLI**: Install and authenticate with `gcloud auth login`
3. **Docker**: For local testing (optional)
4. **Claude Desktop**: For connecting the MCP server

## Phase 1: User OAuth Setup (One-time)

Set up Application Default Credentials (ADC) for your Gmail account:

```bash
gcloud auth application-default login \
  --client-id-file=/path/to/your_oauth_web_client.json \
  --scopes="https://www.googleapis.com/auth/analytics.readonly,https://www.googleapis.com/auth/cloud-platform"
```

This creates `~/.config/gcloud/application_default_credentials.json` which will be used by the server.

## Phase 2: Local Testing (Optional)

Test the server locally with Docker:

```bash
# Build and run locally
./test-local.sh

# Or manually:
docker build -t ga4-mcp:local .
docker run --rm -p 8080:8080 \
  -e GOOGLE_PROJECT_ID="$(gcloud config get-value project)" \
  -v $HOME/.config/gcloud/application_default_credentials.json:/secrets/adc/credentials.json:ro \
  -e GOOGLE_APPLICATION_CREDENTIALS=/secrets/adc/credentials.json \
  ga4-mcp:local
```

Test endpoints:
```bash
curl http://localhost:8080/health
curl -X POST http://localhost:8080/tools/list
```

## Phase 3: Cloud Run Deployment

Deploy to Google Cloud Run:

```bash
# One-command deployment
./deploy.sh

# Or manually follow the steps below...
```

### Manual Deployment Steps

1. **Enable APIs**:
```bash
gcloud services enable \
  analyticsdata.googleapis.com \
  analyticsadmin.googleapis.com \
  run.googleapis.com \
  artifactregistry.googleapis.com \
  secretmanager.googleapis.com
```

2. **Store ADC in Secret Manager**:
```bash
gcloud secrets create mcp_adc_credentials --replication-policy=automatic
gcloud secrets versions add mcp_adc_credentials \
  --data-file="$HOME/.config/gcloud/application_default_credentials.json"

PROJECT_NUM=$(gcloud projects describe $(gcloud config get-value project) --format="value(projectNumber)")
gcloud secrets add-iam-policy-binding mcp_adc_credentials \
  --member="serviceAccount:${PROJECT_NUM}-compute@developer.gserviceaccount.com" \
  --role="roles/secretmanager.secretAccessor"
```

3. **Build and Push**:
```bash
gcloud artifacts repositories create mcp-repo \
  --repository-format=docker --location=us-central1

gcloud builds submit \
  --tag us-central1-docker.pkg.dev/$(gcloud config get-value project)/mcp-repo/ga4-mcp:latest
```

4. **Deploy to Cloud Run**:
```bash
gcloud run deploy ga4-mcp \
  --image=us-central1-docker.pkg.dev/$(gcloud config get-value project)/mcp-repo/ga4-mcp:latest \
  --region=us-central1 \
  --allow-unauthenticated \
  --memory=2Gi \
  --cpu=2 \
  --execution-environment=gen2 \
  --set-env-vars="GOOGLE_PROJECT_ID=$(gcloud config get-value project)" \
  --update-secrets="/secrets/adc/credentials.json=mcp_adc_credentials:latest"
```

## Phase 4: Connect to Claude Desktop

Add your MCP server to Claude Desktop configuration:

**macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
**Windows**: `%APPDATA%\Claude\claude_desktop_config.json`

```json
{
  "mcpServers": {
    "ga4-mcp": {
      "transport": {
        "type": "http",
        "url": "https://YOUR_CLOUD_RUN_URL"
      },
      "env": {
        "GOOGLE_PROJECT_ID": "YOUR_GCP_PROJECT_ID"
      }
    }
  }
}
```

Get your Cloud Run URL:
```bash
gcloud run services describe ga4-mcp --region us-central1 --format='value(status.url)'
```

Restart Claude Desktop after updating the config.

## Phase 5: Test with Claude

In Claude Desktop, try these commands:

1. **List GA4 accounts**:
   - "Use the ga4-mcp server to list my GA4 accounts"

2. **Run a report**:
   - "Run a GA4 report for property 341922028 for 2025-09-01 to 2025-09-30 with metrics totalUsers, sessions, totalRevenue grouped by defaultChannelGroup"

## Troubleshooting

### Common Issues

1. **Empty tools list**: Increase Cloud Run memory to 4Gi:
   ```bash
   gcloud run services update ga4-mcp --region us-central1 --memory=4Gi
   ```

2. **Authentication errors**: Re-run the ADC setup:
   ```bash
   gcloud auth application-default login
   # Then update the secret
   gcloud secrets versions add mcp_adc_credentials \
     --data-file="$HOME/.config/gcloud/application_default_credentials.json"
   ```

3. **Permission errors**: Ensure your Gmail has GA4 read access to the properties you're querying.

### Viewing Logs

```bash
# Cloud Run logs
gcloud run services logs read ga4-mcp --region us-central1

# Local Docker logs
docker logs ga4-mcp-test
```

## Security Notes

- The server uses your personal Gmail OAuth credentials (ADC)
- No service account is used for API access
- All GA4 calls are made as your user account
- Ensure your Gmail has appropriate GA4 permissions

## Cost Considerations

- Cloud Run charges based on requests and compute time
- Free tier includes 2 million requests per month
- Memory and CPU can be adjusted based on usage
- Consider setting up billing alerts for production use
