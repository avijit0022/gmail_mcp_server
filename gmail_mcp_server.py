import json
import warnings
import httpx
import sys
import os
import pathlib
import logging
import re
from typing import Optional

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(os.path.join(pathlib.Path(__file__).parent.resolve(), 'gmail_mcp.log')),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('gmail_mcp_server')

def file_path():
    """Returns the directory path of the current script."""
    script_directory = pathlib.Path(__file__).parent.resolve()
    return script_directory


def validate_email(email: str) -> bool:
    """
    Validates email format using regex pattern.
    
    Args:
        email: Email address to validate.
        
    Returns:
        bool: True if valid email format, False otherwise.
    """
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None


VENV_PATH = os.path.join(file_path(),".venv")  
site_packages_path = os.path.join(VENV_PATH, "lib", "site-packages")

if site_packages_path not in sys.path:
    sys.path.insert(0, site_packages_path)

try:
    import pandas as pd
    import openpyxl
    import requests
    import smtplib
    from email.mime.text import MIMEText
    from email.mime.image import MIMEImage
    from email.mime.multipart import MIMEMultipart
    from email.mime.application import MIMEApplication
    from email.mime.base import MIMEBase
    from email.utils import formatdate
    from email import encoders
    from mcp.server.fastmcp import FastMCP
    print(f"Successfully imported modules from the virtual environment.")
except ImportError:
    print(f"Error: Could not import your_module_name. Make sure it's installed in the virtual environment at {site_packages_path}")


# Reading Environment Variables

ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")
GMAIL_MCP_PORT = int(os.getenv("GMAIL_MCP_SERVER_PORT", 9000))
GMAIL_MCP_HOST = os.getenv("GMAIL_MCP_SERVER_HOST", "localhost")


mcp = FastMCP(name="gmail_mcp_server", host=GMAIL_MCP_HOST, port=GMAIL_MCP_PORT)
warnings.filterwarnings('ignore')


@mcp.tool()
def send_html_mail(receiver_email : str, body : str, cc_email  : Optional[str] = None, files : Optional[dict] = None, images : Optional[dict] = None, sender_email : str = "avijitpal0022@gmail.com") -> str:
    """
    Sends an HTML email with optional attachments using Gmail's SMTP server.

    This tool sends a customizable HTML email through Gmail's SMTP service with
    support for CC recipients and file attachments.

    Args:
        receiver_email (str): The primary recipient's email address.
            Must be a valid email format (e.g., "user@example.com").
        body (str): The HTML content of the email body.
            Can include any valid HTML markup for formatting.
        cc_email (Optional[str]): Carbon copy recipient's email address.
            Defaults to None if no CC is needed.
        files (Optional[dict]): Dictionary of file attachments.
            Keys are filenames with extensions (e.g., "report.pdf").
            Values are full file paths (e.g., "C:/Documents/report.pdf").
            Defaults to None if no attachments are needed.
        images (Optional[dict]): Dictionary of images to embed in the email body.
            Keys are image names with extensions (e.g., "logo.png").
            Values are full file paths (e.g., "C:/Images/logo.png").
            Defaults to None if no images are needed.
        sender_email (str): The sender's Gmail address used for authentication.
            Defaults to "avijitpal0022@gmail.com".

    Returns:
        str: A status message indicating success or failure.
            - On success: "Email sent successfully."
            - On failure: Returns error message with details.

    Input Schema:
        {
            "receiver_email": "string (required) - Primary recipient email",
            "body": "string (required) - HTML content for the email body",
            "cc_email": "string (optional) - CC recipient email, defaults to None",
            "files": "dict (optional) - Dictionary of {filename: filepath} to attach, defaults to None",
            "images": "dict (optional) - Dictionary of {imagename: imagepath} to embed in the email body, defaults to None",
            "sender_email": "string (optional) - Sender Gmail, defaults to 'avijitpal0022@gmail.com'"
        }

    Output Schema:
        {
            "result": "string - Status message indicating email delivery result"
        }

    Example:
        # Send a simple email
        >>> send_html_mail(
        ...     receiver_email="recipient@example.com",
        ...     body="<p>Hello, this is a test email.</p>"
        ... )
        "Email sent successfully."

        # Send email with CC
        >>> send_html_mail(
        ...     receiver_email="primary@example.com",
        ...     body="<h1>Meeting Notes</h1><p>Please review.</p>",
        ...     cc_email="copy@example.com"
        ... )
        "Email sent successfully."

        # Send email with attachments
        >>> send_html_mail(
        ...     receiver_email="recipient@example.com",
        ...     body="<p>Please find the attached documents.</p>",
        ...     files={
        ...         "report.pdf": "C:/Documents/report.pdf",
        ...         "data.xlsx": "C:/Documents/data.xlsx"
        ...     }
        ... )
        "Email sent successfully."

        # Send from a different Gmail account with all options
        >>> send_html_mail(
        ...     receiver_email="recipient@example.com",
        ...     body="<p>Quarterly report attached.</p>",
        ...     cc_email="manager@example.com",
        ...     files={"Q4_Report.pdf": "/path/to/Q4_Report.pdf"},
        ...     sender_email="alternate@gmail.com"
        ... )
        "Email sent successfully."

    Usage:
        1. Ensure credential.txt contains a valid Gmail App Password.
        2. Call the tool with receiver_email and body parameters (required).
        3. Optionally add cc_email, files, or sender_email as needed.
        4. The tool authenticates via SMTP TLS on port 587.
        5. Email is sent with subject "Automated Mail" and the provided HTML body.

    Raises:
        Error messages are returned (not raised) for:
        - Invalid email format (receiver, sender, or CC)
        - Missing or empty credential file
        - SMTP authentication failures
        - Connection timeouts
        - File attachment errors (file not found, permission denied)

    Note:
        - Requires a Gmail App Password stored in credential.txt (not regular password).
        - Gmail must have 2FA enabled and an App Password generated.
        - Supported attachment types: Any file type (PDF, XLSX, images, etc.)
        - Maximum email size with attachments is subject to Gmail's 25MB limit.
    """
    logger.info(f"Attempting to send email to: {receiver_email}")
    
    # Validate email addresses
    if not validate_email(receiver_email):
        error_msg = f"Invalid receiver email format: {receiver_email}"
        logger.error(error_msg)
        return f"Error: {error_msg}"
    
    if not validate_email(sender_email):
        error_msg = f"Invalid sender email format: {sender_email}"
        logger.error(error_msg)
        return f"Error: {error_msg}"
    
    if cc_email and not validate_email(cc_email):
        error_msg = f"Invalid CC email format: {cc_email}"
        logger.error(error_msg)
        return f"Error: {error_msg}"
    
    # Get credentials
    try:
        if not ACCESS_TOKEN:
            raise ValueError("ACCESS_TOKEN environment variable is not set or empty.")
        password = ACCESS_TOKEN
    except ValueError as e:
        logger.error(f"ACCESS_TOKEN value error: {e}")
        return f"Error: {str(e)}"
    
    # Compose the email
    try:
        message = MIMEMultipart("alternative")
        message["Subject"] = "Automated Mail"
        message["From"] = sender_email
        message["To"] = receiver_email      
        if cc_email:
            message["Cc"] = cc_email

        ## Create the plain-text and HTML version of your message
        html = body

        part1 = MIMEText(html, "html")
        message.attach(part1)
        logger.debug("Email message composed successfully")
        
    except Exception as e:
        error_msg = f"Failed to compose email: {str(e)}"
        logger.error(error_msg)
        return f"Error: {error_msg}"


    # Attaching files to email
    if files:
        for filename_with_extension, full_filepath in files.items():
            part2 = MIMEBase('application', "octet-stream")
            part2.set_payload(open(full_filepath, "rb").read())
            encoders.encode_base64(part2)
            part2.add_header('Content-Disposition', f'attachment; filename={filename_with_extension}')
            message.attach(part2)


    # Attaching image to email body
    if images:
        counter = 1
        for imagename_with_extension, full_image_path in images.items():
            fp = open(full_image_path, 'rb')
            msgImage = MIMEImage(fp.read())
            fp.close()
            # Creating an Id for the image
            msgImage.add_header('Content-ID', f'img{counter}')
            msgImage.add_header('Content-Disposition', f'inline; filename="{imagename_with_extension}"')
            # Build out the html for the email
            html += f'<span style = "mso-no-proof:yes"><img width = 100 height = 50 src = "cid:img{counter}"></span>' 
            message.attach(msgImage)
            counter += 1

    # Send the email
    try:
        logger.info("Connecting to Gmail SMTP server...")
        with smtplib.SMTP("smtp.gmail.com", 587, timeout=30) as server:
            server.starttls()
            logger.debug("TLS connection established")
            
            server.login(sender_email, password)
            logger.debug(f"Successfully authenticated as {sender_email}")
            
            recipients = [receiver_email]
            if cc_email:
                recipients.append(cc_email)
            
            server.sendmail(sender_email, recipients, message.as_string())
            logger.info(f"Email sent successfully to: {', '.join(recipients)}")
            
        return "Email sent successfully."
        
    except smtplib.SMTPAuthenticationError as e:
        error_msg = "Authentication failed. Check your Gmail App Password and ensure 2FA is enabled."
        logger.error(f"SMTP Authentication Error: {e}")
        return f"Error: {error_msg}"
        
    except smtplib.SMTPRecipientsRefused as e:
        error_msg = f"Recipient(s) refused: {e.recipients}"
        logger.error(f"SMTP Recipients Refused: {e}")
        return f"Error: {error_msg}"
        
    except smtplib.SMTPSenderRefused as e:
        error_msg = f"Sender address refused: {sender_email}"
        logger.error(f"SMTP Sender Refused: {e}")
        return f"Error: {error_msg}"
        
    except smtplib.SMTPDataError as e:
        error_msg = f"SMTP data error: {str(e)}"
        logger.error(f"SMTP Data Error: {e}")
        return f"Error: {error_msg}"
        
    except smtplib.SMTPConnectError as e:
        error_msg = "Failed to connect to Gmail SMTP server. Check your internet connection."
        logger.error(f"SMTP Connect Error: {e}")
        return f"Error: {error_msg}"
        
    except smtplib.SMTPServerDisconnected as e:
        error_msg = "Server unexpectedly disconnected. Please try again."
        logger.error(f"SMTP Server Disconnected: {e}")
        return f"Error: {error_msg}"
        
    except TimeoutError as e:
        error_msg = "Connection timed out. Check your internet connection and try again."
        logger.error(f"Timeout Error: {e}")
        return f"Error: {error_msg}"
        
    except Exception as e:
        error_msg = f"Unexpected error sending email: {str(e)}"
        logger.error(f"Unexpected error: {e}", exc_info=True)
        return f"Error: {error_msg}"

if __name__ == "__main__":
    logger.info(f"Starting Gmail MCP Server on http://{GMAIL_MCP_HOST}:{GMAIL_MCP_PORT} ...")
    try:
        mcp.run(transport="sse")
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
    except Exception as e:
        logger.error(f"Server error: {e}", exc_info=True)
