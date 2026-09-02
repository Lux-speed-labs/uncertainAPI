"""Built-in source adapters.

Adapters implement the public SourceAdapter protocol. Provider-specific and
third-party adapters should remain optional and independently replaceable.
"""

from uncertainAPI.adapters.dlt import (
    DltDataShapeError,
    DltResourceDiscoverer,
    DltSourceAdapter,
    DltSourceConfigurationError,
    DltSourceRegistry,
    ImportPathDltSourceRegistry,
    StaticDltSourceRegistry,
)
from uncertainAPI.adapters.graphql import GraphQLAdapter, GraphQLResponseError
from uncertainAPI.adapters.http_json import HTTPJSONAdapter

__all__ = [
    "DltDataShapeError",
    "DltResourceDiscoverer",
    "DltSourceAdapter",
    "DltSourceConfigurationError",
    "DltSourceRegistry",
    "GraphQLAdapter",
    "GraphQLResponseError",
    "HTTPJSONAdapter",
    "ImportPathDltSourceRegistry",
    "StaticDltSourceRegistry",
]
