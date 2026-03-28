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
    #format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(os.path.join(pathlib.Path(__file__).parent.resolve(), 'gmail_mcp.log')),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger("     "+__name__)

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
    logger.info(f"Successfully imported modules from the virtual environment.")
except ImportError:
    logger.error(f"Error: Could not import your_module_name. Make sure it's installed in the virtual environment at {site_packages_path}")
    sys.exit

# Reading Environment Variables

ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")
GMAIL_MCP_PORT = int(os.getenv("GMAIL_MCP_SERVER_PORT", 9000))
GMAIL_MCP_HOST = os.getenv("GMAIL_MCP_SERVER_HOST", "localhost")
SENDER = os.getenv("SENDER_EMAIL", None)


mcp = FastMCP(name="gmail_mcp_server", host=GMAIL_MCP_HOST, port=GMAIL_MCP_PORT, streamable_http_path="/mcp")
warnings.filterwarnings('ignore')


@mcp.tool()
def send_html_mail(receiver_email : str, body : str, email_subject : Optional[str] = None, cc_email  : Optional[str] = None, files : Optional[dict] = None, images : Optional[dict] = None) -> str:
    """
    Sends a beautifully formatted HTML email with optional attachments using Gmail's SMTP server.

    This tool sends a richly styled HTML email through Gmail's SMTP service with
    support for CC recipients, file attachments, and inline images.

    IMPORTANT — The `body` parameter accepts full HTML markup. You should provide
    well-structured, visually appealing HTML to produce professional-looking emails.
    Use modern HTML email best practices:

    - Use inline CSS styles (e.g., `style="color: #333; font-family: Arial, sans-serif;"`)
      since most email clients strip `<style>` blocks.
    - Use `<table>` layouts for consistent rendering across email clients.
    - Structure content with headings (`<h1>`–`<h3>`), paragraphs (`<p>`),
      lists (`<ul>`, `<ol>`), dividers (`<hr>`), and blockquotes (`<blockquote>`).
    - Add visual polish with background colors, padding, borders, and spacing.
    - Wrap the entire body in a container table for centered, max-width layouts.

    Example of a well-formatted HTML body:
        ```
        <table width="100%" cellpadding="0" cellspacing="0" style="background-color:#f4f4f4;">
          <tr><td align="center" style="padding:20px;">
            <table width="600" cellpadding="0" cellspacing="0"
                   style="background-color:#ffffff; border-radius:8px; overflow:hidden;">
              <tr><td style="background-color:#4A90D9; padding:24px; text-align:center;">
                <h1 style="color:#ffffff; margin:0; font-family:Arial,sans-serif;">Email Title</h1>
              </td></tr>
              <tr><td style="padding:24px; font-family:Arial,sans-serif; color:#333333; line-height:1.6;">
                <p>Hello,</p>
                <p>This is a <strong>beautifully formatted</strong> email with a
                   <a href="https://example.com" style="color:#4A90D9;">link</a>.</p>
                <hr style="border:none; border-top:1px solid #eeeeee; margin:16px 0;">
                <p style="font-size:12px; color:#999999;">Footer text here.</p>
              </td></tr>
            </table>
          </td></tr>
        </table>
        ```

    Args:
        receiver_email (str): The primary recipient's email address.
            Must be a valid email format (e.g., "user@example.com").
        body (str): The full HTML content of the email body. Provide beautifully
            formatted HTML with inline CSS styles for professional-looking emails.
            Supports all standard HTML elements: headings, paragraphs, tables,
            lists, links, images, dividers, blockquotes, and more.
        email_subject (Optional[str]): The subject line of the email.
            Defaults to "Automated Mail" if not provided.
        cc_email (Optional[str]): Carbon copy recipient's email address.
            Defaults to None if no CC is needed.
        files (Optional[dict]): Dictionary of file attachments.
            Keys are filenames with extensions (e.g., "report.pdf").
            Values are full file paths (e.g., "/home/user/Documents/report.pdf").
            Defaults to None if no attachments are needed.
        images (Optional[dict]): Dictionary of images to embed inline in the email body.
            Keys are image names with extensions (e.g., "logo.png").
            Values are full file paths (e.g., "/home/user/Images/logo.png").
            Images are referenced via `cid:img1`, `cid:img2`, etc. in order.
            Defaults to None if no inline images are needed.

    Returns:
        str: A status message indicating success or failure.
            - On success: "Email sent successfully to: <recipients>"
            - On failure: "Error: <details>"

    Example:
        # Send a simple styled email
        >>> send_html_mail(
        ...     receiver_email="recipient@example.com",
        ...     body='<div style="font-family:Arial,sans-serif; padding:20px;">'
        ...          '<h2 style="color:#2c3e50;">Hello!</h2>'
        ...          '<p style="color:#555;">This is a <strong>styled</strong> email.</p></div>'
        ... )
        "Email sent successfully."

        # Send email with attachments and CC
        >>> send_html_mail(
        ...     receiver_email="recipient@example.com",
        ...     body='<p style="font-family:Arial;">Please find the attached report.</p>',
        ...     email_subject="Q4 Report",
        ...     cc_email="manager@example.com",
        ...     files={"Q4_Report.pdf": "/path/to/Q4_Report.pdf"}
        ... )
        "Email sent successfully."

    Note:
        - Requires a Gmail App Password set via ACCESS_TOKEN env var (not regular password).
        - Gmail must have 2FA enabled and an App Password generated.
        - Use inline CSS only — most email clients ignore <style> blocks and external stylesheets.
        - Supported attachment types: Any file type (PDF, XLSX, images, etc.)
        - Maximum email size with attachments is subject to Gmail's 25MB limit.
    """
    logger.info(f"Attempting to send email to: {receiver_email}")
    
    sender_email = SENDER

    # Validate email addresses
    if not sender_email:
        error_msg = f"Sender Email Not set."
        logger.error(error_msg)
        return f"Error: {error_msg}"

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
    
    subject = email_subject if email_subject else "Automated Mail"
    
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
        message["Subject"] = subject
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
            
        return f"Email sent successfully to: {', '.join(recipients)}"
        
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
    logger.info(f"Starting Gmail MCP Server on http://{GMAIL_MCP_HOST}:{GMAIL_MCP_PORT}/mcp ...")
    try:
        mcp.run(transport="streamable-http")
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
    except Exception as e:
        logger.error(f"Server error: {e}", exc_info=True)
