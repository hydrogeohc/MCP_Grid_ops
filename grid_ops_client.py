#
#The MCP Client connects to the server and facilitates communication between the user, the
#sLLM, and the MCP server. Let's create a file named grid_ops_client.py:
"""
grids_ops_client.py - MCP Client for Grid Operations Research

This client connects to the MCP server, manages the conversation flow,
and handles tool calls for grid operations applications.
"""
import os
import sys
import json
import asyncio
import logging
from datetime import datetime
from typing import Dict, Any, List, Optional
from contextlib import AsyncExitStack
import aioconsole  # For async input

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from dotenv import load_dotenv

# Import our MCP Host
from grid_ops_host import MCPHost

# Configure logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Load environment variables
load_dotenv()

class GridOperationsClient:
    """
    MCP Client for grid operations applications.

    This client:
    1. Connects to the MCP server
    2. Manages the conversation flow
    3. Handles tool calls and results
    4. Maintains operational context
    """

    def __init__(self, model: str = "openai:gpt-4o"):
        """
        Initialize the Grid Operations Client.

        Args:
            model: The LLM model to use (provider:model format)
        """
        self.session: Optional[ClientSession] = None
        self.exit_stack = AsyncExitStack()
        self.host = MCPHost(model=model)

        # Initialize operational context
        self.operational_context = {
            "datasets": [],
            "equipment": [],
            "regions": [],
            "analyses": []
        }

    async def connect_to_server(self, server_script_path: str):
        """
        Connect to an MCP server.

        Args:
            server_script_path: Path to the server script
        """
        is_python = server_script_path.endswith('.py')
        is_js = server_script_path.endswith('.js')
        if not (is_python or is_js):
            raise ValueError("Server script must be a .py or .js file")

        command = "python" if is_python else "node"
        server_params = StdioServerParameters(
            command=command,
            args=[server_script_path],
            env=None
        )

        stdio_transport = await self.exit_stack.enter_async_context(stdio_client(server_params))
        self.stdio, self.write = stdio_transport
        self.session = await self.exit_stack.enter_async_context(ClientSession(self.stdio, self.write))

        await self.session.initialize()

        # List available tools
        response = await self.session.list_tools()
        self.tools = response.tools

        logger.info(f"Connected to grid operations server with {len(self.tools)} tools")
        print(f"\nConnected to grid operations server with {len(self.tools)} tools")
        print(f"Using model: {self.host.model}")

    async def process_operational_query(self, query: str) -> str:
        """
        Process a grid operations query.

        Args:
            query: The user's operational query

        Returns:
            The response to the query
        """
        # Format tools for the host
        formatted_tools = []
        for tool in self.tools:
            formatted_tool = {
                "name": tool.name,
                "description": tool.description,
                "inputSchema": tool.inputSchema
            }
            formatted_tools.append(formatted_tool)

        # Create context string from operational context
        context_str = f"Current operational context: {json.dumps(self.operational_context, indent=2)}"

        # Process the query using the host
        result = await self.host.process_query(query, formatted_tools, context_str)

        # If no tool calls, return the response
        if not result["tool_calls"]:
            return result["response"]

        # Execute tool calls
        tool_results = []
        for tool_call in result["tool_calls"]:
            tool_name = tool_call["name"]
            tool_args = tool_call["arguments"]

            logger.info(f"Executing tool: {tool_name}")
            print(f"\nExecuting tool: {tool_name}")
            print(f"Arguments: {json.dumps(tool_args, indent=2)}")

            # Call the tool on the server
            try:
                tool_result = await self.session.call_tool(tool_name, tool_args)
            except Exception as e:
                logger.error(f"Tool execution failed: {str(e)}")
                continue

            # Update operational context based on tool and result
            self._update_operational_context(tool_name, tool_args, tool_result.content)

            # Add to results
            tool_results.append({
                "id": tool_call["id"],
                "result": tool_result.content
            })

            logger.info(f"Tool result received for {tool_name}")
            print(f"Tool result received: {type(tool_result.content)}")

        # Process tool results to get final answer
        final_answer = await self.host.process_tool_results(
            result["messages"],
            result["llm_response"],
            tool_results
        )
        return final_answer

    def _update_operational_context(self, tool_name: str, tool_args: Dict[str, Any], result: Any):
        """
        Update the operational context based on tool calls and results.

        Args:
            tool_name: The name of the tool called
            tool_args: The arguments passed to the tool
            result: The result returned by the tool
        """
        # Convert result to dict if it's a string
        result_dict = {}
        if isinstance(result, str):
            try:
                result_dict = json.loads(result)
            except json.JSONDecodeError as e:
                result_dict = {"raw_result": result}
                logger.error(f"Failed to parse tool result: {str(e)}")
        elif isinstance(result, dict):
            result_dict = result

        # Update context based on tool type
        if tool_name == "get_grid_topology":
            if "region" in tool_args:
                region = tool_args["region"]
                if region not in self.operational_context["regions"]:
                    self.operational_context["regions"].append(region)

        elif tool_name == "get_grid_load_data":
            if "dataset_id" in tool_args:
                dataset_id = tool_args["dataset_id"]
                if dataset_id not in self.operational_context["datasets"]:
                    self.operational_context["datasets"].append(dataset_id)

        elif tool_name == "get_equipment_status":
            if "equipment_id" in tool_args:
                equipment_id = tool_args["equipment_id"]
                if equipment_id not in self.operational_context["equipment"]:
                    self.operational_context["equipment"].append(equipment_id)

        elif tool_name in ["analyze_load_pattern", "predict_outage_risk", "generate_grid_visualization"]:
            # Add analysis to context
            self.operational_context["analyses"].append({
                "tool": tool_name,
                "args": tool_args,
                "timestamp": datetime.now().isoformat(),
                "result": result_dict
            })

    async def operational_loop(self):
        """Run an interactive operational loop"""
        print("\nGrid Operations MCP Client Started!")
        print("Type your operational queries, 'model:<provider>:<model>' to change models, or 'quit' to exit.")
        print("Type 'context' to view the current operational context.")
        
        while True:
            try:
                query = await aioconsole.ainput("\nOperational Query: ")
                query = query.strip()

                if query.lower() == 'quit':
                    break

                if query.lower() == 'context':
                    print("\nCurrent Operational Context:")
                    print(json.dumps(self.operational_context, indent=2))
                    continue

                if query.startswith('model:'):
                    new_model = query[6:]
                    self.host.change_model(new_model)
                    print(f"Model changed to: {new_model}")
                    continue

                print("\nProcessing your query...")
                response = await self.process_operational_query(query)
                print("\n" + response)

            except Exception as e:
                logger.error(f"Error processing query: {str(e)}")
                print(f"\nError: {str(e)}")
                import traceback
                traceback.print_exc()

    async def cleanup(self):
        """Clean up resources"""
        await self.exit_stack.aclose()

async def main():
    if len(sys.argv) < 2:
        print("Usage: python grid_client.py <path_to_server_script> [initial_model]")
        sys.exit(1)
    initial_model = sys.argv[2] if len(sys.argv) > 2 else "openai:gpt-4o"
    client = GridOperationsClient(model=initial_model)
    
    try:
        await client.connect_to_server(sys.argv[1])
        await client.operational_loop()
    except Exception as e:
        logger.error(f"Fatal error: {str(e)}")
        print(f"Fatal error: {str(e)}")
        import traceback
        traceback.print_exc()
    finally:
        await client.cleanup()
        print("\nClient shutdown complete.")

if __name__ == "__main__":
    asyncio.run(main())
