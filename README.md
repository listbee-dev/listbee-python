# listbee (deprecated)

**This Python SDK is deprecated.** ListBee has pivoted to an agent-native architecture. The primary integration surface is now MCP + OpenAPI.

## What to use instead

### For agent integrations (recommended)
- **MCP HTTP:** `https://mcp.listbee.so` — use with ChatGPT Apps, Claude Connectors, or any MCP HTTP client
- **MCP stdio:** `npx listbee-mcp` — use with Claude Desktop, Cursor, Cline

### For direct HTTP
- **OpenAPI spec:** `https://listbee.so/openapi.json`
- **Docs:** `https://docs.listbee.so`
- Use `requests`, `httpx`, or any HTTP client against `https://api.listbee.so`

## Final version

This package is pinned to a final deprecation release. Installing or importing it will emit a `DeprecationWarning`.

```python
import listbee  # DeprecationWarning: ListBee Python SDK is deprecated — use MCP at mcp.listbee.so
```

## Why this change

ListBee is commerce infrastructure for AI agents. Agents consume MCP, not Python packages. Every engineering minute we'd have spent on this SDK is a minute not spent on making the agent experience better. See https://listbee.so for the positioning story.

## Reversibility

If you depend on a Python SDK and can share your use case, open an issue at the ListBee product site or email damian@listbee.so. A fresh SDK can be auto-generated via Fern OSS CLI in minutes if demand warrants.
