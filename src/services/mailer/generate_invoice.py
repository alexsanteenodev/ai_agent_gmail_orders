from datetime import datetime
from typing import  List
from pydantic import BaseModel

from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter

from langchain_core.tools import tool

class OrderItem(BaseModel):
    description: str
    quantity: int
    price: float

class OrderDetails(BaseModel):
    customer_name: str
    items: List[OrderItem]

def create_invoice_pdf(order_details: OrderDetails) -> str:
    """Internal function to handle PDF generation logic."""
    filename = f"invoice_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
    c = canvas.Canvas(filename, pagesize=letter)
    
    # Add company header
    c.setFont("Helvetica-Bold", 24)
    c.drawString(50, 750, "Your Company Name")
    
    # Add invoice details
    c.setFont("Helvetica", 12)
    c.drawString(50, 700, f"Invoice Date: {datetime.now().strftime('%Y-%m-%d')}")
    c.drawString(50, 680, f"Invoice #: INV-{datetime.now().strftime('%Y%m%d%H%M')}")
    c.drawString(50, 660, f"Customer: {order_details.customer_name}")
    
    # Add order items
    y = 600
    total = 0
    c.drawString(50, y, "Item Description")
    c.drawString(300, y, "Quantity")
    c.drawString(400, y, "Price")
    c.drawString(500, y, "Total")
    
    y -= 20
    for item in order_details.items:
        c.drawString(50, y, item.description)
        c.drawString(300, y, str(item.quantity))
        c.drawString(400, y, f"${item.price:.2f}")
        item_total = item.quantity * item.price
        c.drawString(500, y, f"${item_total:.2f}")
        total += item_total
        y -= 20
    
    # Add total
    c.drawString(400, y-20, "Total:")
    c.drawString(500, y-20, f"${total:.2f}")
    
    c.save()
    return filename

@tool
def generate_invoice(order_details: OrderDetails) -> str:
    """Generate an invoice PDF for the order."""
    return create_invoice_pdf(order_details)
