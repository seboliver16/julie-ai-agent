"""
Email Module

This module handles sending emails for expert scheduling.
"""

import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Check if we should use mock mode
USE_MOCK = os.getenv('USE_MOCK_EMAIL', 'True').lower() in ('true', '1', 't')

def send_email(to_email, subject, text_body, html_body=None):
    """
    Send an email.
    
    Args:
        to_email (str): Recipient email address
        subject (str): Email subject
        text_body (str): Plain text email body
        html_body (str, optional): HTML email body
        
    Returns:
        bool: True if email was sent successfully, False otherwise
    """
    if USE_MOCK:
        return _mock_send_email(to_email, subject, text_body, html_body)
    else:
        return _smtp_send_email(to_email, subject, text_body, html_body)

def _mock_send_email(to_email, subject, text_body, html_body=None):
    """
    Log email instead of sending it (for development).
    
    Args:
        to_email (str): Recipient email address
        subject (str): Email subject
        text_body (str): Plain text email body
        html_body (str, optional): HTML email body
        
    Returns:
        bool: Always returns True
    """
    logger.info("=" * 50)
    logger.info("MOCK EMAIL")
    logger.info("=" * 50)
    logger.info(f"To: {to_email}")
    logger.info(f"Subject: {subject}")
    logger.info("-" * 50)
    logger.info("Text Body:")
    logger.info(text_body)
    if html_body:
        logger.info("-" * 50)
        logger.info("HTML Body: [Not shown in logs]")
    logger.info("=" * 50)
    
    return True

def _smtp_send_email(to_email, subject, text_body, html_body=None):
    """
    Send an email using SMTP.
    
    Args:
        to_email (str): Recipient email address
        subject (str): Email subject
        text_body (str): Plain text email body
        html_body (str, optional): HTML email body
        
    Returns:
        bool: True if email was sent successfully, False otherwise
    """
    # Get email settings from config
    email_host = os.getenv('EMAIL_HOST')
    email_port = int(os.getenv('EMAIL_PORT', 587))
    email_username = os.getenv('EMAIL_USERNAME')
    email_password = os.getenv('EMAIL_PASSWORD')
    
    # Check if settings are available
    if not all([email_host, email_port, email_username, email_password]):
        logger.error("Email settings not configured. Check your config.py file.")
        return False
    
    try:
        # Create message
        msg = MIMEMultipart('alternative')
        msg['Subject'] = subject
        msg['From'] = email_username
        msg['To'] = to_email
        
        # Attach text body
        msg.attach(MIMEText(text_body, 'plain'))
        
        # Attach HTML body if provided
        if html_body:
            msg.attach(MIMEText(html_body, 'html'))
        
        # Connect to server and send
        server = smtplib.SMTP(email_host, email_port)
        server.starttls()
        server.login(email_username, email_password)
        server.send_message(msg)
        server.quit()
        
        logger.info(f"Email sent to {to_email}")
        return True
    
    except Exception as e:
        logger.error(f"Failed to send email: {str(e)}")
        return False

def send_expert_selection_email(user_email, experts, query):
    """
    Send an email with selected experts.
    
    Args:
        user_email (str): User's email address
        experts (list): List of selected expert dictionaries
        query (str): Original search query
        
    Returns:
        bool: True if email was sent successfully, False otherwise
    """
    subject = "Julie AI: Your Selected Experts"
    
    # Plain text version
    text_body = f"Hello,\n\n"
    text_body += f"Based on your query: \"{query}\", you've selected the following experts:\n\n"
    
    for i, expert in enumerate(experts, 1):
        text_body += f"{i}. {expert['name']}\n"
        text_body += f"   {expert['title']} at {expert['company']}\n"
        text_body += f"   Location: {expert['location']}\n"
        text_body += f"   Profile: {expert['profile_url']}\n\n"
    
    text_body += "Please reply to this email with your availability for the next week, and we'll coordinate with these experts.\n\n"
    text_body += "Best regards,\nJulie AI"
    
    # HTML version
    html_body = f"""
    <html>
    <head></head>
    <body>
        <p>Hello,</p>
        <p>Based on your query: "<em>{query}</em>", you've selected the following experts:</p>
        
        <ul>
    """
    
    for expert in experts:
        html_body += f"""
            <li>
                <strong>{expert['name']}</strong><br>
                {expert['title']} at {expert['company']}<br>
                Location: {expert['location']}<br>
                <a href="{expert['profile_url']}">LinkedIn Profile</a>
            </li>
            <br>
        """
    
    html_body += """
        </ul>
        
        <p>Please reply to this email with your availability for the next week, and we'll coordinate with these experts.</p>
        
        <p>Best regards,<br>Julie AI</p>
    </body>
    </html>
    """
    
    return send_email(user_email, subject, text_body, html_body)
