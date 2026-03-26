# Gmail MCP Server

An MCP (Model Context Protocol) server that exposes Gmail sending capabilities as tools, allowing AI assistants like Claude to send HTML emails via Gmail's SMTP.

## Features

- Send HTML emails with optional CC, file attachments, and inline images
- Runs as a Streamable HTTP MCP server
- Gmail App Password authentication (no OAuth required)

## Prerequisites

- Python 3.10+
- A Gmail account with **2-Factor Authentication** enabled
- A **Gmail App Password** (generated at [myaccount.google.com/apppasswords](https://myaccount.google.com/apppasswords))
- `uv` (recommended) or `pip`

## Setup

### Linux / macOS

```bash
bash scripts/setup.sh
```

### Windows (PowerShell)

```powershell
# Allow local scripts to run (one-time, per machine)
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

.\scripts\setup.ps1
```

Both scripts will:
1. Create a `.venv` virtual environment and install dependencies
2. Copy `.env.template` → `.env` if it doesn't exist yet

### Configure `.env`

Edit `.env` and fill in your values:

```env
ACCESS_TOKEN=your_gmail_app_password
SENDER_EMAIL=your_gmail_address@gmail.com

GMAIL_MCP_SERVER_HOST=localhost
GMAIL_MCP_SERVER_PORT=9000

SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
```

## Usage

### Start the server

**Linux / macOS**
```bash
bash scripts/start.sh
```

**Windows**
```powershell
.\scripts\start.ps1
```

The server starts in the background and logs to `gmail_mcp.log`.

### Stop the server

**Linux / macOS**
```bash
bash scripts/stop.sh
```

**Windows**
```powershell
.\scripts\stop.ps1
```

## Connecting to Claude

Add the server to your Claude MCP configuration:

```json
{
  "mcpServers": {
    "gmail": {
      "url": "http://localhost:9000/mcp"
    }
  }
}
```

## Available Tool

### `send_html_mail`

Sends an HTML email via Gmail SMTP.

| Parameter | Type | Required | Description |
|---|---|---|---|
| `receiver_email` | `str` | Yes | Primary recipient email address |
| `body` | `str` | Yes | HTML content of the email body |
| `cc_email` | `str` | No | CC recipient email address |
| `files` | `dict` | No | `{"filename.ext": "/full/path/to/file"}` |
| `images` | `dict` | No | `{"image.png": "/full/path/to/image.png"}` |

The sender address is configured via the `SENDER_EMAIL` environment variable.

Returns `"Email sent successfully."` on success, or an error message on failure.

## Project Structure

```
gmail_agent/
├── gmail_mcp_server.py   # MCP server
├── requirements.txt
├── .env.template         # Environment variable template
├── .env                  # Your local config (git-ignored)
├── gmail_mcp.log         # Runtime log (auto-created)
└── scripts/
    ├── setup.sh / setup.ps1   # One-time environment setup
    ├── start.sh / start.ps1   # Start the server
    └── stop.sh  / stop.ps1    # Stop the server
```
