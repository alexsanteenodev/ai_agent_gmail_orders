import os
from datetime import datetime
from typing import Dict, List
from dotenv import load_dotenv
from langchain_core.tools import tool
from services.mailer.utils.get_gmail_service import get_gmail_service
load_dotenv()


# Allowed customers configuration
ALLOWED_CUSTOMERS = os.getenv('ALLOWED_CUSTOMERS').split(',')

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
