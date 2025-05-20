# Grid Operations MCP Suite

This project implements a Model Context Protocol (MCP) suite for power grid operations research, enabling Large Language Models (LLMs) to interact with real-time grid data, analytics tools, and visualization resources.

## Features

- **MCP Server**: Provides grid operations tools for load analysis, outage prediction, and visualization.
- **MCP Client**: Connects to the server, manages queries, and handles tool execution.
- **Host Integration**: Formats prompts and tool descriptions for LLMs.
- **Model Flexibility**: Supports multiple LLM providers via AI Suite integration.
- **Best Practices**: Includes guidelines for security, performance, and error handling.

## Getting Started

### Prerequisites

- Python 3.8 or higher
- Required packages:
  - `mcp`
  - `aisuite`
  - `pandas`
  - `matplotlib`
  - `numpy`
  - `aioconsole`
  - `python-dotenv`
- Set up environment variables (e.g., API keys) in a `.env` file.

### Running the Server

```bash
python grid_ops_server.py
```

### Running the Client

```bash
python grid_ops_client.py grid_ops_server.py [initial_model]
```

- Replace `[initial_model]` with your chosen LLM model (e.g., `openai:gpt-4o`).

### Usage

- Enter operational queries at the prompt.
- Switch LLM models dynamically using `model:provider:model_name`.
- Type `context` to view the current operational context.
- Type `quit` to exit the client.

### Example Query

```text
Analyze load patterns in the Northeast region for the last 48 hours.
```

### Best Practices

- Use descriptive tool names and detailed JSON schemas for clarity.
- Validate all tool inputs and handle errors gracefully.
- Enable authentication and HTTPS for production environments.
- Monitor performance and optimize tool implementations as needed.

### Troubleshooting

- Refer to `mcp_troubleshooting.md` for solutions to common issues.

## Project Structure

- `insecure_demos/mcp/`
  - `attack-mcp-client.py`: Demonstrates a vulnerable MCP client implementation (for demo purposes only).
  - `vuln-mcp.py`: Contains vulnerable MCP code examples (for demo purposes only).
- `ai_suite_integration.py`: Manages integration with LLM providers.
- `grid_ops_client.py`: Client for interacting with the MCP server.
- `grid_ops_host.py`: Handles LLM host integration.
- `grid_ops_research_example.py`: Example script for grid operations research.
- `grid_ops_server.py`: Implements the MCP server with grid tools and resources.
- `mcp_best_practices.py`: Contains best practices and configuration details.
- `mcp_theory.py`: Theoretical background and concepts for MCP.
- `mcp_troubleshooting.md`: Troubleshooting guide for common issues.
- `README.md`: Project documentation (this file).

## License

This project is licensed under the MIT License.

## Acknowledgments

- Inspired by Andrew Ng's AI Suite and the Model Context Protocol (MCP) community.
