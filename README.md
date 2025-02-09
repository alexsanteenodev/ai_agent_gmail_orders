# Email Processing Agent

An AI-powered email processing system that automatically handles customer service emails, processes orders, and generates invoices.

## Features

- Automatic processing of unread emails
- Filtering emails from allowed customers
- AI-powered response generation
- Automatic invoice generation and sending
- Continuous monitoring of inbox

## Setup

1. Install dependencies:

```bash
make install
```

2. Set up Gmail API:

   - Go to [Google Cloud Console](https://console.cloud.google.com)
   - Create a new project or select existing
   - Enable Gmail API
   - Create OAuth 2.0 credentials:
     - Go to "Credentials" > "Create Credentials" > "OAuth Client ID"
     - Choose "Desktop Application"
     - Download JSON file
     - Save as `credentials/credentials.json`

3. Configure environment variables:
   - Copy `.env.example` to `.env`
   - Update variables:

```env
ANTHROPIC_API_KEY=your_api_key_here
ALLOWED_CUSTOMERS=customer1@example.com,customer2@example.com
```

## Directory Structure

```
langgraph/
├── credentials/         # Store API credentials
│   ├── credentials.json # Gmail OAuth credentials
│   └── token.json      # Auto-generated token
├── .env                # Environment variables
└── mailer.py          # Main application
```

## Usage

Run the email processor:

```bash
make run
```

The system will:

1. Check for new unread emails every 10 seconds
2. Process only emails from allowed customers
3. Generate AI responses
4. Create and send invoices when needed

## First Run

On first run:

1. Browser will open for Gmail authentication
2. Log in with your Gmail account
3. Grant required permissions
4. Token will be saved for future use

## Logging

The system provides detailed logging:

- Email processing status
- Unauthorized sender notifications
- Invoice generation and sending
- Error messages

## Error Handling

- Automatic retry on failures
- Detailed error logging
- Continuous operation even after errors
- Token refresh when expired
