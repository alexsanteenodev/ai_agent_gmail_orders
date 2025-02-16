from typing import Dict, Literal

AppleProduct = Literal[
    "iphone_15",
    "iphone_15_pro",
    "iphone_15_pro_max",
    "macbook_air_13",
    "macbook_air_15",
    "macbook_pro_14",
    "macbook_pro_16",
    "ipad_air",
    "ipad_pro",
    "airpods_pro",
    "apple_watch_series_9"
]

# Fixed prices for Apple products
APPLE_PRODUCT_PRICES: Dict[str, float] = {
    "iphone_15": 799.00,
    "iphone_15_pro": 999.00,
    "iphone_15_pro_max": 1199.00,
    "macbook_air_13": 999.00,
    "macbook_air_15": 1299.00,
    "macbook_pro_14": 1599.00,
    "macbook_pro_16": 2499.00,
    "ipad_air": 599.00,
    "ipad_pro": 799.00,
    "airpods_pro": 249.00,
    "apple_watch_series_9": 399.00
}
