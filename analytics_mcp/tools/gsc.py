# Copyright 2025 Google LLC All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Tools for Google Search Console integration."""

from typing import Any, Dict, List, Optional

from analytics_mcp.coordinator import mcp
from analytics_mcp.tools.utils import _create_credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError


def _get_gsc_service():
    """Returns a Google Search Console service client."""
    credentials = _create_credentials()
    return build("webmasters", "v3", credentials=credentials, cache_discovery=False)


@mcp.tool(title="List Search Console sites")
async def gsc_sites_list() -> Dict[str, Any]:
    """Returns a list of Search Console sites accessible to the authenticated user.
    
    Returns:
        Dict containing sites list and metadata
    """
    try:
        service = _get_gsc_service()
        response = service.sites().list().execute()
        sites = response.get("siteEntry", [])
        return {
            "sites": sites,
            "count": len(sites),
            "error": None
        }
    except HttpError as e:
        return {
            "sites": [],
            "count": 0,
            "error": f"GSC sites.list error: {e}"
        }


@mcp.tool(title="List sitemaps for a site")
async def gsc_sitemaps_list(site_url: str) -> Dict[str, Any]:
    """Returns a list of sitemaps for a Search Console site.
    
    Args:
        site_url: The site URL (e.g., 'https://www.example.com/' or 'sc-domain:example.com')
    
    Returns:
        Dict containing sitemaps list and metadata
    """
    try:
        service = _get_gsc_service()
        response = service.sitemaps().list(siteUrl=site_url).execute()
        sitemaps = response.get("sitemap", [])
        return {
            "sitemaps": sitemaps,
            "count": len(sitemaps),
            "site_url": site_url,
            "error": None
        }
    except HttpError as e:
        return {
            "sitemaps": [],
            "count": 0,
            "site_url": site_url,
            "error": f"GSC sitemaps.list error: {e}"
        }


@mcp.tool(title="Run Search Analytics query")
async def gsc_search_analytics_query(
    site_url: str,
    start_date: str,
    end_date: str,
    dimensions: List[str] = None,
    row_limit: int = 1000,
    filters: Optional[List[Dict[str, Any]]] = None
) -> Dict[str, Any]:
    """Runs a Search Analytics query to get search performance data.
    
    Args:
        site_url: The site URL (e.g., 'https://www.example.com/' or 'sc-domain:example.com')
        start_date: Start date in YYYY-MM-DD format
        end_date: End date in YYYY-MM-DD format
        dimensions: List of dimensions to group by (e.g., ['query', 'page', 'country', 'device'])
        row_limit: Maximum number of rows to return (default: 1000, max: 25000)
        filters: Optional list of filter objects for dimension filtering
    
    Returns:
        Dict containing search analytics data and metadata
    """
    if dimensions is None:
        dimensions = ["query"]
    
    # Validate required parameters
    if not site_url or not start_date or not end_date:
        return {
            "rows": [],
            "meta": {},
            "error": "Required parameters: site_url, start_date, end_date"
        }
    
    # Prepare request body
    body = {
        "startDate": start_date,
        "endDate": end_date,
        "dimensions": dimensions,
        "rowLimit": min(row_limit, 25000)  # Cap at API limit
    }
    
    # Add filters if provided
    if filters:
        body["dimensionFilterGroups"] = [{"groupType": "and", "filters": filters}]
    
    try:
        service = _get_gsc_service()
        response = service.searchanalytics().query(siteUrl=site_url, body=body).execute()
        
        rows = response.get("rows", [])
        meta = {k: v for k, v in response.items() if k != "rows"}
        
        return {
            "rows": rows,
            "meta": meta,
            "site_url": site_url,
            "date_range": f"{start_date} to {end_date}",
            "dimensions": dimensions,
            "error": None
        }
    except HttpError as e:
        return {
            "rows": [],
            "meta": {},
            "site_url": site_url,
            "date_range": f"{start_date} to {end_date}",
            "dimensions": dimensions,
            "error": f"GSC searchanalytics.query error: {e}"
        }
