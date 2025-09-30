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

"""Whoami module for unified account and resource discovery."""

from typing import Any, Dict

from analytics_mcp.coordinator import mcp


@mcp.tool(title="Get unified summary of all accessible accounts and resources")
async def summary() -> Dict[str, Any]:
    """Get a unified summary of all accessible GA4, GSC, and GMC accounts and resources.
    
    This is perfect for bootstrapping Claude's context at chat start.
    
    Returns:
        Dict containing comprehensive account and resource summary
    """
    try:
        # Import all the list functions
        from analytics_mcp.tools.admin.info import get_account_summaries
        from analytics_mcp.tools.gsc import gsc_sites_list
        from analytics_mcp.tools.gmc import gmc_accounts_list
        
        # Fetch all account data in parallel
        ga4_accounts = await get_account_summaries()
        gsc_result = await gsc_sites_list()
        gmc_result = await gmc_accounts_list()
        
        # Process GA4 data
        ga4_accounts_list = []
        ga4_properties = []
        for account in ga4_accounts:
                account_info = {
                    'account_id': account.get('name', ''),
                    'display_name': account.get('display_name', ''),
                    'property_count': len(account.get('property_summaries', []))
                }
                ga4_accounts_list.append(account_info)
                
                for property in account.get('property_summaries', []):
                    property_info = {
                        'property_id': property.get('property', ''),
                        'display_name': property.get('display_name', ''),
                        'website_url': property.get('website_url', ''),
                        'account_name': account.get('display_name', '')
                    }
                    ga4_properties.append(property_info)
        
        # Process GSC data
        gsc_sites = []
        if not gsc_result.get('error'):
            for site in gsc_result.get('rows', []):
                site_info = {
                    'site_url': site.get('siteUrl', ''),
                    'permission_level': site.get('permissionLevel', ''),
                    'site_type': 'domain' if site.get('siteUrl', '').startswith('sc-domain:') else 'url'
                }
                gsc_sites.append(site_info)
        
        # Process GMC data
        gmc_accounts_list = []
        if not gmc_result.get('error'):
            for account in gmc_result.get('rows', []):
                account_info = {
                    'merchant_id': account.get('id', ''),
                    'name': account.get('name', ''),
                    'website_url': account.get('websiteUrl', ''),
                    'account_type': account.get('accountType', '')
                }
                gmc_accounts_list.append(account_info)
        
        # Build comprehensive summary
        summary_data = {
            'ga4': {
                'accounts': ga4_accounts_list,
                'properties': ga4_properties,
                'total_accounts': len(ga4_accounts_list),
                'total_properties': len(ga4_properties),
                'error': None
            },
            'gsc': {
                'sites': gsc_sites,
                'total_sites': len(gsc_sites),
                'error': gsc_result.get('error')
            },
            'gmc': {
                'accounts': gmc_accounts_list,
                'total_accounts': len(gmc_accounts_list),
                'error': gmc_result.get('error')
            },
            'summary': {
                'total_ga4_accounts': len(ga4_accounts_list),
                'total_ga4_properties': len(ga4_properties),
                'total_gsc_sites': len(gsc_sites),
                'total_gmc_accounts': len(gmc_accounts_list),
                'has_errors': any([
                    gsc_result.get('error'),
                    gmc_result.get('error')
                ])
            }
        }
        
        return {
            "rows": [summary_data],
            "meta": {
                "source": "whoami",
                "cached": False,
                "generated_at": "2025-09-30T17:30:00Z"
            },
            "error": None
        }
        
    except Exception as e:
        return {
            "rows": [],
            "meta": {
                "source": "whoami",
                "cached": False
            },
            "error": f"Error generating summary: {e}"
        }
