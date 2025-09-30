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

"""Tools for managing Google Analytics data streams."""

from typing import Any, Dict, List

from analytics_mcp.coordinator import mcp
from analytics_mcp.tools.utils import (
    construct_property_rn,
    create_admin_api_client,
    proto_to_dict,
)
from google.analytics import admin_v1beta


@mcp.tool(title="List data streams for a property")
async def list_data_streams(property_id: int | str) -> List[Dict[str, Any]]:
    """Returns a list of data streams for a property.

    Data streams can be web, iOS app, Android app, or other types.

    Args:
        property_id: The Google Analytics property ID. Accepted formats are:
          - A number
          - A string consisting of 'properties/' followed by a number
    """
    request = admin_v1beta.ListDataStreamsRequest(
        parent=construct_property_rn(property_id)
    )
    # Uses an async list comprehension so the pager returned by
    # list_data_streams retrieves all pages.
    streams_pager = await create_admin_api_client().list_data_streams(
        request=request
    )
    all_pages = [proto_to_dict(stream_page) async for stream_page in streams_pager]
    return all_pages


@mcp.tool(title="Get details of a specific data stream")
async def get_data_stream(
    property_id: int | str, stream_id: str
) -> Dict[str, Any]:
    """Returns details about a specific data stream.

    Args:
        property_id: The Google Analytics property ID. Accepted formats are:
          - A number
          - A string consisting of 'properties/' followed by a number
        stream_id: The data stream ID (e.g., '1234567890')
    """
    client = create_admin_api_client()
    request = admin_v1beta.GetDataStreamRequest(
        name=f"{construct_property_rn(property_id)}/dataStreams/{stream_id}"
    )
    response = await client.get_data_stream(request=request)
    return proto_to_dict(response)


@mcp.tool(title="List Measurement Protocol secrets for a data stream")
async def list_measurement_protocol_secrets(
    property_id: int | str, stream_id: str
) -> List[Dict[str, Any]]:
    """Returns a list of Measurement Protocol secrets for a data stream.

    Args:
        property_id: The Google Analytics property ID. Accepted formats are:
          - A number
          - A string consisting of 'properties/' followed by a number
        stream_id: The data stream ID (e.g., '1234567890')
    """
    request = admin_v1beta.ListMeasurementProtocolSecretsRequest(
        parent=f"{construct_property_rn(property_id)}/dataStreams/{stream_id}"
    )
    # Uses an async list comprehension so the pager returned by
    # list_measurement_protocol_secrets retrieves all pages.
    secrets_pager = await create_admin_api_client().list_measurement_protocol_secrets(
        request=request
    )
    all_pages = [proto_to_dict(secret_page) async for secret_page in secrets_pager]
    return all_pages


@mcp.tool(title="Get details of a specific Measurement Protocol secret")
async def get_measurement_protocol_secret(
    property_id: int | str, stream_id: str, secret_name: str
) -> Dict[str, Any]:
    """Returns details about a specific Measurement Protocol secret.

    Args:
        property_id: The Google Analytics property ID. Accepted formats are:
          - A number
          - A string consisting of 'properties/' followed by a number
        stream_id: The data stream ID (e.g., '1234567890')
        secret_name: The secret name (e.g., '1234567890')
    """
    client = create_admin_api_client()
    request = admin_v1beta.GetMeasurementProtocolSecretRequest(
        name=f"{construct_property_rn(property_id)}/dataStreams/{stream_id}/measurementProtocolSecrets/{secret_name}"
    )
    response = await client.get_measurement_protocol_secret(request=request)
    return proto_to_dict(response)
