import time
from datetime import datetime
from dotenv import load_dotenv

from langchain_anthropic import ChatAnthropic
from langgraph.prebuilt import create_react_agent
from langgraph.checkpoint.memory import MemorySaver
from services.mailer.tools.read_mail import read_emails
from services.mailer.tools.send_mail import send_email
from services.mailer.tools.get_product_price import get_product_price, get_api_info

load_dotenv()

# Initialize the agent
tools = [read_emails, get_product_price, get_api_info, send_email]
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
        
        When processing orders and generating invoices, you MUST format the order_details in this exact structure:
        {
            "customer_name": "Customer's Full Name",
            "items": [
                {
                    "description": "Product Name/Description",
                    "quantity": 1,
                    "price": 1299.99
                }
            ]
        }

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

def run_email_processor(check_interval: int = 5):
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