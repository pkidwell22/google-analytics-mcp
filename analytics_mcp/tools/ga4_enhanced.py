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

"""Enhanced GA4 tools for discovery and preset reporting."""

from typing import Any, Dict, List, Optional

from analytics_mcp.coordinator import mcp
from analytics_mcp.tools.utils import _create_credentials
from google.analytics.data_v1beta import BetaAnalyticsDataClient
from google.analytics.data_v1beta.types import (
    DateRange,
    Dimension,
    Metric,
    RunReportRequest
)


@mcp.tool(title="List all GA4 accounts and properties in a flattened format")
async def properties_list_accounts() -> Dict[str, Any]:
    """List all GA4 accounts and properties in a flattened, easy-to-scan format.
    
    Returns:
        Dict containing flattened list of all accounts and properties
    """
    try:
        from analytics_mcp.tools.admin.info import get_account_summaries
        
        accounts = await get_account_summaries()
        flattened = []
        
        for account in accounts:
            account_info = {
                'account_id': account.get('name', ''),
                'account_display_name': account.get('display_name', ''),
                'property_count': len(account.get('property_summaries', []))
            }
            
            for property in account.get('property_summaries', []):
                property_info = {
                    'account_id': account.get('name', ''),
                    'account_display_name': account.get('display_name', ''),
                    'property_id': property.get('property', ''),
                    'property_display_name': property.get('display_name', ''),
                    'website_url': property.get('website_url', ''),
                    'time_zone': property.get('time_zone', ''),
                    'currency_code': property.get('currency_code', '')
                }
                flattened.append(property_info)
        
        return {
            "rows": flattened,
            "meta": {
                "source": "ga4",
                "cached": False,
                "total_accounts": len(accounts),
                "total_properties": len(flattened)
            },
            "error": None
        }
        
    except Exception as e:
        return {
            "rows": [],
            "meta": {"source": "ga4", "cached": False},
            "error": f"Error listing properties: {e}"
        }


@mcp.tool(title="Find GA4 properties by name or URL search")
async def properties_find(query: str) -> Dict[str, Any]:
    """Find GA4 properties by searching property name or website URL.
    
    Args:
        query: Search query for property name or URL
    
    Returns:
        Dict containing matching properties
    """
    try:
        from analytics_mcp.tools.admin.info import get_account_summaries
        
        accounts = await get_account_summaries()
        query_lower = query.lower()
        matches = []
        
        for account in accounts:
            for property in account.get('property_summaries', []):
                property_name = property.get('display_name', '').lower()
                website_url = property.get('website_url', '').lower()
                
                if (query_lower in property_name or 
                    query_lower in website_url or
                    query_lower in property.get('property', '').lower()):
                    
                    match_info = {
                        'account_id': account.get('name', ''),
                        'account_display_name': account.get('display_name', ''),
                        'property_id': property.get('property', ''),
                        'property_display_name': property.get('display_name', ''),
                        'website_url': property.get('website_url', ''),
                        'match_reason': 'name' if query_lower in property_name else 'url'
                    }
                    matches.append(match_info)
        
        return {
            "rows": matches,
            "meta": {
                "query": query,
                "source": "ga4",
                "cached": False,
                "matches_found": len(matches)
            },
            "error": None
        }
        
    except Exception as e:
        return {
            "rows": [],
            "meta": {"query": query, "source": "ga4", "cached": False},
            "error": f"Error finding properties: {e}"
        }


@mcp.tool(title="Find data stream by property and URL or measurement ID")
async def datastreams_find(property_id: str, url: Optional[str] = None, measurement_id: Optional[str] = None) -> Dict[str, Any]:
    """Find data stream by property and URL or measurement ID.
    
    Args:
        property_id: GA4 property ID
        url: Website URL to match
        measurement_id: Measurement ID to match
    
    Returns:
        Dict containing matching data streams
    """
    try:
        from analytics_mcp.tools.admin.data_streams import list_data_streams
        
        streams_result = await list_data_streams(property_id)
        if streams_result.get('error'):
            return {
                "rows": [],
                "meta": {"property_id": property_id, "source": "ga4", "cached": False},
                "error": streams_result['error']
            }
        
        streams = streams_result.get('rows', [])
        matches = []
        
        for stream in streams:
            stream_url = stream.get('webStreamData', {}).get('defaultUri', '')
            stream_measurement_id = stream.get('webStreamData', {}).get('measurementId', '')
            
            match = False
            match_reason = []
            
            if url and url.lower() in stream_url.lower():
                match = True
                match_reason.append('url')
            
            if measurement_id and measurement_id in stream_measurement_id:
                match = True
                match_reason.append('measurement_id')
            
            if match:
                stream_info = {
                    'stream_id': stream.get('name', ''),
                    'display_name': stream.get('displayName', ''),
                    'type': stream.get('type', ''),
                    'website_url': stream_url,
                    'measurement_id': stream_measurement_id,
                    'match_reason': ', '.join(match_reason)
                }
                matches.append(stream_info)
        
        return {
            "rows": matches,
            "meta": {
                "property_id": property_id,
                "source": "ga4",
                "cached": False,
                "matches_found": len(matches)
            },
            "error": None
        }
        
    except Exception as e:
        return {
            "rows": [],
            "meta": {"property_id": property_id, "source": "ga4", "cached": False},
            "error": f"Error finding data streams: {e}"
        }


@mcp.tool(title="Get top pages report for a GA4 property")
async def report_top_pages(property_id: str, start_date: str, end_date: str, limit: int = 50) -> Dict[str, Any]:
    """Get top pages report for a GA4 property.
    
    Args:
        property_id: GA4 property ID
        start_date: Start date (YYYY-MM-DD)
        end_date: End date (YYYY-MM-DD)
        limit: Maximum number of results (default: 50)
    
    Returns:
        Dict containing top pages data
    """
    try:
        from analytics_mcp.tools.reporting.core import run_report
        
        request_body = {
            "property": property_id,
            "dateRanges": [{"startDate": start_date, "endDate": end_date}],
            "dimensions": [{"name": "pagePath"}],
            "metrics": [
                {"name": "screenPageViews"},
                {"name": "sessions"},
                {"name": "users"},
                {"name": "bounceRate"}
            ],
            "orderBys": [{"metric": {"metricName": "screenPageViews"}, "desc": True}],
            "limit": limit
        }
        
        result = await run_report(request_body)
        return result
        
    except Exception as e:
        return {
            "rows": [],
            "meta": {"property_id": property_id, "source": "ga4", "cached": False},
            "error": f"Error generating top pages report: {e}"
        }


@mcp.tool(title="Get revenue by channel report for a GA4 property")
async def report_revenue_by_channel(property_id: str, start_date: str, end_date: str) -> Dict[str, Any]:
    """Get revenue by channel report for a GA4 property.
    
    Args:
        property_id: GA4 property ID
        start_date: Start date (YYYY-MM-DD)
        end_date: End date (YYYY-MM-DD)
    
    Returns:
        Dict containing revenue by channel data
    """
    try:
        from analytics_mcp.tools.reporting.core import run_report
        
        request_body = {
            "property": property_id,
            "dateRanges": [{"startDate": start_date, "endDate": end_date}],
            "dimensions": [{"name": "sessionDefaultChannelGroup"}],
            "metrics": [
                {"name": "totalRevenue"},
                {"name": "purchaseRevenue"},
                {"name": "sessions"},
                {"name": "transactions"},
                {"name": "conversions"}
            ],
            "orderBys": [{"metric": {"metricName": "totalRevenue"}, "desc": True}]
        }
        
        result = await run_report(request_body)
        return result
        
    except Exception as e:
        return {
            "rows": [],
            "meta": {"property_id": property_id, "source": "ga4", "cached": False},
            "error": f"Error generating revenue by channel report: {e}"
        }


@mcp.tool(title="Get events over time report for a GA4 property")
async def report_events_over_time(property_id: str, start_date: str, end_date: str, event_name: str, granularity: str = 'day') -> Dict[str, Any]:
    """Get events over time report for a GA4 property.
    
    Args:
        property_id: GA4 property ID
        start_date: Start date (YYYY-MM-DD)
        end_date: End date (YYYY-MM-DD)
        event_name: Event name to track
        granularity: Time granularity ('day', 'week', 'month')
    
    Returns:
        Dict containing events over time data
    """
    try:
        from analytics_mcp.tools.reporting.core import run_report
        
        # Map granularity to GA4 dimension
        granularity_map = {
            'day': 'date',
            'week': 'yearWeek',
            'month': 'yearMonth'
        }
        
        time_dimension = granularity_map.get(granularity, 'date')
        
        request_body = {
            "property": property_id,
            "dateRanges": [{"startDate": start_date, "endDate": end_date}],
            "dimensions": [{"name": time_dimension}],
            "metrics": [
                {"name": "eventCount"},
                {"name": "totalUsers"}
            ],
            "dimensionFilter": {
                "filter": {
                    "fieldName": "eventName",
                    "stringFilter": {
                        "matchType": "EXACT",
                        "value": event_name,
                        "caseSensitive": False
                    }
                }
            },
            "orderBys": [{"dimension": {"dimensionName": time_dimension}, "desc": False}]
        }
        
        result = await run_report(request_body)
        return result
        
    except Exception as e:
        return {
            "rows": [],
            "meta": {"property_id": property_id, "source": "ga4", "cached": False},
            "error": f"Error generating events over time report: {e}"
        }


@mcp.tool(title="Get landing pages vs conversions report for a GA4 property")
async def report_landing_pages_vs_conversions(property_id: str, start_date: str, end_date: str, limit: int = 100) -> Dict[str, Any]:
    """Get landing pages vs conversions report for a GA4 property.
    
    Args:
        property_id: GA4 property ID
        start_date: Start date (YYYY-MM-DD)
        end_date: End date (YYYY-MM-DD)
        limit: Maximum number of results (default: 100)
    
    Returns:
        Dict containing landing pages vs conversions data
    """
    try:
        from analytics_mcp.tools.reporting.core import run_report
        
        request_body = {
            "property": property_id,
            "dateRanges": [{"startDate": start_date, "endDate": end_date}],
            "dimensions": [{"name": "landingPage"}],
            "metrics": [
                {"name": "sessions"},
                {"name": "conversions"},
                {"name": "conversionRate"},
                {"name": "bounceRate"},
                {"name": "averageSessionDuration"}
            ],
            "orderBys": [{"metric": {"metricName": "sessions"}, "desc": True}],
            "limit": limit
        }
        
        result = await run_report(request_body)
        return result
        
    except Exception as e:
        return {
            "rows": [],
            "meta": {"property_id": property_id, "source": "ga4", "cached": False},
            "error": f"Error generating landing pages vs conversions report: {e}"
        }
