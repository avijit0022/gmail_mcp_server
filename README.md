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

### Cross-Platform (Recommended)

```bash
python scripts/setup.py
```

Works on Linux, macOS, and Windows. The script will:
1. Verify Python 3.10+ is installed
2. Create a `.venv` virtual environment (using `uv` if available, otherwise `venv` + `pip`)
3. Install dependencies from `requirements.txt`
4. Copy `.env.template` → `.env` if it doesn't exist yet

### Platform-Specific (Alternative)

<details>
<summary>Linux / macOS</summary>

```bash
bash scripts/setup.sh
```
Automatically installs Python via your system package manager if not found.
</details>

<details>
<summary>Windows (PowerShell)</summary>

```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
.\scripts\setup.ps1
```
Automatically installs Python via `winget`, `choco`, or `scoop` if not found.
</details>

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

```bash
python scripts/start.py
```

### Stop the server

```bash
python scripts/stop.py
```

The server runs in the background and logs to `gmail_mcp.log`.

<details>
<summary>Platform-specific alternatives</summary>

**Linux / macOS**
```bash
bash scripts/start.sh
bash scripts/stop.sh
```

**Windows (PowerShell)**
```powershell
.\scripts\start.ps1
.\scripts\stop.ps1
```
</details>

## Connecting to Claude

Add the server to your Claude MCP configuration:

```json
{
  "mcpServers": {
    "gmail_mcp_server":{ 
			"type": "http",
			"url": "http://localhost:9001/mcp"
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
| `subject` | `str` | No | Mail Subject |
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
    ├── setup.py               # Cross-platform setup
    ├── start.py               # Cross-platform start
    ├── stop.py                # Cross-platform stop
    ├── setup.sh / setup.ps1   # Platform-specific setup (alternative)
    ├── start.sh / start.ps1   # Platform-specific start (alternative)
    └── stop.sh  / stop.ps1    # Platform-specific stop (alternative)
```
