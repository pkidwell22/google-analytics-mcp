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

"""Enhanced GSC tools for discovery and preset reporting."""

from typing import Any, Dict, List, Optional

from analytics_mcp.coordinator import mcp


@mcp.tool(title="Find GSC site by domain or URL with best match")
async def sites_find(query: str) -> Dict[str, Any]:
    """Find GSC site by domain or URL with best match.
    
    Args:
        query: Domain or URL to search for
    
    Returns:
        Dict containing best matching site and alternates
    """
    try:
        from analytics_mcp.tools.gsc import gsc_sites_list
        
        sites_result = await gsc_sites_list()
        if sites_result.get('error'):
            return {
                "rows": [],
                "meta": {"query": query, "source": "gsc", "cached": False},
                "error": sites_result['error']
            }
        
        sites = sites_result.get('rows', [])
        query_lower = query.lower().strip()
        
        # Normalize query
        if query_lower.startswith('http'):
            from urllib.parse import urlparse
            parsed = urlparse(query)
            query_domain = parsed.netloc
        else:
            query_domain = query_lower
        
        if query_domain.startswith('www.'):
            query_domain = query_domain[4:]
        
        matches = []
        best_match = None
        best_score = 0
        
        for site in sites:
            site_url = site.get('siteUrl', '')
            if not site_url:
                continue
            
            # Extract domain from site URL
            if site_url.startswith('sc-domain:'):
                site_domain = site_url[10:].lower()
            else:
                from urllib.parse import urlparse
                parsed = urlparse(site_url)
                site_domain = parsed.netloc.lower()
                if site_domain.startswith('www.'):
                    site_domain = site_domain[4:]
            
            # Calculate match score
            score = 0
            if query_domain == site_domain:
                score = 1.0
            elif query_domain in site_domain or site_domain in query_domain:
                score = 0.8
            elif query_lower in site_url.lower():
                score = 0.6
            
            if score > 0:
                site_info = {
                    'site_url': site_url,
                    'permission_level': site.get('permissionLevel', ''),
                    'site_type': 'domain' if site_url.startswith('sc-domain:') else 'url',
                    'match_score': score
                }
                matches.append(site_info)
                
                if score > best_score:
                    best_score = score
                    best_match = site_info
        
        return {
            "rows": matches,
            "meta": {
                "query": query,
                "source": "gsc",
                "cached": False,
                "best_match": best_match,
                "matches_found": len(matches)
            },
            "error": None
        }
        
    except Exception as e:
        return {
            "rows": [],
            "meta": {"query": query, "source": "gsc", "cached": False},
            "error": f"Error finding GSC sites: {e}"
        }


@mcp.tool(title="Get GSC permissions for a site")
async def permissions_get(site_url: str) -> Dict[str, Any]:
    """Get GSC permissions for a site.
    
    Args:
        site_url: GSC site URL
    
    Returns:
        Dict containing permission information
    """
    try:
        from analytics_mcp.tools.gsc import gsc_sites_list
        
        sites_result = await gsc_sites_list()
        if sites_result.get('error'):
            return {
                "rows": [],
                "meta": {"site_url": site_url, "source": "gsc", "cached": False},
                "error": sites_result['error']
            }
        
        sites = sites_result.get('rows', [])
        for site in sites:
            if site.get('siteUrl') == site_url:
                permission_info = {
                    'site_url': site_url,
                    'permission_level': site.get('permissionLevel', ''),
                    'site_type': 'domain' if site_url.startswith('sc-domain:') else 'url',
                    'has_access': True
                }
                return {
                    "rows": [permission_info],
                    "meta": {
                        "site_url": site_url,
                        "source": "gsc",
                        "cached": False
                    },
                    "error": None
                }
        
        return {
            "rows": [],
            "meta": {
                "site_url": site_url,
                "source": "gsc",
                "cached": False
            },
            "error": f"Site '{site_url}' not found in accessible sites"
        }
        
    except Exception as e:
        return {
            "rows": [],
            "meta": {"site_url": site_url, "source": "gsc", "cached": False},
            "error": f"Error getting permissions: {e}"
        }


@mcp.tool(title="Get top queries for a GSC site")
async def top_queries(site_url: str, start_date: str, end_date: str, limit: int = 100) -> Dict[str, Any]:
    """Get top queries for a GSC site.
    
    Args:
        site_url: GSC site URL
        start_date: Start date (YYYY-MM-DD)
        end_date: End date (YYYY-MM-DD)
        limit: Maximum number of results (default: 100)
    
    Returns:
        Dict containing top queries data
    """
    try:
        from analytics_mcp.tools.gsc import gsc_search_analytics_query
        
        result = await gsc_search_analytics_query(
            site_url=site_url,
            start_date=start_date,
            end_date=end_date,
            dimensions=['query'],
            row_limit=limit
        )
        
        # Add metadata
        if result.get('meta'):
            result['meta']['source'] = 'gsc'
            result['meta']['cached'] = False
        
        return result
        
    except Exception as e:
        return {
            "rows": [],
            "meta": {"site_url": site_url, "source": "gsc", "cached": False},
            "error": f"Error getting top queries: {e}"
        }


@mcp.tool(title="Get top pages for a GSC site")
async def top_pages(site_url: str, start_date: str, end_date: str, limit: int = 100) -> Dict[str, Any]:
    """Get top pages for a GSC site.
    
    Args:
        site_url: GSC site URL
        start_date: Start date (YYYY-MM-DD)
        end_date: End date (YYYY-MM-DD)
        limit: Maximum number of results (default: 100)
    
    Returns:
        Dict containing top pages data
    """
    try:
        from analytics_mcp.tools.gsc import gsc_search_analytics_query
        
        result = await gsc_search_analytics_query(
            site_url=site_url,
            start_date=start_date,
            end_date=end_date,
            dimensions=['page'],
            row_limit=limit
        )
        
        # Add metadata
        if result.get('meta'):
            result['meta']['source'] = 'gsc'
            result['meta']['cached'] = False
        
        return result
        
    except Exception as e:
        return {
            "rows": [],
            "meta": {"site_url": site_url, "source": "gsc", "cached": False},
            "error": f"Error getting top pages: {e}"
        }


@mcp.tool(title="Get queries for a specific page in GSC")
async def queries_for_page(site_url: str, page: str, start_date: str, end_date: str, limit: int = 100) -> Dict[str, Any]:
    """Get queries for a specific page in GSC.
    
    Args:
        site_url: GSC site URL
        page: Page URL to analyze
        start_date: Start date (YYYY-MM-DD)
        end_date: End date (YYYY-MM-DD)
        limit: Maximum number of results (default: 100)
    
    Returns:
        Dict containing queries for the page
    """
    try:
        from analytics_mcp.tools.gsc import gsc_search_analytics_query
        
        # Create filter for the specific page
        filters = [{
            "dimension": "page",
            "operator": "equals",
            "expression": page
        }]
        
        result = await gsc_search_analytics_query(
            site_url=site_url,
            start_date=start_date,
            end_date=end_date,
            dimensions=['query'],
            row_limit=limit,
            filters=filters
        )
        
        # Add metadata
        if result.get('meta'):
            result['meta']['source'] = 'gsc'
            result['meta']['cached'] = False
            result['meta']['filtered_page'] = page
        
        return result
        
    except Exception as e:
        return {
            "rows": [],
            "meta": {"site_url": site_url, "page": page, "source": "gsc", "cached": False},
            "error": f"Error getting queries for page: {e}"
        }


@mcp.tool(title="Get country and device matrix for GSC site")
async def country_device_matrix(site_url: str, start_date: str, end_date: str, limit: int = 1000) -> Dict[str, Any]:
    """Get country and device matrix for GSC site.
    
    Args:
        site_url: GSC site URL
        start_date: Start date (YYYY-MM-DD)
        end_date: End date (YYYY-MM-DD)
        limit: Maximum number of results (default: 1000)
    
    Returns:
        Dict containing country and device data
    """
    try:
        from analytics_mcp.tools.gsc import gsc_search_analytics_query
        
        result = await gsc_search_analytics_query(
            site_url=site_url,
            start_date=start_date,
            end_date=end_date,
            dimensions=['country', 'device'],
            row_limit=limit
        )
        
        # Add metadata
        if result.get('meta'):
            result['meta']['source'] = 'gsc'
            result['meta']['cached'] = False
        
        return result
        
    except Exception as e:
        return {
            "rows": [],
            "meta": {"site_url": site_url, "source": "gsc", "cached": False},
            "error": f"Error getting country device matrix: {e}"
        }


@mcp.tool(title="Build GSC search analytics filters")
async def sa_build_filters(include: List[Dict[str, Any]], exclude: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Build GSC search analytics filters from include/exclude lists.
    
    Args:
        include: List of filters to include (AND logic)
        exclude: List of filters to exclude (NOT logic)
    
    Returns:
        Dict containing properly formatted filter groups
    """
    try:
        filter_groups = []
        
        # Build include filters (AND group)
        if include:
            include_group = {
                "groupType": "and",
                "filters": include
            }
            filter_groups.append(include_group)
        
        # Build exclude filters (NOT group)
        if exclude:
            exclude_group = {
                "groupType": "and",
                "filters": [{
                    "dimension": "query",
                    "operator": "notEquals",
                    "expression": "|".join([f["expression"] for f in exclude if "expression" in f])
                }]
            }
            filter_groups.append(exclude_group)
        
        return {
            "rows": [{"dimensionFilterGroups": filter_groups}],
            "meta": {
                "source": "gsc",
                "cached": False,
                "include_count": len(include),
                "exclude_count": len(exclude)
            },
            "error": None
        }
        
    except Exception as e:
        return {
            "rows": [],
            "meta": {"source": "gsc", "cached": False},
            "error": f"Error building filters: {e}"
        }
