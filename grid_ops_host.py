
#The MCP Host is responsible for interpreting the protocol and facilitating communication
#between the LLM and external resources. Let's create a file named grid_ops_host.py:
"""
grid_ops_host.py - MCP Host for Grid Operations Research

This host manages the environment where the LLM runs and facilitates
communication between the LLM and external resources.
"""
import os
import json
import asyncio
from typing import Dict, Any, List, Optional
from dotenv import load_dotenv
import aisuite as ai

# Load environment variables
load_dotenv()

class MCPHost:
    """
    MCP Host for managing LLM interactions with the MCP server (Grid Operations Use Case).

    The host is responsible for:
    1. Initializing the LLM environment
    2. Formatting tool descriptions for the LLM
    3. Processing LLM responses and extracting tool calls
    4. Providing tool results back to the LLM
    """

    def __init__(self, model: str = "openai:gpt-4o"):
        """
        Initialize the MCP Host.

        Args:
            model: The LLM model to use (provider:model format)
        """
        self.ai_client = ai.Client()
        self.model = model
        self.conversation_history = []
        self.system_message = """
        You are a Grid Operations Assistant, an AI specialized in power grid management,
        outage response, maintenance scheduling, and operational analytics. You have access
        to grid topology, sensor data, maintenance logs, and operational tools through the
        Model Context Protocol.

        When answering questions:
        1. Use available tools to access up-to-date grid data and operational records.
        2. Provide evidence-based responses with references to grid events or logs where possible.
        3. Acknowledge operational uncertainty when appropriate.
        4. Consider multiple perspectives on grid reliability and restoration strategies.
        5. Explain complex grid concepts clearly for operators and engineers.

        Your goal is to help grid operators and engineers maintain reliability, optimize performance,
        and restore power efficiently through rigorous operational analysis.
        """

    def format_tools_for_llm(self, tools: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Format tools in a structure suitable for the LLM.

        Args:
            tools: List of tools from the MCP server

        Returns:
            Formatted tools for the LLM
        """
        formatted_tools = []
        for tool in tools:
            formatted_tool = {
                "type": "function",
                "function": {
                    "name": tool["name"],
                    "description": tool["description"],
                    "parameters": tool["inputSchema"]
                }
            }
            formatted_tools.append(formatted_tool)
        return formatted_tools

    def create_messages(self, query: str, context: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Create messages for the LLM, including conversation history.

        Args:
            query: The user's query
            context: Optional additional context to include

        Returns:
            List of messages for the LLM
        """
        messages = [
            {"role": "system", "content": self.system_message}
        ]
        messages.extend(self.conversation_history)
        if context:
            messages.append({"role": "system", "content": f"Additional context: {context}"})
        messages.append({"role": "user", "content": query})
        return messages

    async def process_query(self, query: str, tools: List[Dict[str, Any]],
                           context: Optional[str] = None) -> Dict[str, Any]:
        """
        Process a user query using the LLM and available tools.

        Args:
            query: The user's query
            tools: List of available tools from the MCP server
            context: Optional additional context

        Returns:
            Processing results including LLM response and tool calls
        """
        formatted_tools = self.format_tools_for_llm(tools)
        messages = self.create_messages(query, context)

        response = self.ai_client.chat.completions.create(
            model=self.model,
            messages=messages,
            tools=formatted_tools,
            temperature=0.3,  # Lower temperature for operational tasks
            max_tokens=2000
        )
        llm_response = response.choices[0].message

        # Update conversation history
        self.conversation_history.append({"role": "user", "content": query})
        self.conversation_history.append({
            "role": "assistant",
            "content": llm_response.content,
            "tool_calls": getattr(llm_response, "tool_calls", None)
        })

        # Check if the LLM wants to use tools
        if not hasattr(llm_response, "tool_calls") or not llm_response.tool_calls:
            return {
                "response": llm_response.content,
                "tool_calls": [],
                "final_answer": llm_response.content
            }

        # Extract tool calls
        tool_calls = []
        for tool_call in llm_response.tool_calls:
            tool_name = tool_call.function.name
            tool_args_str = tool_call.function.arguments
            try:
                tool_args = json.loads(tool_args_str)
            except json.JSONDecodeError:
                tool_args = {"raw_input": tool_args_str}
            tool_calls.append({
                "id": tool_call.id,
                "name": tool_name,
                "arguments": tool_args
            })

        return {
            "response": llm_response.content,
            "tool_calls": tool_calls,
            "messages": messages,
            "llm_response": llm_response
        }

    async def process_tool_results(self, messages: List[Dict[str, Any]],
                                  llm_response: Any,
                                  tool_results: List[Dict[str, Any]]) -> str:
        """
        Process tool results and get a final answer from the LLM.

        Args:
            messages: The conversation messages
            llm_response: The LLM's response containing tool calls
            tool_results: Results from executing the tools

        Returns:
            The LLM's final answer after processing tool results
        """
        updated_messages = messages.copy()
        updated_messages.append({
            "role": "assistant",
            "content": llm_response.content,
            "tool_calls": getattr(llm_response, "tool_calls", None)
        })
        for result in tool_results:
            updated_messages.append({
                "role": "tool",
                "tool_call_id": result["id"],
                "content": json.dumps(result["result"])
            })
        final_response = self.ai_client.chat.completions.create(
            model=self.model,
            messages=updated_messages,
            temperature=0.3,
            max_tokens=2000
        )
        final_answer = final_response.choices[0].message.content
        self.conversation_history.append({
            "role": "assistant",
            "content": final_answer
        })
        return final_answer

    def change_model(self, new_model: str) -> None:
        """
        Change the LLM model.

        Args:
            new_model: The new model to use (provider:model format)
        """
        self.model = new_model
        print(f"Model changed to: {new_model}")

# Example usage for grid operations
async def test_host():
    host = MCPHost()

    # Mock tools from MCP server for grid ops
    mock_tools = [
        {
            "name": "analyze_load_pattern",
            "description": "Analyze load patterns for a specific grid region and time window",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "region": {
                        "type": "string",
                        "description": "The grid region to analyze"
                    },
                    "window_hours": {
                        "type": "integer",
                        "description": "The time window in hours"
                    }
                },
                "required": ["region", "window_hours"]
            }
        }
    ]

    # Process a query
    result = await host.process_query(
        "What load patterns have emerged in the Northeast grid region over the last 48 hours?",
        mock_tools
    )

    print("LLM Response:", result["response"])
    print("Tool Calls:", json.dumps(result["tool_calls"], indent=2))

    # Mock tool results
    mock_tool_results = [
        {
            "id": result["tool_calls"][0]["id"],
            "result": {
                "region": "Northeast",
                "window_hours": 48,
                "max_load": "65,000 MW",
                "min_load": "40,000 MW",
                "trend": "increasing evening peaks",
                "recommendation": "Monitor for potential overloads during peak hours."
            }
        }
    ]

    # Process tool results
    final_answer = await host.process_tool_results(
        result["messages"],
        result["llm_response"],
        mock_tool_results
    )

    print("Final Answer:", final_answer)

if __name__ == "__main__":
    asyncio.run(test_host())
