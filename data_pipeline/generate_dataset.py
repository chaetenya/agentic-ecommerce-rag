import pandas as pd
import os

def generate_ecommerce_data():
    data_dir = os.path.join(os.path.dirname(__file__), 'raw_data')
    os.makedirs(data_dir, exist_ok=True)
    
    print(f"Creating dataset in: {data_dir}")

    products = [
        {"product_id": "P001", "name": "Sony WH-1000XM4", "category": "Electronics", "brand": "Sony", "price": 298.00, "specs": "Noise cancelling, 30hr battery, over-ear", "avg_rating": 4.8},
        {"product_id": "P002", "name": "Bose QuietComfort 45", "category": "Electronics", "brand": "Bose", "price": 329.00, "specs": "Noise cancelling, 24hr battery, over-ear", "avg_rating": 4.7},
        {"product_id": "P003", "name": "Apple AirPods Pro 2", "category": "Electronics", "brand": "Apple", "price": 249.00, "specs": "Active noise cancellation, spatial audio, in-ear", "avg_rating": 4.9},
        {"product_id": "P004", "name": "Logitech MX Master 3S", "category": "Peripherals", "brand": "Logitech", "price": 99.99, "specs": "Ergonomic, 8000 DPI, multi-device", "avg_rating": 4.8},
        {"product_id": "P005", "name": "Razer DeathAdder V3", "category": "Peripherals", "brand": "Razer", "price": 69.99, "specs": "Wired, 30K DPI, lightweight gaming", "avg_rating": 4.6},
        {"product_id": "G001", "name": "Organic Avocados (Pack of 4)", "category": "Groceries", "brand": "FreshFarms", "price": 5.99, "specs": "Fresh, locally sourced, organic", "avg_rating": 4.2},
    ]
    
    df = pd.DataFrame(products)
    csv_path = os.path.join(data_dir, "product_catalog.csv")
    df.to_csv(csv_path, index=False)
    print(f"Created structured product catalog: {csv_path}")

    # 3. Generating Unstructured Data (The Vector DB Documents)
    policies = """
# QuickCart E-Commerce Policies

## 1. Return & Refund Policy
- **Electronics & Peripherals:** Items can be returned within 14 days of delivery. If the original packaging is opened, a 15% restocking fee applies. Defective items are exempt from the restocking fee and can be returned within 30 days.
- **Groceries & Perishables:** No returns are accepted for food items. If an item arrives spoiled or damaged, a full refund will be issued if reported within 24 hours of delivery.

## 2. Shipping & Delivery SLAs
- **Standard Shipping:** 3-5 business days. Free for orders over $50.
- **Quick-Commerce Express:** Delivery within 2 hours for eligible local grocery items. Costs a flat $4.99 fee.

## 3. Warranty Information
- All Apple products are covered by a 1-year limited manufacturer warranty.
- Sony and Bose headphones include a 1-year warranty covering internal hardware defects. Accidental water damage is not covered.
"""
    
    txt_path = os.path.join(data_dir, "company_policies.txt")
    with open(txt_path, "w", encoding="utf-8") as f:
        f.write(policies)
    print(f"Created unstructured policy document: {txt_path}")

if __name__ == "__main__":
    generate_ecommerce_data()