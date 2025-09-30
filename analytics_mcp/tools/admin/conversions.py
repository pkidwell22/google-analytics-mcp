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

"""Tools for managing Google Analytics conversion events."""

from typing import Any, Dict, List

from analytics_mcp.coordinator import mcp
from analytics_mcp.tools.utils import (
    construct_property_rn,
    create_admin_api_client,
    proto_to_dict,
)
from google.analytics import admin_v1beta


@mcp.tool(title="List conversion events for a property")
async def list_conversion_events(property_id: int | str) -> List[Dict[str, Any]]:
    """Returns a list of conversion events for a property.

    Args:
        property_id: The Google Analytics property ID. Accepted formats are:
          - A number
          - A string consisting of 'properties/' followed by a number
    """
    request = admin_v1beta.ListConversionEventsRequest(
        parent=construct_property_rn(property_id)
    )
    # Uses an async list comprehension so the pager returned by
    # list_conversion_events retrieves all pages.
    events_pager = await create_admin_api_client().list_conversion_events(
        request=request
    )
    all_pages = [proto_to_dict(event_page) async for event_page in events_pager]
    return all_pages


@mcp.tool(title="Get details of a specific conversion event")
async def get_conversion_event(
    property_id: int | str, event_name: str
) -> Dict[str, Any]:
    """Returns details about a specific conversion event.

    Args:
        property_id: The Google Analytics property ID. Accepted formats are:
          - A number
          - A string consisting of 'properties/' followed by a number
        event_name: The name of the conversion event (e.g., 'purchase', 'sign_up')
    """
    client = create_admin_api_client()
    request = admin_v1beta.GetConversionEventRequest(
        name=f"{construct_property_rn(property_id)}/conversionEvents/{event_name}"
    )
    response = await client.get_conversion_event(request=request)
    return proto_to_dict(response)


@mcp.tool(title="List key events for a property")
async def list_key_events(property_id: int | str) -> List[Dict[str, Any]]:
    """Returns a list of key events (conversions) for a property.

    Args:
        property_id: The Google Analytics property ID. Accepted formats are:
          - A number
          - A string consisting of 'properties/' followed by a number
    """
    request = admin_v1beta.ListKeyEventsRequest(
        parent=construct_property_rn(property_id)
    )
    # Uses an async list comprehension so the pager returned by
    # list_key_events retrieves all pages.
    events_pager = await create_admin_api_client().list_key_events(
        request=request
    )
    all_pages = [proto_to_dict(event_page) async for event_page in events_pager]
    return all_pages


@mcp.tool(title="Get details of a specific key event")
async def get_key_event(
    property_id: int | str, event_name: str
) -> Dict[str, Any]:
    """Returns details about a specific key event.

    Args:
        property_id: The Google Analytics property ID. Accepted formats are:
          - A number
          - A string consisting of 'properties/' followed by a number
        event_name: The name of the key event (e.g., 'purchase', 'sign_up')
    """
    client = create_admin_api_client()
    request = admin_v1beta.GetKeyEventRequest(
        name=f"{construct_property_rn(property_id)}/keyEvents/{event_name}"
    )
    response = await client.get_key_event(request=request)
    return proto_to_dict(response)
