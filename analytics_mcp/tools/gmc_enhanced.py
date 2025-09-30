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

"""Enhanced GMC tools for discovery and reporting."""

from typing import Any, Dict, List, Optional

from analytics_mcp.coordinator import mcp


@mcp.tool(title="List all GMC accounts with detailed information")
async def accounts_list() -> Dict[str, Any]:
    """List all GMC accounts with detailed information.
    
    Returns:
        Dict containing all accessible GMC accounts
    """
    try:
        from analytics_mcp.tools.gmc import gmc_accounts_list
        
        result = await gmc_accounts_list()
        
        # Add metadata
        if result.get('meta'):
            result['meta']['source'] = 'gmc'
            result['meta']['cached'] = False
        
        return result
        
    except Exception as e:
        return {
            "rows": [],
            "meta": {"source": "gmc", "cached": False},
            "error": f"Error listing GMC accounts: {e}"
        }


@mcp.tool(title="Get GMC account status and summary")
async def account_status(merchant_id: str) -> Dict[str, Any]:
    """Get GMC account status and summary.
    
    Args:
        merchant_id: GMC merchant ID
    
    Returns:
        Dict containing account status information
    """
    try:
        from analytics_mcp.tools.gmc import gmc_accounts_get, gmc_accounts_issues_list
        
        # Get account details
        account_result = await gmc_accounts_get(merchant_id)
        if account_result.get('error'):
            return {
                "rows": [],
                "meta": {"merchant_id": merchant_id, "source": "gmc", "cached": False},
                "error": account_result['error']
            }
        
        # Get account issues
        issues_result = await gmc_accounts_issues_list(merchant_id, page_size=50)
        
        account_data = account_result.get('rows', [{}])[0]
        issues_data = issues_result.get('rows', [])
        
        # Build status summary
        status_info = {
            'merchant_id': merchant_id,
            'account_name': account_data.get('name', ''),
            'website_url': account_data.get('websiteUrl', ''),
            'account_type': account_data.get('accountType', ''),
            'total_issues': len(issues_data),
            'issues_by_severity': {},
            'recent_issues': issues_data[:10] if issues_data else []
        }
        
        # Count issues by severity
        for issue in issues_data:
            severity = issue.get('severity', 'unknown')
            status_info['issues_by_severity'][severity] = status_info['issues_by_severity'].get(severity, 0) + 1
        
        return {
            "rows": [status_info],
            "meta": {
                "merchant_id": merchant_id,
                "source": "gmc",
                "cached": False,
                "issues_fetched": len(issues_data)
            },
            "error": None
        }
        
    except Exception as e:
        return {
            "rows": [],
            "meta": {"merchant_id": merchant_id, "source": "gmc", "cached": False},
            "error": f"Error getting account status: {e}"
        }


@mcp.tool(title="Find GMC products by search query")
async def products_find(merchant_id: str, query: str, limit: int = 100) -> Dict[str, Any]:
    """Find GMC products by search query.
    
    Args:
        merchant_id: GMC merchant ID
        query: Search query for product title, ID, or brand
        limit: Maximum number of results (default: 100)
    
    Returns:
        Dict containing matching products
    """
    try:
        from analytics_mcp.tools.gmc import gmc_products_list
        
        # Get all products (we'll filter client-side for now)
        result = await gmc_products_list(merchant_id, page_size=limit)
        if result.get('error'):
            return {
                "rows": [],
                "meta": {"merchant_id": merchant_id, "query": query, "source": "gmc", "cached": False},
                "error": result['error']
            }
        
        products = result.get('rows', [])
        query_lower = query.lower()
        matches = []
        
        for product in products:
            title = product.get('title', '').lower()
            product_id = product.get('id', '').lower()
            brand = product.get('brand', '').lower()
            
            if (query_lower in title or 
                query_lower in product_id or 
                query_lower in brand):
                
                match_info = {
                    'product_id': product.get('id', ''),
                    'title': product.get('title', ''),
                    'brand': product.get('brand', ''),
                    'price': product.get('price', {}),
                    'availability': product.get('availability', ''),
                    'match_reason': 'title' if query_lower in title else 'id' if query_lower in product_id else 'brand'
                }
                matches.append(match_info)
        
        return {
            "rows": matches,
            "meta": {
                "merchant_id": merchant_id,
                "query": query,
                "source": "gmc",
                "cached": False,
                "matches_found": len(matches),
                "total_products_searched": len(products)
            },
            "error": None
        }
        
    except Exception as e:
        return {
            "rows": [],
            "meta": {"merchant_id": merchant_id, "query": query, "source": "gmc", "cached": False},
            "error": f"Error finding products: {e}"
        }


@mcp.tool(title="Get product status for a specific GMC product")
async def product_status(merchant_id: str, offer_id: str) -> Dict[str, Any]:
    """Get product status for a specific GMC product.
    
    Args:
        merchant_id: GMC merchant ID
        offer_id: Product offer ID
    
    Returns:
        Dict containing product status information
    """
    try:
        from analytics_mcp.tools.gmc import gmc_products_get
        
        result = await gmc_products_get(merchant_id, offer_id)
        if result.get('error'):
            return {
                "rows": [],
                "meta": {"merchant_id": merchant_id, "offer_id": offer_id, "source": "gmc", "cached": False},
                "error": result['error']
            }
        
        product = result.get('rows', [{}])[0]
        
        # Extract status information
        status_info = {
            'offer_id': offer_id,
            'title': product.get('title', ''),
            'brand': product.get('brand', ''),
            'availability': product.get('availability', ''),
            'price': product.get('price', {}),
            'condition': product.get('condition', ''),
            'status': product.get('status', ''),
            'issues': product.get('issues', []),
            'warnings': product.get('warnings', [])
        }
        
        return {
            "rows": [status_info],
            "meta": {
                "merchant_id": merchant_id,
                "offer_id": offer_id,
                "source": "gmc",
                "cached": False
            },
            "error": None
        }
        
    except Exception as e:
        return {
            "rows": [],
            "meta": {"merchant_id": merchant_id, "offer_id": offer_id, "source": "gmc", "cached": False},
            "error": f"Error getting product status: {e}"
        }


@mcp.tool(title="Get aggregated product status for GMC account")
async def product_status_aggregate(merchant_id: str, days: int = 30) -> Dict[str, Any]:
    """Get aggregated product status for GMC account.
    
    Args:
        merchant_id: GMC merchant ID
        days: Number of days to look back (default: 30)
    
    Returns:
        Dict containing aggregated product status information
    """
    try:
        from analytics_mcp.tools.gmc import gmc_products_list
        
        # Get products with issues
        result = await gmc_products_list(merchant_id, page_size=1000)
        if result.get('error'):
            return {
                "rows": [],
                "meta": {"merchant_id": merchant_id, "days": days, "source": "gmc", "cached": False},
                "error": result['error']
            }
        
        products = result.get('rows', [])
        
        # Aggregate status information
        status_summary = {
            'merchant_id': merchant_id,
            'total_products': len(products),
            'products_with_issues': 0,
            'products_with_warnings': 0,
            'availability_breakdown': {},
            'status_breakdown': {},
            'common_issues': {},
            'days_analyzed': days
        }
        
        for product in products:
            issues = product.get('issues', [])
            warnings = product.get('warnings', [])
            availability = product.get('availability', 'unknown')
            status = product.get('status', 'unknown')
            
            if issues:
                status_summary['products_with_issues'] += 1
                for issue in issues:
                    issue_type = issue.get('type', 'unknown')
                    status_summary['common_issues'][issue_type] = status_summary['common_issues'].get(issue_type, 0) + 1
            
            if warnings:
                status_summary['products_with_warnings'] += 1
            
            status_summary['availability_breakdown'][availability] = status_summary['availability_breakdown'].get(availability, 0) + 1
            status_summary['status_breakdown'][status] = status_summary['status_breakdown'].get(status, 0) + 1
        
        return {
            "rows": [status_summary],
            "meta": {
                "merchant_id": merchant_id,
                "days": days,
                "source": "gmc",
                "cached": False,
                "products_analyzed": len(products)
            },
            "error": None
        }
        
    except Exception as e:
        return {
            "rows": [],
            "meta": {"merchant_id": merchant_id, "days": days, "source": "gmc", "cached": False},
            "error": f"Error getting aggregated product status: {e}"
        }


@mcp.tool(title="Get GMC issues report for last 30 days")
async def report_issues_last_30d(merchant_id: str) -> Dict[str, Any]:
    """Get GMC issues report for last 30 days.
    
    Args:
        merchant_id: GMC merchant ID
    
    Returns:
        Dict containing issues report
    """
    try:
        from analytics_mcp.tools.gmc import gmc_accounts_issues_list
        
        result = await gmc_accounts_issues_list(merchant_id, page_size=1000)
        if result.get('error'):
            return {
                "rows": [],
                "meta": {"merchant_id": merchant_id, "source": "gmc", "cached": False},
                "error": result['error']
            }
        
        issues = result.get('rows', [])
        
        # Process issues
        issues_summary = {
            'merchant_id': merchant_id,
            'total_issues': len(issues),
            'issues_by_severity': {},
            'issues_by_type': {},
            'recent_issues': issues[:20] if issues else []
        }
        
        for issue in issues:
            severity = issue.get('severity', 'unknown')
            issue_type = issue.get('type', 'unknown')
            
            issues_summary['issues_by_severity'][severity] = issues_summary['issues_by_severity'].get(severity, 0) + 1
            issues_summary['issues_by_type'][issue_type] = issues_summary['issues_by_type'].get(issue_type, 0) + 1
        
        return {
            "rows": [issues_summary],
            "meta": {
                "merchant_id": merchant_id,
                "source": "gmc",
                "cached": False,
                "period": "last_30_days"
            },
            "error": None
        }
        
    except Exception as e:
        return {
            "rows": [],
            "meta": {"merchant_id": merchant_id, "source": "gmc", "cached": False},
            "error": f"Error getting issues report: {e}"
        }
