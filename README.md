# Google Analytics MCP Server

A powerful Model Context Protocol (MCP) server that provides comprehensive Google Analytics 4 (GA4) and Google Search Console (GSC) integration for Claude Desktop and other MCP clients.

## 🚀 Features

### Google Analytics 4 (GA4) Tools (20 tools)
- **Reporting**: Run custom reports with dimensions, metrics, filters, and date ranges
- **Realtime**: Get real-time analytics data
- **Admin**: Manage conversion events, data streams, custom dimensions/metrics
- **Account Management**: List accounts, properties, and Google Ads links

### Google Search Console (GSC) Tools (3 tools)
- **Sites**: List all Search Console sites
- **Sitemaps**: Manage and list sitemaps for sites
- **Search Analytics**: Query search performance data with dimensions and filters

### Deployment Options
- **Cloud Run**: Production-ready deployment with auto-scaling
- **Docker**: Local development and testing
- **Claude Desktop**: Direct integration via HTTP transport

## 📋 Prerequisites

- Python 3.10+
- Google Cloud Project with billing enabled
- Google Analytics 4 property
- Google Search Console access (optional)
- Docker (for local testing)
- `gcloud` CLI configured

## 🛠️ Quick Start

### 1. Clone and Setup

```bash
git clone https://github.com/pkidwell22/google-analytics-mcp.git
cd google-analytics-mcp
pip install -e .
```

### 2. Authentication Setup

```bash
# Run the OAuth setup script
./setup-oauth.sh
```

This will:
- Enable required Google APIs
- Set up Application Default Credentials
- Configure OAuth scopes for GA4 and GSC

### 3. Local Testing

```bash
# Build and run with Docker
./test-local.sh
```

### 4. Cloud Run Deployment

```bash
# Deploy to Google Cloud Run
./deploy.sh
```

## 🔧 Configuration

### Claude Desktop Integration

Add to your `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "ga4-mcp": {
      "transport": {
        "type": "http",
        "url": "https://your-service-url.run.app/mcp"
      },
      "env": {
        "GOOGLE_PROJECT_ID": "your-project-id"
      }
    }
  }
}
```

### Environment Variables

- `GOOGLE_PROJECT_ID`: Your Google Cloud Project ID
- `GOOGLE_APPLICATION_CREDENTIALS`: Path to credentials file (auto-configured in Cloud Run)

## 📊 Available Tools

### GA4 Reporting Tools
- `run_report` - Run custom GA4 reports
- `run_realtime_report` - Get real-time data
- `get_account_summaries` - List GA4 accounts

### GA4 Admin Tools
- `list_conversion_events` - List conversion events
- `get_conversion_event` - Get conversion event details
- `list_data_streams` - List data streams
- `get_data_stream` - Get data stream details
- `list_custom_dimensions` - List custom dimensions
- `get_custom_dimension` - Get custom dimension details
- `list_custom_metrics` - List custom metrics
- `get_custom_metric` - Get custom metric details

### GSC Tools
- `gsc_sites_list` - List Search Console sites
- `gsc_sitemaps_list` - List sitemaps for a site
- `gsc_search_analytics_query` - Query search performance data

## 💡 Example Usage

### With Claude Desktop

Ask Claude to:
- "List all my GA4 accounts and properties"
- "Show me top pages by traffic for the last 30 days"
- "Get search performance data for my website"
- "List all conversion events for property 123456789"

### Direct API Usage

```bash
# Health check
curl https://your-service-url.run.app/health

# List tools (requires MCP session)
curl -X POST https://your-service-url.run.app/mcp \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -d '{"jsonrpc":"2.0","id":"1","method":"tools/list","params":{}}'
```

## 🏗️ Architecture

```
analytics_mcp/
├── coordinator.py          # MCP server configuration
├── server.py              # Entry point and transport handling
├── tools/
│   ├── utils.py           # Common utilities and auth
│   ├── reporting/         # GA4 Data API tools
│   ├── admin/             # GA4 Admin API tools
│   └── gsc.py             # Google Search Console tools
└── __init__.py
```

## 🔐 Security

- Uses Application Default Credentials (ADC)
- No service account keys stored in code
- OAuth scopes limited to read-only access
- Credentials stored securely in Google Secret Manager (Cloud Run)
- Local credentials in `~/.config/gcloud/application_default_credentials.json`

## 📝 Development

### Adding New Tools

1. Create tool function in appropriate module
2. Use `@mcp.tool()` decorator
3. Import in `server.py`
4. Test locally and deploy

### Testing

```bash
# Run local tests
python3 -m analytics_mcp.server --transport http --port 8080

# Test specific tools
python3 -c "
import asyncio
from analytics_mcp.tools.reporting.core import run_report
# Test your tool here
"
```

## 🚀 Deployment Scripts

- `setup-oauth.sh` - Initial OAuth setup
- `test-local.sh` - Local Docker testing
- `deploy.sh` - Cloud Run deployment
- `test-mcp.sh` - MCP server testing

## 📄 License

Apache 2.0 - See LICENSE file for details

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📞 Support

- Issues: [GitHub Issues](https://github.com/pkidwell22/google-analytics-mcp/issues)
- Documentation: See `README_mcp_claude.md` for Claude Desktop setup

## 🎯 Roadmap

- [ ] URL Inspection API for GSC
- [ ] Enhanced filtering options
- [ ] Batch operations
- [ ] Custom dashboard tools
- [ ] Export functionality

---

**Built with ❤️ for the Claude Desktop community**