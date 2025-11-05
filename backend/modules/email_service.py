import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Email configuration - you can set these via environment variables
SMTP_SERVER = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
SMTP_PORT = int(os.getenv('SMTP_PORT', '587'))
EMAIL_USER = os.getenv('EMAIL_USER', '')
EMAIL_PASSWORD = os.getenv('EMAIL_PASSWORD', '')
FROM_EMAIL = os.getenv('FROM_EMAIL', EMAIL_USER)

def send_email(to_email, subject, body, html_body=None):
    """Send email using SMTP"""
    try:
        # If email credentials are not configured, just log (for development)
        if not EMAIL_USER or not EMAIL_PASSWORD:
            print(f"[EMAIL NOT CONFIGURED] Would send email to {to_email}")
            print(f"Subject: {subject}")
            print(f"Body: {body}")
            if html_body:
                print(f"HTML Body: {html_body}")
            return True
        
        msg = MIMEMultipart('alternative')
        msg['Subject'] = subject
        msg['From'] = FROM_EMAIL
        msg['To'] = to_email
        
        # Add both plain text and HTML versions
        part1 = MIMEText(body, 'plain')
        part2 = MIMEText(html_body or body, 'html')
        
        msg.attach(part1)
        if html_body:
            msg.attach(part2)
        
        # Send email
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(EMAIL_USER, EMAIL_PASSWORD)
            server.send_message(msg)
        
        return True
    except Exception as e:
        print(f"Error sending email: {str(e)}")
        return False

def send_password_create_email(email, first_name, token):
    """Send password creation email"""
    base_url = os.getenv('BASE_URL', 'http://localhost:3000')
    create_password_url = f"{base_url}/create-password?token={token}"
    
    subject = "Create Your Password - Stock Analysis Site"
    body = f"""
Hello {first_name},

Thank you for registering with Stock Analysis Site.

Please click on the link below to create your password:
{create_password_url}

This link will expire in 24 hours.

If you did not register for this account, please ignore this email.

Best regards,
Stock Analysis Team
"""
    
    html_body = f"""
<html>
<body style="font-family: Arial, sans-serif;">
    <h2>Welcome to Stock Analysis Site!</h2>
    <p>Hello {first_name},</p>
    <p>Thank you for registering with Stock Analysis Site.</p>
    <p>Please click on the button below to create your password:</p>
    <p><a href="{create_password_url}" style="background-color: #4CAF50; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px; display: inline-block;">Create Password</a></p>
    <p>Or copy and paste this link into your browser:</p>
    <p><a href="{create_password_url}">{create_password_url}</a></p>
    <p><small>This link will expire in 24 hours.</small></p>
    <p>If you did not register for this account, please ignore this email.</p>
    <p>Best regards,<br>Stock Analysis Team</p>
</body>
</html>
"""
    
    return send_email(email, subject, body, html_body)

def send_password_reset_email(email, first_name, token):
    """Send password reset email"""
    base_url = os.getenv('BASE_URL', 'http://localhost:3000')
    reset_password_url = f"{base_url}/reset-password?token={token}"
    
    subject = "Reset Your Password - Stock Analysis Site"
    body = f"""
Hello {first_name},

You have requested to reset your password for Stock Analysis Site.

Please click on the link below to reset your password:
{reset_password_url}

This link will expire in 24 hours.

If you did not request a password reset, please ignore this email.

Best regards,
Stock Analysis Team
"""
    
    html_body = f"""
<html>
<body style="font-family: Arial, sans-serif;">
    <h2>Password Reset Request</h2>
    <p>Hello {first_name},</p>
    <p>You have requested to reset your password for Stock Analysis Site.</p>
    <p>Please click on the button below to reset your password:</p>
    <p><a href="{reset_password_url}" style="background-color: #4CAF50; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px; display: inline-block;">Reset Password</a></p>
    <p>Or copy and paste this link into your browser:</p>
    <p><a href="{reset_password_url}">{reset_password_url}</a></p>
    <p><small>This link will expire in 24 hours.</small></p>
    <p>If you did not request a password reset, please ignore this email.</p>
    <p>Best regards,<br>Stock Analysis Team</p>
</body>
</html>
"""
    
    return send_email(email, subject, body, html_body)

