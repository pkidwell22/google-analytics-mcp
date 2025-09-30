# Google Analytics MCP Server

A powerful Model Context Protocol (MCP) server that provides comprehensive Google Analytics 4 (GA4), Google Search Console (GSC), and Google Merchant Center (GMC) integration for Claude Desktop and other MCP clients.

## ✨ Key Features

### 🚀 **49 Specialized Tools** Across Google Platforms
- **GA4**: 20+ tools for reporting, admin, and discovery
- **GSC**: 10+ tools for search analytics and site management  
- **GMC**: 11+ tools for merchant center and product management
- **Resolver**: 4 tools for human-friendly ID resolution
- **Whoami**: 1 unified summary tool

### 🧠 **Smart Resolver Layer**
- **Human-friendly queries**: Use domains like "gatedepot.com" instead of cryptic IDs
- **Auto-resolution**: Automatically finds the right property/site/account
- **Fuzzy matching**: Handles typos and variations intelligently
- **Multi-platform**: Works across GA4, GSC, and GMC

### ⚡ **Performance Optimizations**
- **TTL Caching**: 10-minute cache for discovery calls (instant repeat lookups)
- **Auto-retry**: Handles Google API rate limits with exponential backoff
- **Configurable**: Environment variables for cache and retry settings

### 🔒 **Enterprise Security**
- **OAuth Integration**: User-based authentication via Application Default Credentials
- **Secret Management**: Credentials stored securely in Google Secret Manager
- **Read-only Access**: Limited scopes for data protection

## 📊 Available Tools

### GA4 Tools (20 tools)
**Core Reporting:**
- `run_report` - Custom GA4 reports with dimensions, metrics, filters
- `run_realtime_report` - Real-time analytics data
- `get_custom_dimensions_and_metrics` - Property metadata

**Admin Management:**
- `get_account_summaries` - List all GA4 accounts and properties
- `get_property_details` - Detailed property information
- `list_conversion_events` - Conversion event management
- `list_data_streams` - Data stream configuration
- `list_custom_dimensions` - Custom dimension management
- `list_custom_metrics` - Custom metric management
- `list_google_ads_links` - Google Ads integration

**Enhanced Discovery:**
- `properties_list_accounts` - Flattened account/property list
- `properties_find` - Search properties by name/URL
- `datastreams_find` - Find streams by URL/measurement ID
- `report_top_pages` - Top pages preset report
- `report_revenue_by_channel` - Revenue analysis preset
- `report_events_over_time` - Event tracking over time
- `report_landing_pages_vs_conversions` - Landing page analysis

### GSC Tools (10 tools)
**Basic Operations:**
- `gsc_sites_list` - List Search Console sites
- `gsc_sitemaps_list` - Manage sitemaps
- `gsc_search_analytics_query` - Search performance data

**Enhanced Analytics:**
- `sites_find` - Find sites by domain/URL
- `permissions_get` - Site permission details
- `top_queries` - Top search queries preset
- `top_pages` - Top performing pages preset
- `queries_for_page` - Queries driving specific pages
- `country_device_matrix` - Geographic and device analysis
- `sa_build_filters` - Advanced filter builder

### GMC Tools (11 tools)
**Account Management:**
- `gmc_accounts_list` - List Merchant Center accounts
- `gmc_accounts_get` - Account details
- `gmc_accounts_issues_list` - Account issues
- `accounts_list` - Enhanced account listing
- `account_status` - Account status and summary

**Product Management:**
- `gmc_products_list` - List products
- `gmc_products_get` - Product details
- `products_find` - Search products by query
- `product_status` - Individual product status
- `product_status_aggregate` - Bulk product status

**Reporting:**
- `report_issues_last_30d` - Recent issues report

### Resolver Tools (4 tools)
- `find_ga4_property` - Resolve domain/URL to GA4 property
- `find_gsc_site` - Resolve domain/URL to GSC site
- `find_gmc_account` - Resolve domain/brand to GMC account
- `find_google_ads_link` - Find Google Ads links for properties

### Whoami Tool (1 tool)
- `summary` - Unified overview of all accessible accounts and resources

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
- Enable required Google APIs (GA4, GSC, GMC, Cloud Run, Secret Manager)
- Set up Application Default Credentials
- Configure OAuth scopes for all platforms

### 3. Local Testing

```bash
# Build and run with Docker
./test-local.sh

# Or run directly
python3 -m analytics_mcp.server --transport http --port 8080
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
        "url": "https://ga4-mcp-syiiroz2la-uc.a.run.app"
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
- `MCP_CACHE_TTL_SEC`: Cache TTL in seconds (default: 600)
- `MCP_CACHE_MAXSIZE`: Maximum cache entries (default: 2048)
- `MCP_GOOGLE_RETRIES`: API retry attempts (default: 5)

## 💡 Example Usage

### With Claude Desktop

**Natural Language Queries:**
- "Show me revenue by channel for gatedepot.com"
- "What are the top pages for my site?"
- "Find conversion issues in my Merchant Center"
- "List all my Google properties and accounts"
- "Show me search performance for my landing pages"

**Advanced Analytics:**
- "Get top queries driving traffic to /products page"
- "Show me country and device breakdown for last month"
- "Find products with issues in my Merchant Center"
- "Analyze events over time for purchase events"

### Direct API Usage

```bash
# Health check
curl https://ga4-mcp-syiiroz2la-uc.a.run.app/health

# Test cache functionality
bash scripts/smoke_cache.sh
```

## 🏗️ Architecture

```
analytics_mcp/
├── coordinator.py              # MCP server configuration
├── server.py                  # Entry point and transport handling
├── tools/
│   ├── utils.py               # Common utilities and auth
│   ├── reporting/             # GA4 Data API tools
│   ├── admin/                 # GA4 Admin API tools
│   ├── gsc.py                 # Google Search Console tools
│   ├── gsc_enhanced.py        # Enhanced GSC tools
│   ├── gmc.py                 # Google Merchant Center tools
│   ├── gmc_enhanced.py        # Enhanced GMC tools
│   ├── ga4_enhanced.py        # Enhanced GA4 tools
│   ├── resolver.py            # Human-friendly ID resolution
│   └── whoami.py              # Unified account summary
├── utils/
│   ├── cache.py               # TTL caching system
│   └── google_retry.py        # API retry logic
└── scripts/
    └── smoke_cache.sh         # Cache validation script
```

## 🔒 Security

- **OAuth Integration**: User-based authentication via Application Default Credentials
- **Secret Management**: Credentials stored securely in Google Secret Manager
- **Read-only Access**: Limited scopes for data protection
- **No Hardcoded Keys**: All sensitive data externalized
- **Environment-based Config**: Secure configuration via environment variables

## ⚡ Performance Features

### Smart Caching
- **TTL-based**: Configurable cache expiration (default: 10 minutes)
- **Memory efficient**: LRU eviction with configurable max size
- **Transparent**: Cache status visible in `meta.cached` field
- **Selective**: Only caches discovery/resolver calls, not real-time data

### Resilient API Calls
- **Auto-retry**: Handles 429/5xx errors automatically
- **Exponential backoff**: Prevents API hammering
- **Random jitter**: Avoids thundering herd problems
- **Configurable**: Adjustable retry attempts and timing

## 🧪 Testing

### Local Testing

```bash
# Run server locally
python3 -m analytics_mcp.server --transport http --port 8080

# Test specific tools
python3 -c "
import asyncio
from analytics_mcp.tools.resolver import find_ga4_property
# Test your tool here
"
```

### Cache Testing

```bash
# Test cache functionality
bash scripts/smoke_cache.sh

# Test with custom URL
URL=https://your-service-url.run.app bash scripts/smoke_cache.sh
```

## 📈 Real-World Impact

**Before MCP:**
- Copy/paste property IDs like `properties/341922028`
- Switch between multiple Google tools
- Remember different interfaces and APIs
- Manual ID lookups and context switching

**After MCP:**
- Natural language: "Show me revenue for gatedepot.com"
- Unified interface through Claude
- Instant cached lookups
- Automatic error handling and retries

## 🚀 Deployment Scripts

- `setup-oauth.sh` - Initial OAuth setup and API enablement
- `test-local.sh` - Local Docker testing
- `deploy.sh` - Cloud Run deployment with environment variables
- `test-mcp.sh` - MCP server testing
- `scripts/smoke_cache.sh` - Cache validation testing

## 📋 Prerequisites

- Python 3.10+
- Google Cloud Project with billing enabled
- Google Analytics 4 property
- Google Search Console access (optional)
- Google Merchant Center access (optional)
- Docker (for local testing)
- `gcloud` CLI configured

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 License

Apache 2.0 - See LICENSE file for details

## 🆘 Support

- **Issues**: [GitHub Issues](https://github.com/pkidwell22/google-analytics-mcp/issues)
- **Documentation**: See `README_mcp_claude.md` for Claude Desktop setup
- **Deployment**: See `DEPLOYMENT_STEPS.md` for detailed deployment guide

## 🗺️ Roadmap

- [x] **Resolver Layer** - Human-friendly ID resolution
- [x] **TTL Caching** - Performance optimization
- [x] **Auto-retry** - Resilient API calls
- [x] **GMC Integration** - Merchant Center tools
- [x] **Enhanced Tools** - Discovery and preset reports
- [ ] **URL Inspection API** - GSC URL inspection
- [ ] **Batch Operations** - Bulk data operations
- [ ] **Custom Dashboards** - Visualization tools
- [ ] **Export Functionality** - Data export capabilities
- [ ] **Advanced Filtering** - More sophisticated query options

---

**Built with ❤️ for the Claude AI community**