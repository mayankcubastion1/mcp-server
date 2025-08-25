"""Top-level package for mcp_server.

Re-exports the most commonly used helpers for convenience so users can
simply ``import mcp_server`` and access the public API.
"""

import mcp_server.api as api

build_mcp_server = api.build_mcp_server
all_tool_specs = api.all_tool_specs
create_tool_specs = api.create_tool_specs
create_langchain_tools = api.create_langchain_tools
set_request_headers = api.set_request_headers
auth_header_getter = api.auth_header_getter
