import asyncio
import json
from typing import List, Dict, Any, Optional

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

class StreamlitMCPClient:
    """
    A synchronous wrapper around the asynchronous MCP client,
    designed to work within Streamlit's execution model.
    """
    def __init__(self, command: str, args: List[str]):
        self.command = command
        self.args = args
        self.server_params = StdioServerParameters(
            command=self.command,
            args=self.args,
            env=None
        )
        self._tools = []

    def get_tools(self) -> List[Dict[str, Any]]:
        """Connects to the server, fetches tools, and disconnects."""
        return asyncio.run(self._get_tools_async())

    async def _get_tools_async(self) -> List[Dict[str, Any]]:
        async with stdio_client(self.server_params) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                response = await session.list_tools()
                
                # Convert MCP tools to Groq/OpenAI compatible format
                formatted_tools = []
                for tool in response.tools:
                    formatted_tools.append({
                        "type": "function",
                        "function": {
                            "name": tool.name,
                            "description": tool.description,
                            "parameters": tool.inputSchema
                        }
                    })
                return formatted_tools

    def call_tool(self, name: str, arguments: dict) -> str:
        """Connects to the server, executes a specific tool, and disconnects."""
        return asyncio.run(self._call_tool_async(name, arguments))

    async def _call_tool_async(self, name: str, arguments: dict) -> str:
        async with stdio_client(self.server_params) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                result = await session.call_tool(name, arguments=arguments)
                
                # Parse the result
                if result.isError:
                    return f"Error: {result.content}"
                
                # Usually content is a list of TextContent objects
                if result.content:
                    return result.content[0].text
                return "Success but no content returned."
