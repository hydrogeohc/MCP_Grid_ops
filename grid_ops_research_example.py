
"""
grid_ops_research_example.py - Complete Example of MCP for Grid Operations Research

This script demonstrates a complete workflow for using MCP in grid operations research,
including server setup, client connection, and research queries.
"""
import os
import sys
import json
import asyncio
from typing import Dict, Any, List, Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

async def run_grid_operations_example():
    """Run a complete grid operations example using MCP"""
    print("=== Model Context Protocol (MCP) Grid Operations Example ===\n")
    
    # Step 1: Start the MCP server with unbuffered output
    print("Starting the MCP Grid Operations Server...")
    server_process = await asyncio.create_subprocess_exec(
        "python", "-u", "grid_ops_server.py",  # Added -u for unbuffered output
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE
    )

    # Wait for server to initialize with error handling
    try:
        startup_line = await asyncio.wait_for(server_process.stdout.readline(), timeout=15)
        if not startup_line:
            raise asyncio.TimeoutError()
        print(f"Server startup detected: {startup_line.decode().strip()}")
    except asyncio.TimeoutError:
        print("Server failed to start within 15 seconds")
        # Check for server errors
        if server_process.stderr:
            stderr_output = await server_process.stderr.read()
            print(f"Server error output:\n{stderr_output.decode()}")
        return

    # Step 2: Initialize the client
    print("\nInitializing the Grid Operations Client...")
    from grid_ops_client import GridOperationsClient

    try:
        # Step 3: Connect to the server with proper parameters
        client = GridOperationsClient(model="openai:gpt-4o")
        print("Connecting to the Grid Operations Server...")
        await client.connect_to_server("grid_ops_server.py")      # Added explicit port
            
        

        # [Rest of original code remains unchanged...]
        # Step 4-6: Example queries, model switching, context display

    finally:
        # Step 7: Clean up resources
        print("\nCleaning up resources...")
        await client.cleanup()
        
        # Terminate server process
        if server_process.returncode is None:
            server_process.terminate()
            try:
                await asyncio.wait_for(server_process.wait(), timeout=5)
            except asyncio.TimeoutError:
                server_process.kill()
                await server_process.wait()

        print("\nGrid operations example completed successfully!")

if __name__ == "__main__":
    try:
        asyncio.run(run_grid_operations_example())
    except KeyboardInterrupt:
        print("\nOperation cancelled by user")
    except Exception as e:
        print(f"Fatal error: {str(e)}")