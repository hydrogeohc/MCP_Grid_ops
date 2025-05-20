
"""
mcp_best_practices.py - Best Practices and Configuration Options for MCP

This module provides best practices, configuration options, and utility functions
for implementing MCP in grid operationsa applications.
"""
import os
import json
import logging
from typing import Dict, Any, List, Optional, Union
from dataclasses import dataclass
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("mcp-grid")

# Configuration options
@dataclass
class MCPConfig:
    """Configuration options for MCP implementation (Grid Operations)"""

    # Server configuration
    server_name: str = "Grid Operations Assistant"
    server_version: str = "1.0.0"
    server_description: str = "MCP Server for power grid operation and analytics"
    server_port: int = 8000  # For HTTP/SSE transport

    # Client configuration
    default_model: str = "openai:gpt-4o"
    timeout_seconds: int = 60
    max_retries: int = 3
    retry_delay_seconds: int = 2

    # Host configuration
    system_prompt_template: str = """
    You are a Grid Operations Assistant, an AI specialized in power grid management, 
    outage response, maintenance scheduling, and operational analytics. 
    You have access to grid topology, sensor data, maintenance logs, and operational tools 
    through the Model Context Protocol.

    When answering questions:
    1. Use available tools to access up-to-date grid data and operational records.
    2. Provide evidence-based responses with references to grid events or logs where possible.
    3. Acknowledge operational uncertainty when appropriate.
    4. Consider multiple perspectives on grid reliability and restoration strategies.
    5. Explain complex grid concepts clearly for operators and engineers.

    Your goal is to help grid operators and engineers maintain reliability, optimize performance, 
    and restore power efficiently through rigorous operational analysis.
    """
    temperature: float = 0.3  # Lower temperature for operational tasks
    max_tokens: int = 2000

    # Security configuration
    enable_authentication: bool = False
    api_key_header: str = "X-API-Key"
    allowed_origins: List[str] = None  # For CORS in HTTP/SSE transport

    # Performance configuration
    enable_caching: bool = True
    cache_ttl_seconds: int = 3600  # 1 hour
    max_concurrent_requests: int = 10

    def __post_init__(self):
        """Initialize default values for None fields"""
        if self.allowed_origins is None:
            self.allowed_origins = ["http://localhost:3000", "https://example.com"]

# Best practices for grid operations
class MCPBestPractices:
    """Best practices for MCP implementation in grid operations"""

    @staticmethod
    def tool_design_guidelines() -> List[str]:
        """Guidelines for designing effective MCP tools for grid ops"""
        return [
            "Use descriptive, action-oriented tool names (e.g., 'analyze_outage_pattern', not 'outage_tool')",
            "Provide detailed descriptions for each tool to clarify operational use",
            "Design tools to be modular and composable for complex grid workflows",
            "Include input validation in tool implementations to handle edge cases",
            "Return structured data from tools for easier AI processing",
            "Include confidence levels or uncertainty estimates in analytics results",
            "Design tools at the right granularity for operational tasks",
            "Ensure tool parameters are well-described and typed",
            "Consider computational cost and optimize for real-time performance",
            "Include references to grid logs or events in tool results where applicable"
        ]

    @staticmethod
    def prompt_design_guidelines() -> List[str]:
        """Guidelines for designing effective prompts for grid operations"""
        return [
            "Be specific about the operational question or scenario",
            "Provide context about grid topology, status, or recent events",
            "Specify the desired format and level of detail in the response",
            "Encourage critical thinking and evaluation of operational evidence",
            "Ask for multiple restoration or optimization strategies where appropriate",
            "Request uncertainty estimates or confidence levels",
            "Specify the intended audience (e.g., dispatcher, engineer)",
            "Break complex grid scenarios into manageable steps",
            "Include relevant background (e.g., weather, maintenance windows)",
            "Encourage use of specific tools for grid analytics"
        ]

    @staticmethod
    def security_best_practices() -> List[str]:
        """Security best practices for MCP in grid ops"""
        return [
            "Implement authentication and authorization for production deployments",
            "Validate and sanitize all inputs to prevent injection attacks",
            "Implement rate limiting to prevent abuse",
            "Use HTTPS for all communications in production",
            "Limit tool capabilities to only what is necessary",
            "Implement error handling that doesn't leak sensitive info",
            "Regularly update dependencies to address vulnerabilities",
            "Log access and operations for audit purposes",
            "Implement proper secrets management for API keys",
            "Consider privacy and critical infrastructure protection"
        ]

    @staticmethod
    def performance_optimization_tips() -> List[str]:
        """Performance optimization tips for grid ops"""
        return [
            "Cache frequently accessed grid data",
            "Use asynchronous processing for long-running analytics",
            "Batch related operations where possible",
            "Optimize queries for grid event logs and sensor data",
            "Implement pagination for large datasets",
            "Use connection pooling for database/API connections",
            "Scale horizontally for high-load scenarios",
            "Implement timeouts for external API calls",
            "Use efficient data structures for real-time processing",
            "Profile and optimize bottlenecks in the implementation"
        ]

    @staticmethod
    def error_handling_strategies() -> List[str]:
        """Robust error handling strategies for grid ops"""
        return [
            "Implement graceful degradation when components fail",
            "Provide meaningful error messages for diagnosis",
            "Implement retry mechanisms with exponential backoff",
            "Log detailed error info for debugging",
            "Handle edge cases and unexpected inputs",
            "Implement circuit breakers for external dependencies",
            "Provide fallback mechanisms for critical operations",
            "Validate inputs early to catch errors before processing",
            "Use structured error responses with error codes/messages",
            "Implement global error handling for unhandled exceptions"
        ]

# Utility functions for grid ops
class MCPUtils:
    """Utility functions for MCP implementation in grid operations"""

    @staticmethod
    def format_tool_result(result: Any, tool_name: str) -> Dict[str, Any]:
        """
        Format a tool result for consistent presentation.
        """
        if isinstance(result, str):
            try:
                result_dict = json.loads(result)
            except json.JSONDecodeError:
                result_dict = {"raw_result": result}
        else:
            result_dict = result

        return {
            "tool": tool_name,
            "timestamp": datetime.now().isoformat(),
            "result": result_dict
        }

    @staticmethod
    def validate_tool_args(args: Dict[str, Any], schema: Dict[str, Any]) -> List[str]:
        """
        Validate tool arguments against a schema.
        """
        errors = []
        required = schema.get("required", [])
        for prop in required:
            if prop not in args:
                errors.append(f"Missing required property: {prop}")

        properties = schema.get("properties", {})
        for prop, value in args.items():
            if prop in properties:
                prop_schema = properties[prop]
                prop_type = prop_schema.get("type")
                if prop_type == "string" and not isinstance(value, str):
                    errors.append(f"Property {prop} should be a string")
                elif prop_type == "integer" and not isinstance(value, int):
                    errors.append(f"Property {prop} should be an integer")
                elif prop_type == "number" and not isinstance(value, (int, float)):
                    errors.append(f"Property {prop} should be a number")
                elif prop_type == "boolean" and not isinstance(value, bool):
                    errors.append(f"Property {prop} should be a boolean")
                elif prop_type == "array" and not isinstance(value, list):
                    errors.append(f"Property {prop} should be an array")
                elif prop_type == "object" and not isinstance(value, dict):
                    errors.append(f"Property {prop} should be an object")
        return errors

    @staticmethod
    def create_error_response(error_message: str, error_code: str = "ERROR") -> Dict[str, Any]:
        """
        Create a standardized error response.
        """
        return {
            "error": {
                "code": error_code,
                "message": error_message,
                "timestamp": datetime.now().isoformat()
            }
        }

    @staticmethod
    def truncate_conversation_history(history: List[Dict[str, Any]], max_length: int = 10) -> List[Dict[str, Any]]:
        """
        Truncate conversation history to prevent it from growing too large.
        """
        if len(history) <= max_length:
            return history
        return [history[0]] + history[-(max_length-1):]

# Example usage
if __name__ == "__main__":
    config = MCPConfig(
        server_name="Advanced Grid Operations Assistant",
        enable_authentication=True,
        max_concurrent_requests=20
    )

    print("MCP Configuration:")
    for key, value in config.__dict__.items():
        print(f"  {key}: {value}")

    print("\nTool Design Guidelines:")
    for i, guideline in enumerate(MCPBestPractices.tool_design_guidelines(), 1):
        print(f"  {i}. {guideline}")

    print("\nTesting Utility Functions:")
    result = {"load_increase": "150MW", "confidence": "high"}
    formatted = MCPUtils.format_tool_result(result, "analyze_load_pattern")
    print(f"Formatted Tool Result: {json.dumps(formatted, indent=2)}")

    args = {"substation_id": "S123", "start_time": "2024-01-01T00:00:00Z", "end_time": "2024-01-02T00:00:00Z"}
    schema = {
        "type": "object",
        "properties": {
            "substation_id": {"type": "string"},
            "start_time": {"type": "string"},
            "end_time": {"type": "string"}
        },
        "required": ["substation_id", "start_time", "end_time"]
    }
    errors = MCPUtils.validate_tool_args(args, schema)
    print(f"Validation Errors: {errors}")
