from enum import Enum
from typing import Dict

class AppleProduct(str, Enum):
    IPHONE_15 = "iphone_15"
    IPHONE_15_PRO = "iphone_15_pro"
    IPHONE_15_PRO_MAX = "iphone_15_pro_max"
    MACBOOK_AIR_13 = "macbook_air_13"
    MACBOOK_AIR_15 = "macbook_air_15"
    MACBOOK_PRO_14 = "macbook_pro_14"
    MACBOOK_PRO_16 = "macbook_pro_16"
    IPAD_AIR = "ipad_air"
    IPAD_PRO = "ipad_pro"
    AIRPODS_PRO = "airpods_pro"
    APPLE_WATCH_SERIES_9 = "apple_watch_series_9"

# Fixed prices for Apple products
APPLE_PRODUCT_PRICES: Dict[AppleProduct, float] = {
    AppleProduct.IPHONE_15: 799.00,
    AppleProduct.IPHONE_15_PRO: 999.00,
    AppleProduct.IPHONE_15_PRO_MAX: 1199.00,
    AppleProduct.MACBOOK_AIR_13: 999.00,
    AppleProduct.MACBOOK_AIR_15: 1299.00,
    AppleProduct.MACBOOK_PRO_14: 1599.00,
    AppleProduct.MACBOOK_PRO_16: 2499.00,
    AppleProduct.IPAD_AIR: 599.00,
    AppleProduct.IPAD_PRO: 799.00,
    AppleProduct.AIRPODS_PRO: 249.00,
    AppleProduct.APPLE_WATCH_SERIES_9: 399.00
}
