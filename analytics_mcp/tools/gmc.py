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

"""Tools for Google Merchant Center integration using the official Merchant API."""

from typing import Any, Dict, List, Optional

from analytics_mcp.coordinator import mcp
from analytics_mcp.tools.utils import _create_credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError


def _get_gmc_service():
    """Returns a Google Merchant Center service client using Content API v2.1."""
    credentials = _create_credentials()
    # Use Content API v2.1 which includes all Merchant Center functionality
    return build("content", "v2.1", credentials=credentials, cache_discovery=False)


@mcp.tool(title="List accessible Merchant Center accounts")
async def gmc_accounts_list() -> Dict[str, Any]:
    """Returns a list of all accessible Merchant Center accounts.
    
    Returns:
        Dict containing accounts list and metadata
    """
    try:
        service = _get_gmc_service()
        # Since the account is not an MCA, we'll get the specific account details
        # Gate Depot merchant ID: 5397681596
        response = service.accounts().get(
            merchantId=5397681596,
            accountId=5397681596
        ).execute()
        
        # Return as a list with one account
        accounts = [response]
        return {
            "rows": accounts,
            "meta": {"count": len(accounts)},
            "error": None
        }
    except HttpError as e:
        return {
            "rows": [],
            "meta": {"count": 0},
            "error": f"Merchant Center accounts.get error: {e}"
        }


@mcp.tool(title="Get Merchant Center account details")
async def gmc_accounts_get(account_id: str) -> Dict[str, Any]:
    """Returns Merchant Center account metadata.
    
    Args:
        account_id: The Merchant Center account ID (e.g., "123456789")
    
    Returns:
        Dict containing account details and metadata
    """
    try:
        service = _get_gmc_service()
        response = service.accounts().get(
            merchantId=account_id,
            accountId=account_id
        ).execute()
        return {
            "rows": [response],
            "meta": {"account_id": account_id},
            "error": None
        }
    except HttpError as e:
        return {
            "rows": [],
            "meta": {"account_id": account_id},
            "error": f"Merchant Center accounts.get error: {e}"
        }


@mcp.tool(title="List products in Merchant Center")
async def gmc_products_list(
    account_id: str,
    page_token: Optional[str] = None,
    page_size: Optional[int] = None
) -> Dict[str, Any]:
    """Returns a list of products in the Merchant Center account.
    
    Args:
        account_id: The Merchant Center account ID (e.g., "123456789")
        page_token: Optional pagination token
        page_size: Optional page size for results
    
    Returns:
        Dict containing products list and metadata
    """
    try:
        service = _get_gmc_service()
        request_params = {"merchantId": account_id}
        if page_token:
            request_params["pageToken"] = page_token
        if page_size:
            request_params["maxResults"] = page_size
            
        response = service.products().list(**request_params).execute()
        products = response.get("resources", [])
        meta = {k: v for k, v in response.items() if k != "resources"}
        return {
            "rows": products,
            "meta": meta,
            "error": None
        }
    except HttpError as e:
        return {
            "rows": [],
            "meta": {"account_id": account_id},
            "error": f"Merchant Center products.list error: {e}"
        }


@mcp.tool(title="Get Merchant Center product details")
async def gmc_products_get(
    account_id: str,
    product_id: str
) -> Dict[str, Any]:
    """Returns details of a specific product in Merchant Center.
    
    Args:
        account_id: The Merchant Center account ID (e.g., "123456789")
        product_id: The product ID
    
    Returns:
        Dict containing product details and metadata
    """
    try:
        service = _get_gmc_service()
        response = service.products().get(
            merchantId=account_id,
            productId=product_id
        ).execute()
        return {
            "rows": [response],
            "meta": {"account_id": account_id, "product_id": product_id},
            "error": None
        }
    except HttpError as e:
        return {
            "rows": [],
            "meta": {"account_id": account_id, "product_id": product_id},
            "error": f"Merchant Center products.get error: {e}"
        }


@mcp.tool(title="List Merchant Center account issues")
async def gmc_accounts_issues_list(
    account_id: str,
    page_token: Optional[str] = None,
    page_size: Optional[int] = None
) -> Dict[str, Any]:
    """Returns a list of issues for the Merchant Center account.
    
    Args:
        account_id: The Merchant Center account ID (e.g., "123456789")
        page_token: Optional pagination token
        page_size: Optional page size for results
    
    Returns:
        Dict containing issues list and metadata
    """
    try:
        service = _get_gmc_service()
        request_params = {"merchantId": account_id}
        if page_token:
            request_params["pageToken"] = page_token
        if page_size:
            request_params["maxResults"] = page_size
            
        response = service.accountstatuses().list(**request_params).execute()
        issues = response.get("resources", [])
        meta = {k: v for k, v in response.items() if k != "resources"}
        return {
            "rows": issues,
            "meta": meta,
            "error": None
        }
    except HttpError as e:
        return {
            "rows": [],
            "meta": {"account_id": account_id},
            "error": f"Merchant Center accountstatuses.list error: {e}"
        }