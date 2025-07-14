#!/usr/bin/env python3
"""
Enhanced Claude-Gemini MCP Server
Leverages Gemini's 1M token context for intelligent codebase analysis
Based on Gemini's architectural recommendations
"""

import json
import sys
import os
import glob
import asyncio
from typing import Dict, Any, Optional, List, Tuple
from pathlib import Path
from dataclasses import dataclass
from datetime import datetime

# Ensure unbuffered output
sys.stdout = os.fdopen(sys.stdout.fileno(), 'w', 1)
sys.stderr = os.fdopen(sys.stderr.fileno(), 'w', 1)

__version__ = "2.0.0"

# Token counting - try tiktoken first, fallback to estimation
try:
    import tiktoken
    TIKTOKEN_AVAILABLE = True
    encoding = tiktoken.get_encoding("cl100k_base")
except ImportError:
    TIKTOKEN_AVAILABLE = False

# Initialize Gemini
try:
    import google.generativeai as genai
    
    API_KEY = os.environ.get("GEMINI_API_KEY", "YOUR_API_KEY_HERE")
    if API_KEY == "YOUR_API_KEY_HERE":
        print(json.dumps({
            "jsonrpc": "2.0",
            "error": {
                "code": -32603,
                "message": "Please set your Gemini API key in GEMINI_API_KEY environment variable"
            }
        }), file=sys.stdout, flush=True)
        sys.exit(1)
    
    genai.configure(api_key=API_KEY)
    model = genai.GenerativeModel('gemini-2.0-flash')
    GEMINI_AVAILABLE = True
except Exception as e:
    GEMINI_AVAILABLE = False
    GEMINI_ERROR = str(e)

@dataclass
class FileInfo:
    """Metadata for each file in the codebase"""
    path: str
    content: str
    tokens: int
    size: int
    modified: datetime
    language: str
    relevance_score: float

class CodebaseIngestion:
    """Handles codebase scanning, parsing, and relevance scoring"""
    
    # File extensions to include
    CODE_EXTENSIONS = {
        '.py', '.js', '.ts', '.jsx', '.tsx', '.java', '.cpp', '.c', '.h', 
        '.cs', '.php', '.rb', '.go', '.rs', '.swift', '.kt', '.scala',
        '.html', '.css', '.scss', '.vue', '.svelte', '.md', '.yml', '.yaml',
        '.json', '.xml', '.sql', '.sh', '.dockerfile', '.tf', '.tf'
    }
    
    # Directories and patterns to skip
    SKIP_PATTERNS = {
        'node_modules', '.git', '__pycache__', '.venv', 'venv', 'dist', 
        'build', '.next', '.nuxt', 'target', 'bin', 'obj', '.idea', 
        '.vscode', 'coverage', '.pytest_cache', '.mypy_cache',
        '*.lock', 'package-lock.json', 'yarn.lock', '*.log'
    }
    
    @staticmethod
    def count_tokens(text: str) -> int:
        """Count tokens using tiktoken or fallback estimation"""
        if TIKTOKEN_AVAILABLE:
            return len(encoding.encode(text))
        else:
            # Fallback: rough estimate (4 chars per token)
            return len(text) // 4
    
    @staticmethod
    def get_language(file_path: str) -> str:
        """Detect programming language from file extension"""
        ext = Path(file_path).suffix.lower()
        language_map = {
            '.py': 'python', '.js': 'javascript', '.ts': 'typescript',
            '.jsx': 'react', '.tsx': 'react-ts', '.java': 'java',
            '.cpp': 'cpp', '.c': 'c', '.h': 'c-header',
            '.cs': 'csharp', '.php': 'php', '.rb': 'ruby',
            '.go': 'go', '.rs': 'rust', '.swift': 'swift',
            '.kt': 'kotlin', '.scala': 'scala', '.html': 'html',
            '.css': 'css', '.scss': 'scss', '.vue': 'vue',
            '.svelte': 'svelte', '.md': 'markdown', '.yml': 'yaml',
            '.yaml': 'yaml', '.json': 'json', '.xml': 'xml',
            '.sql': 'sql', '.sh': 'bash', '.dockerfile': 'docker',
            '.tf': 'terraform'
        }
        return language_map.get(ext, 'unknown')
    
    @staticmethod
    def calculate_relevance_score(file_info: Dict[str, Any], project_root: str) -> float:
        """Calculate relevance score for file prioritization"""
        score = 1.0
        path = file_info['relative_path']
        
        # Language importance (core languages get higher scores)
        language_weights = {
            'python': 1.2, 'javascript': 1.2, 'typescript': 1.3,
            'java': 1.2, 'cpp': 1.1, 'go': 1.2, 'rust': 1.2,
            'css': 0.8, 'html': 0.7, 'json': 0.6, 'yaml': 0.5
        }
        score *= language_weights.get(file_info['language'], 1.0)
        
        # Directory importance (src, lib, core dirs are more important)
        if any(core_dir in path for core_dir in ['src/', 'lib/', 'core/', 'app/']):
            score *= 1.3
        elif any(low_dir in path for low_dir in ['test/', 'tests/', 'docs/', 'doc/']):
            score *= 0.7
        elif any(config_dir in path for config_dir in ['config/', 'configs/', 'settings/']):
            score *= 0.6
        
        # File size factor (prefer smaller files for better fit)
        if file_info['tokens'] < 100:
            score *= 1.1
        elif file_info['tokens'] > 5000:
            score *= 0.8
        elif file_info['tokens'] > 10000:
            score *= 0.6
        
        # Main files get higher priority
        filename = Path(path).name.lower()
        if filename in ['main.py', 'index.js', 'app.py', 'server.py', 'main.go']:
            score *= 1.5
        elif filename.startswith('test_') or filename.endswith('_test.py'):
            score *= 0.7
        
        return score
    
    @classmethod
    def scan_codebase(cls, project_path: str, max_tokens: int = 900000) -> Dict[str, Any]:
        """Scan and prepare codebase for Gemini context"""
        project_path = Path(project_path).resolve()
        files_info = []
        total_tokens = 0
        
        for file_path in project_path.rglob('*'):
            # Skip directories and hidden files
            if file_path.is_dir() or file_path.name.startswith('.'):
                continue
                
            # Skip unwanted patterns
            relative_path = file_path.relative_to(project_path)
            if any(pattern in str(relative_path) for pattern in cls.SKIP_PATTERNS):
                continue
                
            # Only include code files
            if file_path.suffix.lower() not in cls.CODE_EXTENSIONS:
                continue
                
            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                    
                # Skip empty files
                if not content.strip():
                    continue
                    
                file_tokens = cls.count_tokens(content)
                
                # Skip extremely large individual files
                if file_tokens > 50000:
                    continue
                
                file_info = {
                    'path': str(file_path),
                    'relative_path': str(relative_path),
                    'content': content,
                    'tokens': file_tokens,
                    'size': len(content),
                    'modified': datetime.fromtimestamp(file_path.stat().st_mtime),
                    'language': cls.get_language(str(file_path))
                }
                
                # Calculate relevance score
                file_info['relevance_score'] = cls.calculate_relevance_score(file_info, str(project_path))
                
                files_info.append(file_info)
                total_tokens += file_tokens
                
            except Exception as e:
                continue
        
        # Sort by relevance score (highest first)
        files_info.sort(key=lambda x: x['relevance_score'], reverse=True)
        
        # Trim to fit within token limit
        selected_files = []
        used_tokens = 0
        
        for file_info in files_info:
            if used_tokens + file_info['tokens'] <= max_tokens:
                selected_files.append(file_info)
                used_tokens += file_info['tokens']
            else:
                break
        
        return {
            'files': selected_files,
            'total_tokens': used_tokens,
            'total_files': len(selected_files),
            'scanned_files': len(files_info),
            'project_path': str(project_path)
        }

class ContextManager:
    """Manages the 1M token context window for Gemini"""
    
    @staticmethod
    def create_codebase_context(codebase_data: Dict[str, Any]) -> str:
        """Create formatted context for Gemini with structured representation"""
        
        context = f"""# INTELLIGENT CODEBASE ANALYSIS CONTEXT

## PROJECT OVERVIEW
- **Path:** {codebase_data['project_path']}
- **Files Loaded:** {codebase_data['total_files']} (out of {codebase_data['scanned_files']} scanned)
- **Total Tokens:** {codebase_data['total_tokens']:,}
- **Analysis Capabilities:** Architecture, Semantic Search, Improvements, Code Flow

## CODEBASE STRUCTURE

"""
        
        # Add file tree structure
        context += "### File Tree:\n"
        for file_info in codebase_data['files'][:20]:  # Show top 20 files in tree
            context += f"- {file_info['relative_path']} ({file_info['language']}, {file_info['tokens']} tokens, score: {file_info['relevance_score']:.2f})\n"
        
        if len(codebase_data['files']) > 20:
            context += f"... and {len(codebase_data['files']) - 20} more files\n"
        
        context += "\n## COMPLETE FILE CONTENTS:\n\n"
        
        # Add all file contents with clear delimiters
        for file_info in codebase_data['files']:
            context += f"### 📁 {file_info['relative_path']} ({file_info['language']})\n"
            context += f"```{file_info['language']}\n{file_info['content']}\n```\n\n"
        
        context += """
## ANALYSIS INSTRUCTIONS:
You now have the complete codebase loaded in your context with intelligent file prioritization.
When answering questions:
1. Reference specific files and line numbers when possible
2. Consider the overall architecture and relationships between files
3. Provide concrete, actionable insights
4. Focus on the most relevant files based on the user's query
5. Use your understanding of the complete codebase context
"""
        
        return context

# Global state
current_codebase_context = None
current_project_path = None
current_codebase_data = None

def send_response(response: Dict[str, Any]):
    """Send a JSON-RPC response"""
    print(json.dumps(response), flush=True)

def handle_initialize(request_id: Any) -> Dict[str, Any]:
    """Handle initialization"""
    return {
        "jsonrpc": "2.0",
        "id": request_id,
        "result": {
            "protocolVersion": "2024-11-05",
            "capabilities": {"tools": {}},
            "serverInfo": {
                "name": "enhanced-claude-gemini-mcp",
                "version": __version__
            }
        }
    }

def handle_tools_list(request_id: Any) -> Dict[str, Any]:
    """List available enhanced analysis tools"""
    if not GEMINI_AVAILABLE:
        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "result": {"tools": []}
        }
    
    tools = [
        {
            "name": "load_codebase",
            "description": "Load entire codebase into Gemini's 1M token context with intelligent prioritization",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "project_path": {
                        "type": "string",
                        "description": "Path to the project directory to analyze"
                    },
                    "max_tokens": {
                        "type": "number",
                        "description": "Maximum tokens to use (default: 900000)",
                        "default": 900000
                    }
                },
                "required": ["project_path"]
            }
        },
        {
            "name": "analyze_architecture",
            "description": "Get comprehensive architecture analysis of loaded codebase",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "focus": {
                        "type": "string",
                        "description": "Focus area: architecture, patterns, dependencies, structure, or custom query",
                        "default": "architecture"
                    }
                }
            }
        },
        {
            "name": "semantic_search",
            "description": "Search codebase semantically using natural language queries",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Natural language description of what to find in the codebase"
                    }
                },
                "required": ["query"]
            }
        },
        {
            "name": "suggest_improvements",
            "description": "Get specific improvement suggestions for the loaded codebase",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "area": {
                        "type": "string",
                        "description": "Focus area: performance, security, maintainability, testing, architecture, or general",
                        "default": "general"
                    }
                }
            }
        },
        {
            "name": "explain_codeflow",
            "description": "Trace and explain how specific functionality works across the codebase",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "functionality": {
                        "type": "string",
                        "description": "Describe the functionality to trace through the codebase"
                    }
                },
                "required": ["functionality"]
            }
        },
        {
            "name": "codebase_summary",
            "description": "Get a comprehensive summary of the loaded codebase",
            "inputSchema": {
                "type": "object",
                "properties": {}
            }
        },
        {
            "name": "ask_with_context",
            "description": "Ask any question with full codebase context and intelligent analysis",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "question": {
                        "type": "string",
                        "description": "Your question about the codebase"
                    }
                },
                "required": ["question"]
            }
        }
    ]
    
    return {
        "jsonrpc": "2.0",
        "id": request_id,
        "result": {"tools": tools}
    }

def call_gemini_with_context(prompt: str, temperature: float = 0.3) -> str:
    """Call Gemini with current codebase context"""
    try:
        if current_codebase_context:
            full_prompt = current_codebase_context + "\n\n## USER QUERY:\n" + prompt
        else:
            full_prompt = "❌ No codebase loaded. Please use 'load_codebase' first.\n\n" + prompt
            
        response = model.generate_content(
            full_prompt,
            generation_config=genai.GenerationConfig(
                temperature=temperature,
                max_output_tokens=8192,
            )
        )
        return response.text
    except Exception as e:
        return f"Error calling Gemini: {str(e)}"

def handle_tool_call(request_id: Any, params: Dict[str, Any]) -> Dict[str, Any]:
    """Handle enhanced tool execution"""
    global current_codebase_context, current_project_path, current_codebase_data
    
    tool_name = params.get("name")
    arguments = params.get("arguments", {})
    
    try:
        if tool_name == "load_codebase":
            project_path = arguments.get("project_path")
            max_tokens = arguments.get("max_tokens", 900000)
            
            if not os.path.exists(project_path):
                result = f"❌ Error: Project path '{project_path}' does not exist"
            else:
                # Scan and ingest codebase
                codebase_data = CodebaseIngestion.scan_codebase(project_path, max_tokens)
                current_codebase_context = ContextManager.create_codebase_context(codebase_data)
                current_project_path = project_path
                current_codebase_data = codebase_data
                
                # Create summary with statistics
                languages = {}
                for file_info in codebase_data['files']:
                    lang = file_info['language']
                    languages[lang] = languages.get(lang, 0) + 1
                
                lang_summary = ", ".join([f"{lang}: {count}" for lang, count in sorted(languages.items())])
                
                result = f"""✅ INTELLIGENT CODEBASE LOADED SUCCESSFULLY

📁 **Project:** {codebase_data['project_path']}
📄 **Files Loaded:** {codebase_data['total_files']} (from {codebase_data['scanned_files']} scanned)
🧮 **Tokens Used:** {codebase_data['total_tokens']:,} / 1,000,000
📊 **Languages:** {lang_summary}
🎯 **Prioritization:** Files ranked by relevance score

Gemini now has your entire codebase intelligently loaded in context!

**Available Analysis Tools:**
• `analyze_architecture` - Comprehensive architecture analysis
• `semantic_search` - Natural language code search  
• `suggest_improvements` - Targeted improvement suggestions
• `explain_codeflow` - Trace functionality across files
• `codebase_summary` - Complete project overview
• `ask_with_context` - Ask anything about your code

Ready for intelligent analysis! 🧠"""

        elif tool_name == "analyze_architecture":
            if not current_codebase_context:
                result = "❌ No codebase loaded. Use 'load_codebase' first."
            else:
                focus = arguments.get("focus", "architecture")
                prompt = f"""Provide a comprehensive {focus} analysis of this codebase. Include:

1. **Overall Architecture & Design Patterns**
2. **Key Components & Their Relationships** 
3. **Data Flow & Dependencies**
4. **Technology Stack & Framework Usage**
5. **Code Organization & Structure Quality**
6. **Notable Design Decisions**

Be specific and reference actual files, functions, and code patterns you observe."""
                result = call_gemini_with_context(prompt, 0.2)

        elif tool_name == "semantic_search":
            if not current_codebase_context:
                result = "❌ No codebase loaded. Use 'load_codebase' first."
            else:
                query = arguments.get("query")
                prompt = f"""Perform a semantic search for: "{query}"

Provide:
1. **Exact file locations** where this functionality exists
2. **Relevant code snippets** with line context
3. **Related functions/classes** that work together
4. **Usage patterns** across the codebase
5. **Dependencies** and connections to other parts

Focus on semantic meaning, not just keyword matching."""
                result = call_gemini_with_context(prompt, 0.2)

        elif tool_name == "suggest_improvements":
            if not current_codebase_context:
                result = "❌ No codebase loaded. Use 'load_codebase' first."
            else:
                area = arguments.get("area", "general")
                prompt = f"""Analyze the codebase and suggest specific improvements for {area}:

Provide:
1. **Specific Issues** with file/line references
2. **Concrete Solutions** with code examples
3. **Priority Ranking** (High/Medium/Low)
4. **Implementation Steps** for each suggestion
5. **Potential Risks** of each change

Focus on actionable improvements with clear benefits."""
                result = call_gemini_with_context(prompt, 0.3)

        elif tool_name == "explain_codeflow":
            if not current_codebase_context:
                result = "❌ No codebase loaded. Use 'load_codebase' first."
            else:
                functionality = arguments.get("functionality")
                prompt = f"""Trace and explain how this functionality works: "{functionality}"

Provide:
1. **Entry Points** - Where this functionality starts
2. **Code Flow** - Step-by-step execution path across files
3. **Key Functions/Classes** - Main components involved
4. **Data Transformations** - How data flows and changes
5. **External Dependencies** - APIs, databases, etc.
6. **Visual Flow** - ASCII diagram if helpful

Reference specific files and line numbers."""
                result = call_gemini_with_context(prompt, 0.2)

        elif tool_name == "codebase_summary":
            if not current_codebase_context:
                result = "❌ No codebase loaded. Use 'load_codebase' first."
            else:
                prompt = """Provide a comprehensive summary of this entire codebase:

1. **Project Purpose** - What does this software do?
2. **Architecture Overview** - How is it structured?
3. **Key Features** - Main functionality areas
4. **Technology Stack** - Languages, frameworks, tools
5. **Code Quality Assessment** - Strengths and areas for improvement
6. **Development Insights** - Patterns, conventions, notable aspects

Make it accessible for both technical and non-technical stakeholders."""
                result = call_gemini_with_context(prompt, 0.3)

        elif tool_name == "ask_with_context":
            if not current_codebase_context:
                result = "❌ No codebase loaded. Use 'load_codebase' first."
            else:
                question = arguments.get("question")
                result = call_gemini_with_context(question, 0.3)

        else:
            raise ValueError(f"Unknown tool: {tool_name}")
        
        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "result": {
                "content": [
                    {
                        "type": "text",
                        "text": f"🧠 GEMINI INTELLIGENT ANALYSIS:\n\n{result}"
                    }
                ]
            }
        }
    except Exception as e:
        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "error": {
                "code": -32603,
                "message": str(e)
            }
        }

def main():
    """Main server loop"""
    while True:
        try:
            line = sys.stdin.readline()
            if not line:
                break
            
            request = json.loads(line.strip())
            method = request.get("method")
            request_id = request.get("id")
            params = request.get("params", {})
            
            if method == "initialize":
                response = handle_initialize(request_id)
            elif method == "tools/list":
                response = handle_tools_list(request_id)
            elif method == "tools/call":
                response = handle_tool_call(request_id, params)
            else:
                response = {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "error": {
                        "code": -32601,
                        "message": f"Method not found: {method}"
                    }
                }
            
            send_response(response)
            
        except json.JSONDecodeError:
            continue
        except EOFError:
            break
        except Exception as e:
            if 'request_id' in locals():
                send_response({
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "error": {
                        "code": -32603,
                        "message": f"Internal error: {str(e)}"
                    }
                })

if __name__ == "__main__":
    main()