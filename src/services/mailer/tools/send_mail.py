import os
import base64
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from langchain_core.tools import tool
from datetime import datetime
from typing import Dict, Optional
from dotenv import load_dotenv
from src.services.mailer.utils.invoice.generate_invoice import generate_invoice, OrderDetails, OrderItem
from src.services.mailer.utils.get_gmail_service import get_gmail_service
load_dotenv()


@tool
def send_email(to: str, subject: str, body: str, attach_invoice: Optional[bool] = False, order_details: Optional[Dict] = None) -> str:
    """Send an email with optional invoice attachment."""
    service = get_gmail_service()
    
    message = MIMEMultipart()
    message['to'] = to
    message['subject'] = subject
    
    msg = MIMEText(body
    message.attach(msg)
    
    print(f"[{datetime.now()}] Attaching invoice: {attach_invoice}")
    print(f"[{datetime.now()}] Order details: {order_details}")
    if attach_invoice and order_details:
        # Generate invoice PDF
        print(f"[{datetime.now()}] Generating invoice")
        try:
            # Convert items to OrderItem instances
            items = [OrderItem(**item) for item in order_details.get('items', [])]
            # Create OrderDetails instance
            order_model = OrderDetails(
                customer_name=order_details.get('customer_name'),
                items=items
            )
            invoice_path = generate_invoice(order_model)
            print(f"[{datetime.now()}] Invoice path: {invoice_path}")
            with open(invoice_path, 'rb') as f:
                invoice = MIMEApplication(f.read(), _subtype='pdf')
                invoice.add_header('Content-Disposition', 'attachment', filename='invoice.pdf')
                message.attach(invoice)
                print(f"[{datetime.now()}] Invoice attached to email")
            os.remove(invoice_path)  # Clean up
        except Exception as e:
            print(f"[{datetime.now()}] Error generating invoice: {str(e)}")
    
    raw = base64.urlsafe_b64encode(message.as_bytes()).decode('utf-8')
    service.users().messages().send(userId='me', body={'raw': raw}).execute()
    return "Email sent successfully"


