# Enhanced Gemini MCP Server

🧠 **Intelligent Codebase Analysis with Gemini's 1M Token Context Window**

Transform your development workflow with this enhanced MCP server that leverages Google's Gemini AI for comprehensive codebase analysis. Load entire projects into Gemini's massive context window and get intelligent insights about your code.

## ✨ Key Features

- **🎯 Intelligent Codebase Loading** - Smart file prioritization and relevance scoring
- **🧮 1M Token Context** - Leverage Gemini's full context window for comprehensive analysis
- **🔍 Semantic Search** - Natural language code search across your entire project
- **🏗️ Architecture Analysis** - Get detailed insights into your codebase structure
- **💡 Smart Improvements** - Targeted suggestions for performance, security, and maintainability
- **📊 Code Flow Tracing** - Understand how functionality works across files
- **🎨 Project Summaries** - Comprehensive overviews of any codebase
- **⚡ Session Caching** - 30-minute cache for faster repeated analyses
- **💾 Export Sessions** - Save important findings for future reference

## 🚀 Quick Start

### Prerequisites
- Python 3.8+ installed
- Claude Code CLI installed
- Google Gemini API key ([Get one free](https://aistudio.google.com/apikey))

### Installation

1. **Clone the repository:**
```bash
git clone https://github.com/ECamposSoria/gemini-mcp-enhanced.git
cd gemini-mcp-enhanced
```

2. **Run enhanced setup:**
```bash
./enhanced_setup.sh
```

3. **Enter your Gemini API key when prompted**

That's it! 🎉

## 🛠️ Available Tools

### Core Analysis Tools

#### `load_codebase`
Load an entire project into Gemini's context with intelligent prioritization:
```bash
mcp__gemini-collab-enhanced__load_codebase
  project_path: "/path/to/your/project"
  max_tokens: 900000  # optional, default: 900000
```

#### `analyze_architecture`
Get comprehensive architecture analysis:
```bash
mcp__gemini-collab-enhanced__analyze_architecture
  focus: "architecture"  # or "patterns", "dependencies", "structure"
```

#### `semantic_search`
Search your codebase using natural language:
```bash
mcp__gemini-collab-enhanced__semantic_search
  query: "Find functions that handle user authentication"
```

#### `suggest_improvements`
Get targeted improvement suggestions:
```bash
mcp__gemini-collab-enhanced__suggest_improvements
  area: "security"  # or "performance", "maintainability", "testing"
```

#### `explain_codeflow`
Trace how functionality works across your codebase:
```bash
mcp__gemini-collab-enhanced__explain_codeflow
  functionality: "How user registration works from API to database"
```

#### `codebase_summary`
Get a comprehensive project overview:
```bash
mcp__gemini-collab-enhanced__codebase_summary
```

#### `ask_with_context`
Ask any question about your loaded codebase:
```bash
mcp__gemini-collab-enhanced__ask_with_context
  question: "What security vulnerabilities exist in the authentication system?"
```

### Session Management Tools

#### `export_session`
Export cached analysis results to a markdown file:
```bash
mcp__gemini-collab-enhanced__export_session
  export_path: "/path/to/export"  # optional, defaults to project path
```

#### `session_stats`
Get current session cache statistics:
```bash
mcp__gemini-collab-enhanced__session_stats
```

## ⚡ Session Caching

The enhanced server includes intelligent session caching to improve performance:

- **Automatic Caching**: Analysis results are cached for 30 minutes
- **Smart Invalidation**: Cache clears when switching projects
- **Performance Boost**: Repeated queries return instantly from cache
- **Export Capability**: Save important findings before they expire

### Caching Benefits
1. **Faster Iterations**: Re-run analyses without waiting
2. **Token Savings**: Avoid redundant API calls to Gemini
3. **Persistent Insights**: Export sessions for long-term reference

## 📖 Usage Examples

### Complete Workflow Example

```bash
# Start Claude Code
claude

# Load your project
mcp__gemini-collab-enhanced__load_codebase
  project_path: "/home/user/my-app"

# Get architecture overview
mcp__gemini-collab-enhanced__analyze_architecture

# Find specific functionality
mcp__gemini-collab-enhanced__semantic_search
  query: "payment processing logic"

# Get security improvements
mcp__gemini-collab-enhanced__suggest_improvements
  area: "security"

# Ask specific questions
mcp__gemini-collab-enhanced__ask_with_context
  question: "How can I optimize the database queries in the user service?"
```

## 🧠 How It Works

### Intelligent File Prioritization
The server uses a sophisticated scoring system to determine which files are most relevant:

- **Language weights** - Core languages (Python, JavaScript, TypeScript) get higher priority
- **Directory importance** - `src/`, `lib/`, `core/` directories are prioritized
- **File size optimization** - Balances completeness with context limits
- **Special files** - `main.py`, `index.js`, `app.py` get bonus priority

### Smart Token Management
- Uses `tiktoken` for accurate token counting
- Stays within Gemini's 1M token limit intelligently
- Fallback estimation when tiktoken unavailable
- Structured context formatting for optimal analysis

### Context Creation
Creates comprehensive context including:
- File tree structure with metadata
- Complete file contents with syntax highlighting
- Relevance scores and language detection
- Project statistics and organization

## 🔧 Technical Details

### Supported File Types
- **Languages**: Python, JavaScript, TypeScript, Java, C++, Go, Rust, Swift, Kotlin, Scala
- **Web**: HTML, CSS, SCSS, Vue, Svelte, React (JSX/TSX)
- **Config**: JSON, YAML, XML, Dockerfile, Terraform
- **Documentation**: Markdown, SQL scripts

### Performance Features
- Intelligent file filtering (skips `node_modules`, `.git`, `__pycache__`, etc.)
- Relevance-based file selection
- Token-aware content loading
- Efficient context creation

## 📁 Installation Details

The enhanced server is installed at: `~/.claude-mcp-servers/gemini-collab-enhanced/`

### File Structure
```
~/.claude-mcp-servers/gemini-collab-enhanced/
├── enhanced_server.py      # Main server with intelligent analysis
├── requirements.txt        # Python dependencies
└── test_enhanced.py       # Test suite
```

## 🐛 Troubleshooting

**Server not showing up?**
```bash
# Check installation
claude mcp list

# Reinstall if needed
claude mcp remove gemini-collab-enhanced
./enhanced_setup.sh
```

**Token counting issues?**
```bash
# Install tiktoken for accurate counting
pip install tiktoken>=0.5.1
```

**Large codebase not loading completely?**
- Increase `max_tokens` parameter
- Check file relevance scores
- Exclude unnecessary directories

**Connection errors?**
- Verify Gemini API key is valid
- Check internet connection
- Ensure dependencies are installed: `pip install -r requirements.txt`

## 🔄 Updates

### From Basic to Enhanced
If upgrading from the basic MCP server:

1. **Install enhanced version:**
```bash
git clone https://github.com/ECamposSoria/gemini-mcp-enhanced.git
cd gemini-mcp-enhanced
./enhanced_setup.sh
```

2. **Remove old version (optional):**
```bash
claude mcp remove gemini-collab
```

## 🎯 Best Practices

### For Large Codebases
- Start with architectural analysis
- Use semantic search to find specific areas
- Focus improvement suggestions on specific areas
- Break down complex questions into smaller parts

### For Security Analysis
1. Load codebase
2. Run security-focused improvements
3. Use semantic search for auth/validation code
4. Ask specific security questions with context

### For Performance Optimization
1. Analyze architecture first
2. Search for performance-critical code
3. Get performance-focused suggestions
4. Trace code flow for bottlenecks

## 🤝 Contributing

Contributions welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Submit a pull request

## 📜 License

MIT License - Use freely!

## 🙏 Acknowledgments

- Built for the Claude Code community
- Powered by Google's Gemini AI
- Enhanced by ECamposSoria

---

**Ready to revolutionize your code analysis?** 🚀

Start by loading your first codebase and experience the power of AI-driven development insights!