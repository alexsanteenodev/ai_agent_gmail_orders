import os
import base64
import time
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from datetime import datetime
from typing import Dict, List, Optional
from dotenv import load_dotenv
from services.mailer.generate_invoice import generate_invoice

from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build, Resource

from langchain_anthropic import ChatAnthropic
from langchain_core.tools import tool
from langgraph.prebuilt import create_react_agent
from langgraph.checkpoint.memory import MemorySaver
load_dotenv()

# Gmail API setup
SCOPES = ['https://www.googleapis.com/auth/gmail.modify']

# Allowed customers configuration
ALLOWED_CUSTOMERS = os.getenv('ALLOWED_CUSTOMERS').split(',')

# Type ignore for Gmail API dynamic methods
# pylint: disable=no-member
def get_gmail_service() -> Resource:
    """Get Gmail service using simple OAuth."""
    try:
        token_path = 'credentials/token.json'
        creds_path = 'credentials/credentials.json'
        # Look for existing token
        if os.path.exists(token_path):
            creds = Credentials.from_authorized_user_file(token_path, SCOPES)
            if not creds.expired:
                return build('gmail', 'v1', credentials=creds)
            
        # Check for client secrets file
        if not os.path.exists(creds_path):
            raise FileNotFoundError(
                "\n1. Go to https://console.cloud.google.com"
                "\n2. Create Project (or select existing)"
                "\n3. Enable Gmail API"
                "\n4. Create Credentials > OAuth Client ID > Desktop App"
                "\n5. Download JSON and save as 'credentials.json' in this folder"
            )
        
        # Start OAuth flow
        flow = InstalledAppFlow.from_client_secrets_file(creds_path, SCOPES)
        creds = flow.run_local_server(port=0)
       
        # Save token for next time
        with open(token_path, 'w') as token:
            token.write(creds.to_json())
            
        return build('gmail', 'v1', credentials=creds)
        
    except Exception as e:
        print(f"\nError: {str(e)}")
        if isinstance(e, FileNotFoundError):
            print("\nFollow the setup instructions above to get started!")
        raise

# Tools for the agent
@tool
def read_emails() -> List[Dict]:
    """Read unread emails from Gmail inbox."""
    try:
        print(f"[{datetime.now()}] Attempting to read emails...")
        service = get_gmail_service()
        results = service.users().messages().list(userId='me', labelIds=['INBOX', 'UNREAD']).execute()
        messages = results.get('messages', [])
        
        print(f"[{datetime.now()}] Found {len(messages)} unread messages")
        emails = []
        for message in messages:
            try:
                msg = service.users().messages().get(userId='me', id=message['id']).execute()
                headers = msg['payload']['headers']
                subject = next(h['value'] for h in headers if h['name'] == 'Subject')
                sender = next(h['value'] for h in headers if h['name'] == 'From')
                
                # Extract email address from sender (handles "Name <email@example.com>" format)
                sender_email = sender.split('<')[-1].split('>')[0] if '<' in sender else sender
                
                # Check if sender is in allowed list
                if sender_email not in ALLOWED_CUSTOMERS:
                    print(f"[{datetime.now()}] Skipping email from unauthorized sender: {sender_email}")
                    continue
                
                # Mark as read
                service.users().messages().modify(
                    userId='me', 
                    id=message['id'],
                    body={'removeLabelIds': ['UNREAD']}
                ).execute()
                
                emails.append({
                    'id': message['id'],
                    'subject': subject,
                    'from': sender,
                    'sender_email': sender_email,
                    'snippet': msg['snippet']
                })
                print(f"[{datetime.now()}] Processed email from allowed sender: {sender_email}")
            except Exception as e:
                print(f"[{datetime.now()}] Error processing individual email: {str(e)}")
                continue
        
        return emails
    except Exception as e:
        print(f"[{datetime.now()}] Error in read_emails: {str(e)}")
        raise

@tool
def send_email(to: str, subject: str, body: str, attach_invoice: Optional[bool] = False, order_details: Optional[Dict] = None) -> str:
    """Send an email with optional invoice attachment."""
    service = get_gmail_service()
    
    message = MIMEMultipart()
    message['to'] = to
    message['subject'] = subject
    
    msg = MIMEText(body)
    message.attach(msg)
    
    if attach_invoice and order_details:
        # Generate invoice PDF
        invoice_path = generate_invoice(order_details)
        with open(invoice_path, 'rb') as f:
            invoice = MIMEApplication(f.read(), _subtype='pdf')
            invoice.add_header('Content-Disposition', 'attachment', filename='invoice.pdf')
            message.attach(invoice)
            print(f"[{datetime.now()}] Invoice attached to email")
        os.remove(invoice_path)  # Clean up
    
    raw = base64.urlsafe_b64encode(message.as_bytes()).decode('utf-8')
    service.users().messages().send(userId='me', body={'raw': raw}).execute()
    return "Email sent successfully"



# Initialize the agent
tools = [read_emails, send_email, generate_invoice]
model = ChatAnthropic(
    model="claude-3-5-sonnet-latest",
    temperature=0,
    model_kwargs={
        "system": """You are an AI assistant that handles customer service emails.
        Your responsibilities include:
        1. Reading and understanding customer inquiries
        2. Processing orders and confirming details
        3. Generating and sending invoices when orders are confirmed
        4. Responding professionally to customer questions
        
        Always maintain a professional tone and ensure all order details are correct before processing."""
    }
)

# Initialize memory to persist state between graph runs
checkpointer = MemorySaver()

app = create_react_agent(model, tools, checkpointer=checkpointer)

def process_emails():
    """Main function to process incoming emails."""
    try:
        final_state = app.invoke(
            {"messages": [{"role": "user", "content": "Please check for new emails and process any orders or inquiries."}]},
            config={"configurable": {"thread_id": "email_processor"}}
        )
        print(f"[{datetime.now()}] {final_state['messages'][-1].content}")
        return final_state["messages"][-1].content
    except Exception as e:
        print(f"[{datetime.now()}] Error processing emails: {e}")
        return None

def run_email_processor(check_interval: int = 10):  # 10 seconds
    """Run the email processor as a continuous job."""
    print(f"[{datetime.now()}] Starting email processor job...")
    print("Checking for new emails every", check_interval, "seconds")
    
    while True:
        try:
            process_emails()
            print(f"[{datetime.now()}] Email processor job completed successfully")
            time.sleep(check_interval)
        except Exception as e:
            print(f"[{datetime.now()}] Error in job: {e}")
            time.sleep(check_interval)
        time.sleep(check_interval)

if __name__ == "__main__":
    run_email_processor()