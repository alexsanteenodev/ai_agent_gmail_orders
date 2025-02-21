import argparse
import json
from generate_invoice import OrderDetails, create_invoice_pdf

def main():
    parser = argparse.ArgumentParser(description='Generate an invoice PDF from order details')
    parser.add_argument('--order', type=str, required=True, 
                       help='Order details in JSON format or path to JSON file')
    
    args = parser.parse_args()
    
    try:
        # Try to parse as direct JSON string
        order_json = json.loads(args.order)
        order_data = OrderDetails.model_validate(order_json)
        filename = create_invoice_pdf(order_data)  # Use the internal function directly
        print(f"Invoice generated successfully: {filename}")
    except json.JSONDecodeError:
        # If not valid JSON, try to read from file
        try:
            with open(args.order, 'r') as f:
                order_json = json.load(f)
                order_data = OrderDetails.model_validate(order_json)
                filename = create_invoice_pdf(order_data)  # Use the internal function directly
                print(f"Invoice generated successfully: {filename}")
        except:
            print("Error: Please provide valid JSON data or a path to a JSON file")
            exit(1)

if __name__ == "__main__":
    main() 