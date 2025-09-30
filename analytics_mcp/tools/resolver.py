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

"""Resolver module for human-friendly ID resolution across GA4, GSC, and GMC."""

import os
import re
from typing import Any, Dict, List, Optional
from urllib.parse import urlparse

from analytics_mcp.coordinator import mcp
from analytics_mcp.utils.cache import TTLCache, ttl_memoize

# Initialize cache for resolver operations
_resolver_cache = TTLCache(
    maxsize=int(os.getenv("MCP_CACHE_MAXSIZE", "2048")),
    ttl=float(os.getenv("MCP_CACHE_TTL_SEC", "600"))  # 10 min default
)
from analytics_mcp.tools.utils import _create_credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError


def _normalize_domain(domain_or_url: str) -> str:
    """Normalize domain/URL to consistent format."""
    if not domain_or_url:
        return ""
    
    # Remove protocol
    if domain_or_url.startswith(('http://', 'https://')):
        domain_or_url = domain_or_url.split('://', 1)[1]
    
    # Remove www prefix
    if domain_or_url.startswith('www.'):
        domain_or_url = domain_or_url[4:]
    
    # Remove trailing slash
    domain_or_url = domain_or_url.rstrip('/')
    
    return domain_or_url.lower()


def _fuzzy_match(query: str, candidates: List[str], threshold: float = 0.6) -> Optional[str]:
    """Simple fuzzy matching for domain/name resolution."""
    if not query or not candidates:
        return None
    
    query = query.lower().strip()
    best_match = None
    best_score = 0
    
    for candidate in candidates:
        candidate = candidate.lower().strip()
        
        # Exact match
        if query == candidate:
            return candidate
        
        # Contains match
        if query in candidate or candidate in query:
            score = len(query) / len(candidate) if len(candidate) > 0 else 0
            if score > best_score:
                best_score = score
                best_match = candidate
        
        # Domain similarity
        if '.' in query and '.' in candidate:
            query_parts = query.split('.')
            candidate_parts = candidate.split('.')
            if len(query_parts) >= 2 and len(candidate_parts) >= 2:
                if query_parts[-2:] == candidate_parts[-2:]:  # Same domain + TLD
                    score = 0.8
                    if score > best_score:
                        best_score = score
                        best_match = candidate
    
    return best_match if best_score >= threshold else None


@ttl_memoize(_resolver_cache)
async def _find_ga4_property_internal(query: str) -> Dict[str, Any]:
    """Find GA4 property by domain, URL, or property name.
    
    Args:
        query: Domain (e.g., 'gatedepot.com'), URL, or property name
    
    Returns:
        Dict containing property details and resolution metadata
    """
    try:
        from analytics_mcp.tools.admin.info import get_account_summaries
        
        # Get all accounts and properties
        accounts = await get_account_summaries()
        normalized_query = _normalize_domain(query)
        
        # Build list of all properties with their details
        all_properties = []
        for account in accounts:
            for property in account.get('property_summaries', []):
                property_info = {
                    'property_id': property.get('property'),
                    'property_display_name': property.get('display_name', ''),
                    'website_url': property.get('website_url', ''),
                    'account_display_name': account.get('display_name', ''),
                    'account_id': account.get('name', '')
                }
                all_properties.append(property_info)
        
        # Try to match by website URL first (prioritize properties with URLs)
        for prop in all_properties:
            if prop['website_url']:
                prop_domain = _normalize_domain(prop['website_url'])
                if normalized_query == prop_domain or normalized_query in prop_domain:
                    return {
                        "rows": [prop],
                        "meta": {
                            "query": query,
                            "resolved": {
                                "property_id": prop['property_id'],
                                "method": "website_url_match"
                            },
                            "source": "ga4"
                        },
                        "error": None
                    }
        
        # Also try to match by display name that contains domain info
        for prop in all_properties:
            if prop['property_display_name'] and prop['website_url']:  # Only properties with both name and URL
                display_name = prop['property_display_name'].lower()
                if (normalized_query in display_name or 
                    query.lower() in display_name):
                    return {
                        "rows": [prop],
                        "meta": {
                            "query": query,
                            "resolved": {
                                "property_id": prop['property_id'],
                                "method": "display_name_with_url_match"
                            },
                            "source": "ga4"
                        },
                        "error": None
                    }
        
        # Try to match by display name (which often contains domain info)
        for prop in all_properties:
            if prop['property_display_name']:
                display_name = prop['property_display_name'].lower()
                if (normalized_query in display_name or 
                    query.lower() in display_name):
                    return {
                        "rows": [prop],
                        "meta": {
                            "query": query,
                            "resolved": {
                                "property_id": prop['property_id'],
                                "method": "display_name_match"
                            },
                            "source": "ga4"
                        },
                        "error": None
                    }
        
        # Try fuzzy matching on display names
        display_names = [prop['property_display_name'] for prop in all_properties if prop['property_display_name']]
        name_match = _fuzzy_match(query, display_names)
        if name_match:
            for prop in all_properties:
                if prop['property_display_name'].lower() == name_match.lower():
                    return {
                        "rows": [prop],
                        "meta": {
                            "query": query,
                            "resolved": {
                                "property_id": prop['property_id'],
                                "method": "fuzzy_name_match"
                            },
                            "source": "ga4"
                        },
                        "error": None
                    }
        
        # No match found
        return {
            "rows": [],
            "meta": {
                "query": query,
                "resolved": None,
                "source": "ga4",
                "available_properties": len(all_properties)
            },
            "error": f"No GA4 property found matching '{query}'. Found {len(all_properties)} properties total."
        }
        
    except Exception as e:
        return {
            "rows": [],
            "meta": {"query": query, "resolved": None, "source": "ga4"},
            "error": f"Error finding GA4 property: {e}"
        }


@mcp.tool(title="Find GA4 property by domain, URL, or name")
async def find_ga4_property(query: str) -> Dict[str, Any]:
    """Find GA4 property by domain, URL, or property name.
    
    Args:
        query: Domain (e.g., 'gatedepot.com'), URL, or property name
    
    Returns:
        Dict containing property details and resolution metadata
    """
    result, cached = await _find_ga4_property_internal(query)
    result["meta"]["cached"] = cached
    return result


@ttl_memoize(_resolver_cache)
async def _find_gsc_site_internal(query: str) -> Dict[str, Any]:
    """Find GSC site by domain or URL.
    
    Args:
        query: Domain (e.g., 'gatedepot.com') or URL
    
    Returns:
        Dict containing site details and resolution metadata
    """
    try:
        from analytics_mcp.tools.gsc import gsc_sites_list
        
        # Get all GSC sites
        sites_result = await gsc_sites_list()
        if sites_result.get('error'):
            return {
                "rows": [],
                "meta": {"query": query, "resolved": None, "error": sites_result['error']},
                "error": f"Failed to fetch GSC sites: {sites_result['error']}"
            }
        
        sites = sites_result.get('rows', [])
        normalized_query = _normalize_domain(query)
        
        # Try to match sites
        for site in sites:
            site_url = site.get('siteUrl', '')
            if not site_url:
                continue
                
            # Normalize site URL for comparison
            if site_url.startswith('sc-domain:'):
                domain_part = site_url[10:]  # Remove 'sc-domain:' prefix
                site_domain = _normalize_domain(domain_part)
            else:
                site_domain = _normalize_domain(site_url)
            
            if normalized_query == site_domain or normalized_query in site_domain:
                return {
                    "rows": [site],
                    "meta": {
                        "query": query,
                        "resolved": {
                            "site_url": site_url,
                            "method": "domain_match"
                        },
                        "source": "gsc"
                    },
                    "error": None
                }
        
        # No match found
        return {
            "rows": [],
            "meta": {
                "query": query,
                "resolved": None,
                "source": "gsc",
                "available_sites": len(sites)
            },
            "error": f"No GSC site found matching '{query}'. Found {len(sites)} sites total."
        }
        
    except Exception as e:
        return {
            "rows": [],
            "meta": {"query": query, "resolved": None, "source": "gsc"},
            "error": f"Error finding GSC site: {e}"
        }


@mcp.tool(title="Find GSC site by domain or URL")
async def find_gsc_site(query: str) -> Dict[str, Any]:
    """Find GSC site by domain or URL.
    
    Args:
        query: Domain (e.g., 'gatedepot.com') or URL
    
    Returns:
        Dict containing site details and resolution metadata
    """
    result, cached = await _find_gsc_site_internal(query)
    result["meta"]["cached"] = cached
    return result


@ttl_memoize(_resolver_cache)
async def _find_gmc_account_internal(query: str) -> Dict[str, Any]:
    """Find GMC account by domain, brand, or account name.
    
    Args:
        query: Domain, brand name, or account name
    
    Returns:
        Dict containing account details and resolution metadata
    """
    try:
        from analytics_mcp.tools.gmc import gmc_accounts_list
        
        # Get all GMC accounts
        accounts_result = await gmc_accounts_list()
        if accounts_result.get('error'):
            return {
                "rows": [],
                "meta": {"query": query, "resolved": None, "error": accounts_result['error']},
                "error": f"Failed to fetch GMC accounts: {accounts_result['error']}"
            }
        
        accounts = accounts_result.get('rows', [])
        normalized_query = _normalize_domain(query)
        
        # Try to match by account name first
        account_names = [acc.get('name', '') for acc in accounts if acc.get('name')]
        name_match = _fuzzy_match(query, account_names)
        if name_match:
            for account in accounts:
                if account.get('name', '').lower() == name_match.lower():
                    return {
                        "rows": [account],
                        "meta": {
                            "query": query,
                            "resolved": {
                                "merchant_id": account.get('id'),
                                "method": "name_match"
                            },
                            "source": "gmc"
                        },
                        "error": None
                    }
        
        # Try to match by website URL if available
        for account in accounts:
            website_url = account.get('websiteUrl', '')
            if website_url:
                account_domain = _normalize_domain(website_url)
                if normalized_query == account_domain or normalized_query in account_domain:
                    return {
                        "rows": [account],
                        "meta": {
                            "query": query,
                            "resolved": {
                                "merchant_id": account.get('id'),
                                "method": "website_url_match"
                            },
                            "source": "gmc"
                        },
                        "error": None
                    }
        
        # No match found
        return {
            "rows": [],
            "meta": {
                "query": query,
                "resolved": None,
                "source": "gmc",
                "available_accounts": len(accounts)
            },
            "error": f"No GMC account found matching '{query}'. Found {len(accounts)} accounts total."
        }
        
    except Exception as e:
        return {
            "rows": [],
            "meta": {"query": query, "resolved": None, "source": "gmc"},
            "error": f"Error finding GMC account: {e}"
        }


@mcp.tool(title="Find GMC account by domain, brand, or name")
async def find_gmc_account(query: str) -> Dict[str, Any]:
    """Find GMC account by domain, brand, or account name.
    
    Args:
        query: Domain, brand name, or account name
    
    Returns:
        Dict containing account details and resolution metadata
    """
    result, cached = await _find_gmc_account_internal(query)
    result["meta"]["cached"] = cached
    return result


@mcp.tool(title="Find Google Ads links for a GA4 property")
async def find_google_ads_link(property_id: str) -> Dict[str, Any]:
    """Find Google Ads links for a GA4 property.
    
    Args:
        property_id: GA4 property ID (e.g., 'properties/123456789')
    
    Returns:
        Dict containing Google Ads links and metadata
    """
    try:
        from analytics_mcp.tools.admin.info import list_google_ads_links
        
        # Get Google Ads links for the property
        links_result = await list_google_ads_links(property_id)
        if links_result.get('error'):
            return {
                "rows": [],
                "meta": {"property_id": property_id, "resolved": None, "error": links_result['error']},
                "error": f"Failed to fetch Google Ads links: {links_result['error']}"
            }
        
        links = links_result.get('rows', [])
        return {
            "rows": links,
            "meta": {
                "property_id": property_id,
                "resolved": {
                    "links_found": len(links),
                    "method": "direct_lookup"
                },
                "source": "ga4_ads"
            },
            "error": None
        }
        
    except Exception as e:
        return {
            "rows": [],
            "meta": {"property_id": property_id, "resolved": None, "source": "ga4_ads"},
            "error": f"Error finding Google Ads links: {e}"
        }
