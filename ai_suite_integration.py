#Andrew Ng's AI Suite provides a unified interface for interacting with various LLM providers.
#Let's create a dedicated file to demonstrate the integration with AI Suite for model flexibility,
#named ai_suite_integration.py:
"""
ai_suite_integration.py - AI Suite Integration for MCP

This module demonstrates how to integrate Andrew Ng's AI Suite with MCP
for model flexibility in grid operations applications.
"""
import os
import json
from typing import Dict, Any, List, Optional
from dotenv import load_dotenv
import aisuite as ai

# Load environment variables
load_dotenv()

class AISuiteManager:
    """
    Manager for AI Suite integration with MCP (Grid Operations).

    This class:
    1. Provides a unified interface for different LLM providers
    2. Handles model switching for grid operations
    3. Manages API keys and configuration
    4. Optimizes prompts for grid management tasks
    """

    def __init__(self):
        """Initialize the AI Suite Manager"""
        self.client = ai.Client()
        self.available_models = self._get_available_models()

    def _get_available_models(self) -> Dict[str, List[str]]:
        """Get available models for grid operations analysis"""
        return {
            "openai": ["gpt-4o", "gpt-4-turbo", "gpt-4", "gpt-3.5-turbo"],
            "anthropic": [
                "claude-3-5-sonnet-20241022", 
                "claude-3-opus-20240229",
                "claude-3-sonnet-20240229"
            ],
            "google": ["gemini-1.5-pro", "gemini-1.5-flash"],
            "mistral": ["mistral-large-latest", "mistral-medium-latest"]
        }

    def list_available_models(self) -> Dict[str, List[str]]:
        """List models suitable for grid operations"""
        return self.available_models

    def validate_model(self, model: str) -> bool:
        """Validate grid operations model availability"""
        if ":" not in model:
            return False
        provider, model_name = model.split(":", 1)
        return provider in self.available_models and model_name in self.available_models[provider]

    def optimize_system_prompt(self, prompt: str, model: str) -> str:
        """Optimize prompts for grid operations tasks"""
        if ":" not in model:
            return prompt

        provider, _ = model.split(":", 1)
        
        if provider == "anthropic":
            return prompt + "\n\nInclude detailed technical analysis of grid load patterns and equipment status."
        elif provider == "google":
            return prompt + "\n\nStructure response with clear sections for load analysis, risk assessment, and recommendations."
        elif provider == "mistral":
            return "\n".join([line.strip() for line in prompt.split("\n") if line.strip()])
        
        return prompt + "\n\nProvide concise, actionable insights for grid operators."

    def optimize_tool_format(self, tools: List[Dict[str, Any]], model: str) -> List[Dict[str, Any]]:
        """Format tools for grid operations workflows"""
        if ":" not in model:
            return tools

        provider, _ = model.split(":", 1)

        # Format for grid operation tools
        if provider == "anthropic":
            return [{
                "name": t["name"],
                "description": t["description"],
                "input_schema": t["inputSchema"]
            } for t in tools]
        elif provider == "google":
            return [{
                "function_declarations": [{
                    "name": t["name"],
                    "description": t["description"],
                    "parameters": t["inputSchema"]
                }]
            } for t in tools]
        
        return [{
            "type": "function",
            "function": {
                "name": t["name"],
                "description": t["description"],
                "parameters": t["inputSchema"]
            }
        } for t in tools]

    def create_chat_completion(self, model: str, messages: List[Dict[str, Any]],
                              tools: Optional[List[Dict[str, Any]]] = None,
                              temperature: float = 0.3) -> Any:
        """Create chat completion for grid operations analysis"""
        if not self.validate_model(model):
            raise ValueError(f"Invalid grid operations model: {model}")

        # Optimize system prompts
        for i, msg in enumerate(messages):
            if msg["role"] == "system":
                messages[i]["content"] = self.optimize_system_prompt(msg["content"], model)

        formatted_tools = self.optimize_tool_format(tools, model) if tools else None

        return self.client.chat.completions.create(
            model=model,
            messages=messages,
            tools=formatted_tools,
            temperature=temperature,
            max_tokens=2000
        )

# Grid operations example usage
def test_grid_operations_manager():
    """Test AI Suite Manager with grid operations scenario"""
    manager = AISuiteManager()

    print("Available Grid Operations Models:")
    for provider, models in manager.list_available_models().items():
        print(f"  {provider.upper()}: {', '.join(models)}")

    system_prompt = """
    You are a Grid Operations Assistant, an AI specialized in power grid management,
    outage prediction, load balancing, and equipment maintenance analysis.
    """
    
    print("\nOptimized Prompt for Claude:")
    print(manager.optimize_system_prompt(
        system_prompt, 
        "anthropic:claude-3-opus-20240229"
    ))

    grid_tools = [{
        "name": "analyze_load_pattern",
        "description": "Analyze electrical load patterns in specific grid regions",
        "inputSchema": {
            "type": "object",
            "properties": {
                "region": {"type": "string"},
                "time_window": {"type": "string"},
                "voltage_level": {"type": "number"}
            },
            "required": ["region", "time_window"]
        }
    }]

    print("\nOptimized Tools for Gemini:")
    print(json.dumps(
        manager.optimize_tool_format(grid_tools, "google:gemini-1.5-pro"),
        indent=2
    ))

if __name__ == "__main__":
    test_grid_operations_manager()
