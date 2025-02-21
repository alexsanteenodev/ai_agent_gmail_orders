import os
from googleapiclient.discovery import build, Resource
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow

# Gmail API setup
SCOPES = ['https://www.googleapis.com/auth/gmail.modify']

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
