#!/usr/bin/env python3
"""Test script for enhanced MCP server"""

import json
import subprocess
import sys

def test_mcp_tool(tool_name, params):
    """Test an MCP tool call"""
    request = {
        "jsonrpc": "2.0",
        "id": 3,
        "method": "tools/call",
        "params": {
            "name": tool_name,
            "arguments": params
        }
    }
    
    process = subprocess.Popen(
        ["python3", "/home/eze/.claude-mcp-servers/gemini-collab-enhanced/server.py"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    
    # Send initialization first
    init_request = {"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {}}
    process.stdin.write(json.dumps(init_request) + "\n")
    process.stdin.flush()
    
    # Read initialization response
    init_response = process.stdout.readline()
    print(f"Init response: {init_response.strip()}")
    
    # Send the actual tool call
    process.stdin.write(json.dumps(request) + "\n")
    process.stdin.flush()
    process.stdin.close()
    
    # Read response
    response = process.stdout.readline()
    process.wait()
    
    return json.loads(response)

if __name__ == "__main__":
    print("🧪 Testing Enhanced MCP Server...")
    
    # Test loading current project
    print("\n📁 Testing load_codebase...")
    result = test_mcp_tool("load_codebase", {
        "project_path": "/home/eze/projects/claude_code-gemini-mcp",
        "max_tokens": 50000  # Small limit for testing
    })
    
    if "result" in result:
        print("✅ load_codebase successful!")
        content = result["result"]["content"][0]["text"]
        print(f"📄 Response preview: {content[:200]}...")
    else:
        print(f"❌ load_codebase failed: {result.get('error', 'Unknown error')}")