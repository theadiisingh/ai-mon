"""
Email service for sending notifications.
"""
from typing import Optional, List
import aiosmtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings


class EmailService:
    """Service for sending email notifications."""
    
    def __init__(self):
        self.smtp_host = settings.smtp_host
        self.smtp_port = settings.smtp_port
        self.smtp_user = settings.smtp_user
        self.smtp_password = settings.smtp_password
        self.email_from = settings.email_from
    
    async def send_email(
        self,
        to_email: str,
        subject: str,
        body: str,
        html: Optional[str] = None
    ) -> bool:
        """Send an email."""
        if not self.smtp_user or not self.smtp_password:
            # Email not configured, skip sending
            return False
        
        try:
            message = MIMEMultipart("alternative")
            message["Subject"] = subject
            message["From"] = self.email_from
            message["To"] = to_email
            
            # Add plain text version
            text_part = MIMEText(body, "plain")
            message.attach(text_part)
            
            # Add HTML version if provided
            if html:
                html_part = MIMEText(html, "html")
                message.attach(html_part)
            
            await aiosmtplib.send(
                message,
                hostname=self.smtp_host,
                port=self.smtp_port,
                username=self.smtp_user,
                password=self.smtp_password,
                start_tls=True
            )
            
            return True
        except Exception as e:
            print(f"Failed to send email: {e}")
            return False
    
    async def send_api_down_notification(
        self,
        to_email: str,
        api_name: str,
        api_url: str,
        error_message: str,
        failure_count: int
    ) -> bool:
        """Send notification when an API goes down."""
        subject = f"🔴 Alert: {api_name} is Down"
        
        body = f"""
Hello,

Your API "{api_name}" ({api_url}) is experiencing issues.

Details:
- Error: {error_message}
- Consecutive Failures: {failure_count}

Please check your dashboard for more details.

Best regards,
AI MON Team
"""
        
        html = f"""
<!DOCTYPE html>
<html>
<head>
    <style>
        body {{ font-family: Arial, sans-serif; line-height: 1.6; }}
        .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
        .alert {{ background-color: #fee; border-left: 4px solid #c00; padding: 15px; margin: 20px 0; }}
        .details {{ background-color: #f5f5f5; padding: 15px; border-radius: 5px; }}
    </style>
</head>
<body>
    <div class="container">
        <h2>🔴 API Down Alert</h2>
        <p>Hello,</p>
        <p>Your API <strong>{api_name}</strong> ({api_url}) is experiencing issues.</p>
        
        <div class="alert">
            <strong>Alert:</strong> Your API has failed {failure_count} consecutive checks.
        </div>
        
        <div class="details">
            <p><strong>Error:</strong> {error_message}</p>
            <p><strong>URL:</strong> {api_url}</p>
        </div>
        
        <p>Please check your AI MON dashboard for more details and insights.</p>
        
        <p>Best regards,<br>AI MON Team</p>
    </div>
</body>
</html>
"""
        
        return await self.send_email(to_email, subject, body, html)
    
    async def send_api_recovered_notification(
        self,
        to_email: str,
        api_name: str,
        api_url: str,
        downtime_minutes: int
    ) -> bool:
        """Send notification when an API recovers."""
        subject = f"✅ Recovered: {api_name} is Back Up"
        
        body = f"""
Hello,

Great news! Your API "{api_name}" ({api_url}) has recovered.

Details:
- Downtime: ~{downtime_minutes} minutes

Best regards,
AI MON Team
"""
        
        html = f"""
<!DOCTYPE html>
<html>
<head>
    <style>
        body {{ font-family: Arial, sans-serif; line-height: 1.6; }}
        .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
        .success {{ background-color: #efe; border-left: 4px solid #0c0; padding: 15px; margin: 20px 0; }}
    </style>
</head>
<body>
    <div class="container">
        <h2>✅ API Recovered</h2>
        <p>Hello,</p>
        <p>Great news! Your API <strong>{api_name}</strong> ({api_url}) has recovered.</p>
        
        <div class="success">
            <strong>Downtime:</strong> approximately {downtime_minutes} minutes
        </div>
        
        <p>Best regards,<br>AI MON Team</p>
    </div>
</body>
</html>
"""
        
        return await self.send_email(to_email, subject, body, html)
    
    async def send_anomaly_detected_notification(
        self,
        to_email: str,
        api_name: str,
        api_url: str,
        anomaly_type: str,
        details: str
    ) -> bool:
        """Send notification when an anomaly is detected."""
        subject = f"⚠️ Anomaly Detected: {api_name}"
        
        body = f"""
Hello,

An anomaly has been detected for your API "{api_name}" ({api_url}).

Details:
- Type: {anomaly_type}
- Details: {details}

Best regards,
AI MON Team
"""
        
        html = f"""
<!DOCTYPE html>
<html>
<head>
    <style>
        body {{ font-family: Arial, sans-serif; line-height: 1.6; }}
        .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
        .warning {{ background-color: #ffc; border-left: 4px solid #cc0; padding: 15px; margin: 20px 0; }}
    </style>
</head>
<body>
    <div class="container">
        <h2>⚠️ Anomaly Detected</h2>
        <p>Hello,</p>
        <p>An anomaly has been detected for your API <strong>{api_name}</strong> ({api_url}).</p>
        
        <div class="warning">
            <p><strong>Type:</strong> {anomaly_type}</p>
            <p><strong>Details:</strong> {details}</p>
        </div>
        
        <p>Please check your AI MON dashboard for more details and AI-generated insights.</p>
        
        <p>Best regards,<br>AI MON Team</p>
    </div>
</body>
</html>
"""
        
        return await self.send_email(to_email, subject, body, html)
    
    async def send_welcome_email(
        self,
        to_email: str,
        username: str
    ) -> bool:
        """Send welcome email to new users."""
        subject = "Welcome to AI MON - Smart API Monitoring"
        
        body = f"""
Hello {username},

Welcome to AI MON! We're excited to have you on board.

AI MON helps you monitor your APIs in real-time, detect failures, and get AI-powered insights to debug issues quickly.

Getting Started:
1. Add your first API endpoint
2. Configure monitoring intervals
3. View real-time metrics on your dashboard

If you need any help, don't hesitate to reach out.

Best regards,
AI MON Team
"""
        
        html = f"""
<!DOCTYPE html>
<html>
<head>
    <style>
        body {{ font-family: Arial, sans-serif; line-height: 1.6; }}
        .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
        .btn {{ background-color: #007bff; color: white; padding: 12px 24px; text-decoration: none; border-radius: 5px; display: inline-block; }}
    </style>
</head>
<body>
    <div class="container">
        <h2>Welcome to AI MON! 🎉</h2>
        <p>Hello {username},</p>
        <p>Welcome to AI MON! We're excited to have you on board.</p>
        
        <p>AI MON helps you monitor your APIs in real-time, detect failures, and get AI-powered insights to debug issues quickly.</p>
        
        <h3>Getting Started:</h3>
        <ol>
            <li>Add your first API endpoint</li>
            <li>Configure monitoring intervals</li>
            <li>View real-time metrics on your dashboard</li>
        </ol>
        
        <p>If you need any help, don't hesitate to reach out.</p>
        
        <p>Best regards,<br>AI MON Team</p>
    </div>
</body>
</html>
"""
        
        return await self.send_email(to_email, subject, body, html)
