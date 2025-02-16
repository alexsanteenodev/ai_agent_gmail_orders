from fastapi import FastAPI
from typing import List
import uvicorn
from pydantic import BaseModel
from types.product_types import AppleProduct, APPLE_PRODUCT_PRICES

app = FastAPI(title="Apple Products Pricing API")

class PriceResponse(BaseModel):
    product_id: AppleProduct
    price: float
    currency: str = "USD"

class BulkPriceRequest(BaseModel):
    product_ids: List[AppleProduct]

@app.get("/")
async def root():
    return {"message": "Welcome to the Apple Products Pricing API"}

@app.get("/price/{product_id}", response_model=PriceResponse)
async def get_price(product_id: AppleProduct):
    return PriceResponse(
        product_id=product_id,
        price=APPLE_PRODUCT_PRICES[product_id]
    )

@app.post("/bulk-prices")
async def get_bulk_prices(request: BulkPriceRequest):
    return [
        PriceResponse(
            product_id=product_id,
            price=APPLE_PRODUCT_PRICES[product_id]
        )
        for product_id in request.product_ids
    ]

@app.get("/products")
async def list_products():
    return [
        {"product_id": product.value, "price": APPLE_PRODUCT_PRICES[product]}
        for product in AppleProduct
    ]

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=3001)
