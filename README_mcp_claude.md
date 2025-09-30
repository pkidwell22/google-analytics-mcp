# Claude Desktop + Google Analytics MCP Setup

This guide shows you how to connect Claude Desktop to your Google Analytics MCP server running on Cloud Run.

## The Issue
Claude Desktop needs to establish an **SSE (Server-Sent Events) session** first, not just make direct HTTP POST requests. The server is working fine, but the transport protocol requires proper session management.

## Option A: Direct SSE Connection (Recommended)

### 1. Update Claude Desktop Config

**macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
**Windows**: `%APPDATA%\Claude\claude_desktop_config.json`

```json
{
  "mcpServers": {
    "ga4-mcp": {
      "transport": {
        "type": "http",
        "url": "https://ga4-mcp-265267513550.us-central1.run.app/sse"
      },
      "env": {
        "GOOGLE_PROJECT_ID": "continual-rhino-472501-i6"
      }
    }
  }
}
```

### 2. Restart Claude Desktop

After updating the config, restart Claude Desktop completely.

## Option B: Using Cloud Run Proxy (Alternative)

If Option A doesn't work, use the Cloud Run proxy:

### 1. Start the Proxy
```bash
gcloud run services proxy ga4-mcp --region us-central1 --port=3000
```

### 2. Update Claude Desktop Config
```json
{
  "mcpServers": {
    "ga4-mcp": {
      "transport": {
        "type": "http",
        "url": "http://localhost:3000/sse"
      }
    }
  }
}
```

## Option C: Using mcp-remote Shim (Fallback)

If Claude Desktop doesn't support direct HTTP URLs:

```json
{
  "mcpServers": {
    "ga4-mcp": {
      "command": "npx",
      "args": ["-y", "mcp-remote", "https://ga4-mcp-265267513550.us-central1.run.app/sse"]
    }
  }
}
```

## Testing the Connection

### 1. Test SSE Endpoint
```bash
curl -iN https://ga4-mcp-265267513550.us-central1.run.app/sse
```
You should see an event stream with session information.

### 2. Test MCP Tools in Claude
After restarting Claude Desktop, try these commands:

- **"Use the ga4-mcp server to list my GA4 accounts"**
- **"Run a GA4 report for property 341922028 for 2025-09-01 to 2025-09-30 with metrics totalUsers, sessions, totalRevenue grouped by defaultChannelGroup"**

## Available Tools

- `get_account_summaries` - List GA4 accounts
- `run_report` - Run GA4 reports
- `run_realtime_report` - Run realtime reports
- `get_property_details` - Get property info
- `list_google_ads_links` - List Google Ads links
- `get_custom_dimensions_and_metrics` - Get custom dimensions/metrics

## Troubleshooting

### Check Claude Desktop Logs
- **macOS**: `~/Library/Logs/Claude/mcp*.log`
- **Windows**: `%APPDATA%\Claude\logs\mcp*.log`

Look for errors like "session id missing" or transport mismatches.

### Verify Server Health
```bash
curl https://ga4-mcp-265267513550.us-central1.run.app/health
```
Should return: `{"status":"healthy","service":"Google Analytics MCP Server"}`

### Test MCP Protocol
```bash
curl -X POST https://ga4-mcp-265267513550.us-central1.run.app/mcp \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -d '{"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {"protocolVersion": "2024-11-05", "capabilities": {}, "clientInfo": {"name": "test-client", "version": "1.0.0"}}}'
```

## Why This Works

- Cloud Run supports **streamable HTTP (SSE)** for MCP, not stdio
- Clients must create a session via the SSE endpoint (`/sse`)
- The session ID must be included in subsequent JSON-RPC calls
- The `/mcp` endpoint requires proper session management

## Server Details

- **URL**: https://ga4-mcp-265267513550.us-central1.run.app
- **Health**: `/health`
- **SSE Endpoint**: `/sse` (for session establishment)
- **MCP Endpoint**: `/mcp` (for JSON-RPC calls)
- **Project**: continual-rhino-472501-i6
