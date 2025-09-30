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

"""Enhanced tools for managing Google Analytics custom dimensions and metrics."""

from typing import Any, Dict, List

from analytics_mcp.coordinator import mcp
from analytics_mcp.tools.utils import (
    construct_property_rn,
    create_admin_api_client,
    proto_to_dict,
)
from google.analytics import admin_v1beta


@mcp.tool(title="List all custom dimensions for a property")
async def list_custom_dimensions(property_id: int | str) -> List[Dict[str, Any]]:
    """Returns a detailed list of all custom dimensions for a property.

    This provides more detailed information than the metadata-based tool.

    Args:
        property_id: The Google Analytics property ID. Accepted formats are:
          - A number
          - A string consisting of 'properties/' followed by a number
    """
    request = admin_v1beta.ListCustomDimensionsRequest(
        parent=construct_property_rn(property_id)
    )
    # Uses an async list comprehension so the pager returned by
    # list_custom_dimensions retrieves all pages.
    dimensions_pager = await create_admin_api_client().list_custom_dimensions(
        request=request
    )
    all_pages = [proto_to_dict(dimension_page) async for dimension_page in dimensions_pager]
    return all_pages


@mcp.tool(title="Get details of a specific custom dimension")
async def get_custom_dimension(
    property_id: int | str, dimension_name: str
) -> Dict[str, Any]:
    """Returns detailed information about a specific custom dimension.

    Args:
        property_id: The Google Analytics property ID. Accepted formats are:
          - A number
          - A string consisting of 'properties/' followed by a number
        dimension_name: The custom dimension name (e.g., 'custom_dimension_1')
    """
    client = create_admin_api_client()
    request = admin_v1beta.GetCustomDimensionRequest(
        name=f"{construct_property_rn(property_id)}/customDimensions/{dimension_name}"
    )
    response = await client.get_custom_dimension(request=request)
    return proto_to_dict(response)


@mcp.tool(title="List all custom metrics for a property")
async def list_custom_metrics(property_id: int | str) -> List[Dict[str, Any]]:
    """Returns a detailed list of all custom metrics for a property.

    This provides more detailed information than the metadata-based tool.

    Args:
        property_id: The Google Analytics property ID. Accepted formats are:
          - A number
          - A string consisting of 'properties/' followed by a number
    """
    request = admin_v1beta.ListCustomMetricsRequest(
        parent=construct_property_rn(property_id)
    )
    # Uses an async list comprehension so the pager returned by
    # list_custom_metrics retrieves all pages.
    metrics_pager = await create_admin_api_client().list_custom_metrics(
        request=request
    )
    all_pages = [proto_to_dict(metric_page) async for metric_page in metrics_pager]
    return all_pages


@mcp.tool(title="Get details of a specific custom metric")
async def get_custom_metric(
    property_id: int | str, metric_name: str
) -> Dict[str, Any]:
    """Returns detailed information about a specific custom metric.

    Args:
        property_id: The Google Analytics property ID. Accepted formats are:
          - A number
          - A string consisting of 'properties/' followed by a number
        metric_name: The custom metric name (e.g., 'custom_metric_1')
    """
    client = create_admin_api_client()
    request = admin_v1beta.GetCustomMetricRequest(
        name=f"{construct_property_rn(property_id)}/customMetrics/{metric_name}"
    )
    response = await client.get_custom_metric(request=request)
    return proto_to_dict(response)
