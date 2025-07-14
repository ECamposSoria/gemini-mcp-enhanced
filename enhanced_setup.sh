#!/bin/bash

# Enhanced Claude-Gemini MCP Server Setup
# Installs the intelligent codebase analysis version

set -e

API_KEY="$1"
INSTALL_DIR="$HOME/.claude-mcp-servers/gemini-collab-enhanced"

echo "🚀 Setting up Enhanced Claude-Gemini MCP Server..."

# Check if API key is provided
if [ -z "$API_KEY" ]; then
    echo "❌ Error: Please provide your Gemini API key"
    echo "Usage: ./enhanced_setup.sh YOUR_GEMINI_API_KEY"
    echo "Get a free API key at: https://aistudio.google.com/apikey"
    exit 1
fi

# Create installation directory
echo "📁 Creating installation directory..."
mkdir -p "$INSTALL_DIR"

# Copy enhanced server
echo "📋 Installing enhanced server..."
cp enhanced_server.py "$INSTALL_DIR/server.py"
cp requirements.txt "$INSTALL_DIR/"

# Set API key in server file
echo "🔑 Configuring API key..."
sed -i.bak "s/YOUR_API_KEY_HERE/$API_KEY/g" "$INSTALL_DIR/server.py"

# Install Python dependencies
echo "📦 Installing Python dependencies..."
if command -v python3 &> /dev/null; then
    PYTHON_CMD="python3"
elif command -v python &> /dev/null; then
    PYTHON_CMD="python"
else
    echo "❌ Error: Python not found. Please install Python 3.8+"
    exit 1
fi

# Install dependencies
$PYTHON_CMD -m pip install -r "$INSTALL_DIR/requirements.txt" --user

# Remove existing MCP server if it exists
echo "🔄 Configuring MCP server..."
if command -v claude &> /dev/null; then
    claude mcp remove gemini-collab-enhanced 2>/dev/null || true
    claude mcp add --scope user gemini-collab-enhanced python3 "$INSTALL_DIR/server.py"
    echo "✅ Enhanced MCP server registered with Claude Code!"
else
    echo "⚠️  Claude Code CLI not found. Please install it first."
    echo "   The server is installed at: $INSTALL_DIR"
    echo "   You can manually configure it later."
fi

# Create usage example
cat > "$INSTALL_DIR/USAGE.md" << 'EOF'
# Enhanced Claude-Gemini MCP Server Usage

## Load and Analyze Codebase

```bash
claude

# Load your project
load_codebase
  project_path: "/path/to/your/project"

# Get architecture analysis
analyze_architecture
  focus: "architecture"

# Semantic search
semantic_search
  query: "find authentication logic"

# Get improvement suggestions  
suggest_improvements
  area: "security"

# Trace functionality
explain_codeflow
  functionality: "user login process"

# Ask anything about your code
ask_with_context
  question: "How does the API handle errors?"
```

## Available Tools

- **load_codebase** - Load entire codebase with intelligent prioritization
- **analyze_architecture** - Comprehensive architecture analysis
- **semantic_search** - Natural language code search
- **suggest_improvements** - Targeted improvement suggestions
- **explain_codeflow** - Trace functionality across files
- **codebase_summary** - Complete project overview
- **ask_with_context** - Ask anything with full context

## Features

✅ Leverages Gemini's 1M token context window
✅ Intelligent file prioritization by relevance
✅ Supports 20+ programming languages
✅ Semantic search beyond simple grep
✅ Architecture analysis and patterns detection
✅ Actionable improvement suggestions
✅ Cross-file functionality tracing
EOF

echo ""
echo "🎉 Enhanced Claude-Gemini MCP Server installed successfully!"
echo ""
echo "📍 Installation location: $INSTALL_DIR"
echo "📖 Usage guide: $INSTALL_DIR/USAGE.md"
echo ""
echo "🚀 Ready to use! Start Claude Code and try:"
echo "   load_codebase"
echo "     project_path: \"/path/to/your/project\""
echo ""
echo "💡 This enhanced version provides:"
echo "   • Intelligent codebase loading (up to 1M tokens)"
echo "   • Architecture analysis and pattern detection"
echo "   • Semantic search with natural language"
echo "   • Targeted improvement suggestions"
echo "   • Cross-file functionality tracing"
echo ""