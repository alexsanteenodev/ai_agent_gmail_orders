from fastapi import FastAPI
from typing import List, Dict
import uvicorn
from pydantic import BaseModel
from models.product_types import AppleProduct, APPLE_PRODUCT_PRICES

app = FastAPI(title="Apple Products Pricing API")

class PriceResponse(BaseModel):
    product_id: AppleProduct
    price: float
    currency: str = "USD"

class ApiInfoResponse(BaseModel):
    available_products: List[str]
    endpoints: Dict[str, str]
    version: str = "1.0.0"

@app.get("/api-info", response_model=ApiInfoResponse)
async def get_api_info():
    """Get information about available APIs and their endpoints."""
    return ApiInfoResponse(
        available_products=list(AppleProduct.__members__.keys()),
        endpoints={
            "get_price": "/price/{product_id}",
            "get_api_info": "/api-info"
        }
    )

@app.get("/price/{product_id}", response_model=PriceResponse)
async def get_price(product_id: AppleProduct):
    return PriceResponse(
        product_id=product_id,
        price=APPLE_PRODUCT_PRICES[product_id]
    )

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=3001)
