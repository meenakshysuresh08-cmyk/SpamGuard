#!/usr/bin/env python
"""Generate PDF versions of phishing email samples."""

from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas
import os

def create_pdf(text_content, filename):
    """Create a PDF from text content."""
    c = canvas.Canvas(filename, pagesize=letter)
    width, height = letter
    
    # Title
    c.setFont("Helvetica-Bold", 16)
    c.drawString(1*inch, height - 1*inch, "Phishing Email Sample")
    
    # Date
    from datetime import datetime
    c.setFont("Helvetica", 10)
    c.drawString(1*inch, height - 1.3*inch, f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Content box
    y_pos = height - 1.8*inch
    
    # Split text into lines and draw
    lines = text_content.split('\n')
    c.setFont("Courier", 10)
    
    for line in lines:
        # Wrap long lines
        words = line.split()
        current_line = ""
        
        for word in words:
            test_line = current_line + word + " "
            if c.stringWidth(test_line, "Courier", 10) < width - 2*inch:
                current_line = test_line
            else:
                c.drawString(1*inch, y_pos, current_line)
                y_pos -= 0.18*inch
                current_line = word + " "
        
        if current_line:
            c.drawString(1*inch, y_pos, current_line)
            y_pos -= 0.18*inch
        
        # Add space between paragraphs
        if line.strip() == "":
            y_pos -= 0.1*inch
        
        # Check if we need a new page
        if y_pos < 1*inch:
            c.showPage()
            c.setFont("Courier", 10)
            y_pos = height - 1*inch
    
    c.save()
    print(f"Created: {filename}")

def main():
    # Create sample emails directory for PDFs
    pdf_dir = "sample_emails/pdf"
    os.makedirs(pdf_dir, exist_ok=True)
    
    # Email 1
    email1 = """Subject: URGENT: Account Verification Required - Action Needed Within 24 Hours!

Dear Valued Customer,

URGENT: Your account has been temporarily suspended due to suspicious activity!

We detected unusual login attempts from a new device at IP address 192.168.1.100.
IMMEDIATELY verify your identity to restore access!

CLICK HERE: https://account-verify-secure.xyz/login

Your OTP is: 847291

DO NOT share this code with anyone!

Failure to verify within 24 hours will result in permanent account deletion.

Sincerely,
Security Team
SecureBank Support
"""
    
    # Email 2
    email2 = """Subject: You've Won $500,000! Claim Your Prize Now!

CONGRATULATIONS!

You have been selected as the lucky winner of our International Sweepstakes!
You will receive $500,000 USD - NO PURCHASE NECESSARY!

TO CLAIM YOUR PRIZE:
1. Click: https://prize-claim-lottery.top/verify
2. Complete the verification form
3. Pay processing fee of $50 via PayPal or Western Union

This offer expires in 48 HOURS! ACT NOW!

Don't miss your chance to become a millionaire!

Best regards,
International Lottery Claims Office
Free Entry - Winner Selected Randomly
"""
    
    # Email 3
    email3 = """Subject: Immediate Action: Password Reset Required for Security

Your password is about to expire. Reset now to avoid account lockout!

URGENT: Your account password will expire in 2 hours!
To prevent unauthorized access, please reset immediately.

Click here: https://password-reset-secure.com/reset

You will need to enter your current password and create a new one.
For security, we'll also verify your SSN and credit card on file.

If you don't reset, your account will be permanently suspended.

Security Team
SecureAccount Services
"""
    
    create_pdf(email1, f"{pdf_dir}/phishing_001.pdf")
    create_pdf(email2, f"{pdf_dir}/phishing_002.pdf")
    create_pdf(email3, f"{pdf_dir}/phishing_003.pdf")
    
    print("\nAll PDFs generated successfully!")
    print(f"Location: {os.path.abspath(pdf_dir)}/")

if __name__ == "__main__":
    main()
