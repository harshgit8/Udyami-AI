# Udyami AI - Personal Knowledge Base System

A local-first AI system that searches YOUR documents before providing answers.

## Quick Start

### 1. Start Backend
```bash
START_UDYAMI_AI.bat
```

### 2. Configure Claude Desktop

Edit: `%APPDATA%\Claude\claude_desktop_config.json`

```json
{
  "mcpServers": {
    "udyami-ai": {
      "command": "node",
      "args": ["D:/A_LEARN/helix-main/udyami-mcp-docker/dist/index.js"],
      "env": {
        "MCP_USER_ID": "local_user",
        "BACKEND_URL": "http://localhost:8000/search"
      }
    }
  }
}
```

### 3. Restart Claude Desktop

### 4. Upload Documents

Go to: `http://localhost:3000/dashboard/upload`

Upload PDFs, DOCX, TXT files - they'll be automatically processed and searchable.

### 5. Ask Questions

Claude will ALWAYS search your documents first. If not found, it will say so.

## Features

- ✅ **Automatic Document Processing** - PDFs, DOCX, TXT extracted and indexed
- ✅ **Smart Search** - Keyword extraction and ranked results
- ✅ **Strict Mode** - Only answers from YOUR documents
- ✅ **Real-time** - New uploads immediately searchable
- ✅ **Local-first** - No cloud dependencies

## System Requirements

- Node.js (v20+)
- Python (3.10+)
- Windows/Mac/Linux

## Architecture

```
Claude Desktop → MCP Server → Backend API → Your Documents
```

## Current Status

- Backend: Udyami AI Local Backend
- MCP Server: Udyami AI
- Tool Name: udyami-ai

## Support

All errors resolved ✅
All documentation cleaned up ✅
System ready to use ✅
