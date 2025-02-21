from langchain_core.tools import tool
from dotenv import load_dotenv
import requests
load_dotenv()


@tool
def get_product_price(product_id: str) -> float:
    """Get the price of a product from the product database."""

    # call fake pricing api
    response = requests.get(f"http://localhost:3001/price/{product_id}")
    return response.json()['price']


@tool
def get_api_info() -> dict:
    """Get information about available APIs and their endpoints from the fake pricing API."""
    try:
        response = requests.get("http://localhost:3001/api-info")
        return response.json()
    except requests.RequestException as e:
        return {"error": f"Failed to fetch API info: {str(e)}"}



