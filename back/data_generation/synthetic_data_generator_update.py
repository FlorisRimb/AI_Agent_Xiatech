import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random

# =====================================================
# CONFIG
# =====================================================
AVG_ORDERS_PER_DAY = 160
MAX_ITEMS_PER_ORDER = 3
TRENDING_SKU_COUNT = (3, 6)       # anomaly count
TREND_MULTIPLIER = (3, 10)        # sales boost multiplier
np.random.seed(42)
random.seed(42)

# =====================================================
# 1. Product Catalogue (More realistic)
# =====================================================
categories = {
    "Men": [
        ("Athletic Running Shoes", "Breathable mesh upper with cushioned EVA sole"),
        ("Slim Fit Jeans", "Denim stretch fabric with tapered leg"),
        ("Oversized Hoodie", "Heavyweight cotton fleece, kangaroo pocket"),
        ("Lightweight Windbreaker", "Water-resistant jacket with packable hood"),
        ("Polo Shirt", "Organic cotton pique polo with 3-button collar"),
        ("Cargo Joggers", "Elastic waist cotton joggers with utility pockets"),
        ("Padded Winter Coat", "Quilted synthetic insulation with storm cuffs"),
        ("Basic Tee Pack (3)", "Soft-touch classic crew neck t-shirts"),
    ],
    "Women": [
        ("Yoga Leggings", "High-rise seamless stretch fabric"),
        ("Sports Bra", "Medium support, moisture-wicking nylon"),
        ("Midi Dress", "Floral printed viscose with wrap silhouette"),
        ("Denim Jacket", "Classic stone-washed denim, metal buttons"),
        ("Tailored Blazer", "Lapel collar, premium structured fit"),
        ("Athleisure Set", "Leggings + cropped top matching set"),
        ("Oversized Knit Sweater", "Wool blend cable knit pullover"),
        ("High-Waisted Jeans", "Blue stretch denim, sculpting fit"),
    ],
    "Kids": [
        ("Graphic T-Shirt", "Organic cotton with cartoon print"),
        ("School Hoodie", "Soft fleece, embroidered logo"),
        ("Waterproof Raincoat", "Reflective strips, detachable hood"),
        ("Cargo Shorts", "Durable cotton, side pockets"),
        ("Sneaker Boots", "Hybrid sneaker boot, anti-slip sole"),
        ("Pyjama Set", "Cotton long-sleeve + trousers"),
        ("Soft Plush Jacket", "Faux-fur fleece zip hoodie"),
        ("Summer Dress", "Lightweight cotton floral"),
    ],
    "Footwear": [
        ("Running Trainers", "Foam midsole, breathable mesh upper"),
        ("Basketball Shoes", "High-top ankle support, rubber outsole"),
        ("Slip-On Sneakers", "Ultra-light EVA slides, city casual"),
        ("Leather Business Shoes", "Hand-stitched oxfords, polished"),
        ("Court Sneakers", "Classic retro tennis sneaker"),
        ("Trail Hiking Boots", "Waterproof membrane, Vibram sole"),
        ("Platform Street Shoes", "Chunky platform lifestyle shoe"),
        ("Rain Boots", "Flexible PVC, reinforced toe"),
    ],
    "Accessories": [
        ("Wool Beanie", "Rib-knit design, one size fits most"),
        ("Sports Cap", "Adjustable strap, breathable mesh back"),
        ("Winter Gloves", "Touchscreen fingertips, fleece lining"),
        ("Ski Scarf", "Thermal knit scarf, machine washable"),
        ("Leather Belt", "Genuine hide, matte buckle"),
        ("Sports Socks Pack (6)", "Cushion-heel athletic socks"),
        ("Crossbody Bag", "Minimal sling bag, waterproof zip"),
        ("Running Headband", "Moisture-wicking elastic band"),
    ],
}
NUM_PRODUCTS = sum(len(categories[x]) for x in categories)


# Collect products (flatten categories)
def generate_products() :
    product_rows = []
    sku_counter = 1

    for cat, items in categories.items():
        for (name, desc) in items:
            product_rows.append({
                "sku": f"SKU-{sku_counter:04d}",
                "name": name,
                "category": cat,
                "description": desc,
                "price": round(np.random.uniform(7, 450), 2),
            })
            sku_counter += 1

    # If < NUM_PRODUCTS → repeat until filled
    while len(product_rows) < NUM_PRODUCTS:
        product_rows += product_rows

    product_rows = product_rows[:NUM_PRODUCTS]
    products_df = pd.DataFrame(product_rows)

    return products_df


# =====================================================
# 2. Supplier table + SKU → Supplier mapping
# =====================================================
supplier_pool = [
    ("SUP-A001", "Asia Logistics", 6),
    ("SUP-A002", "Northern Supply Group", 3),
    ("SUP-A003", "FastLane Imports", 2),
    ("SUP-A004", "Retail Partner Hub", 5),
    ("SUP-A005", "Euro Fashion Trade", 8),
]

def generate_supplier_mapping(products_df : pd.DataFrame) :
    # Create SKU → Supplier dataset
    sku_supplier_rows = []
    for sku in products_df["sku"]:
        supplier = random.choice(supplier_pool)
        sku_supplier_rows.append({
            "sku": sku,
            "supplier_id": supplier[0],
            "supplier_name": supplier[1],
            "po_lead_days": supplier[2]
        })

    sku_supplier_df = pd.DataFrame(sku_supplier_rows)

    return sku_supplier_df


# =====================================================
# 3. Trending SKU anomaly
# =====================================================
products_df = generate_products()

trending_skus = random.sample(
    list(products_df["sku"]),
    random.randint(*TRENDING_SKU_COUNT)
)

trending_multiplier_map = {
    sku: random.randint(*TREND_MULTIPLIER)
    for sku in trending_skus
}


# =====================================================
# 4. Sales transactions
# =====================================================

def gen_qty(sku):
    if sku in trending_multiplier_map:
        base = np.random.randint(2, 6)
        return base * trending_multiplier_map[sku]
    return np.random.randint(1, 5)

def generate_sales(products_df : pd.DataFrame) :

    yesterday = datetime.now() - timedelta(days=1)
    sales_records = []
    order_counter = 10000


    for _ in range(AVG_ORDERS_PER_DAY):
        order_skus = random.sample(
            list(products_df["sku"]),
            k=random.randint(1, MAX_ITEMS_PER_ORDER)
        )

        t = yesterday + timedelta(
            seconds=random.randint(1, 24 * 60 * 60)
        )

        for sku in order_skus:
            order_counter += 1
            oid = f"ORDER-{order_counter}"

            sales_records.append({
                "transaction_id": oid,
                "sku": sku,
                "timestamp": t.strftime("%Y-%m-%d %H:%M:%S"),
                "quantity": gen_qty(sku)
            })

    sales_df = pd.DataFrame(sales_records)

    return sales_df


# =====================================================
# 5. Inventory snapshot
# =====================================================

def generate_inventory(products_df : pd.DataFrame) :

    stock_df = pd.DataFrame({
        "sku": products_df["sku"],
        "stock_on_hand": np.random.randint(50, 900, NUM_PRODUCTS)
    })

    return stock_df

def generate_synthetic_data() :
    products_df = generate_products()
    sales_df = generate_sales(products_df)
    stock_df = generate_inventory(products_df)
    sku_supplier_df = generate_supplier_mapping(products_df)

    return products_df, sales_df, stock_df, sku_supplier_df



# ------------------------------
# PREVIEW OUTPUT
# ------------------------------

if __name__ == '__main__' :

    products_df, sales_df, stock_df, sku_supplier_df = generate_synthetic_data()

    print("\n PRODUCTS")
    print(products_df.head())

    print("\n SAMPLE SALES")
    print(sales_df.head(10))

    print("\n STOCK")
    print(stock_df.head())

    print("\n SKU → SUPPLIER")
    print(sku_supplier_df.head())