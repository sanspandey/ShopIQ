"""
Run this script to generate a realistic sample sales Excel file for testing ShopIQ.
    python generate_sample_data.py
"""
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random

random.seed(42)
np.random.seed(42)

PRODUCTS = [
    "Basmati Rice (5kg)", "Toor Dal (1kg)", "Sunflower Oil (1L)",
    "Aashirvaad Atta (10kg)", "Amul Butter (500g)", "Maggi Noodles (70g)",
    "Parle-G Biscuits (800g)", "Colgate Toothpaste (200g)", "Dettol Soap (75g)",
    "Surf Excel (1kg)", "Haldiram Namkeen (200g)", "Kurkure (90g)",
    "Coca Cola (600ml)", "Nescafé Coffee (50g)", "Green Tea (25 bags)",
]

CATEGORIES = {
    "Basmati Rice (5kg)":       "Grains",
    "Toor Dal (1kg)":           "Pulses",
    "Sunflower Oil (1L)":       "Oils",
    "Aashirvaad Atta (10kg)":   "Grains",
    "Amul Butter (500g)":       "Dairy",
    "Maggi Noodles (70g)":      "Snacks",
    "Parle-G Biscuits (800g)":  "Snacks",
    "Colgate Toothpaste (200g)":"Personal Care",
    "Dettol Soap (75g)":        "Personal Care",
    "Surf Excel (1kg)":         "Household",
    "Haldiram Namkeen (200g)":  "Snacks",
    "Kurkure (90g)":            "Snacks",
    "Coca Cola (600ml)":        "Beverages",
    "Nescafé Coffee (50g)":     "Beverages",
    "Green Tea (25 bags)":      "Beverages",
}

PRICES = {
    "Basmati Rice (5kg)":       380,
    "Toor Dal (1kg)":           130,
    "Sunflower Oil (1L)":       140,
    "Aashirvaad Atta (10kg)":   450,
    "Amul Butter (500g)":       260,
    "Maggi Noodles (70g)":      14,
    "Parle-G Biscuits (800g)":  50,
    "Colgate Toothpaste (200g)":80,
    "Dettol Soap (75g)":        40,
    "Surf Excel (1kg)":         130,
    "Haldiram Namkeen (200g)":  50,
    "Kurkure (90g)":            20,
    "Coca Cola (600ml)":        40,
    "Nescafé Coffee (50g)":     120,
    "Green Tea (25 bags)":      90,
}

start_date = datetime(2024, 1, 1)
records = []

for day_offset in range(365):
    date = start_date + timedelta(days=day_offset)
    # More sales on weekends and month-start
    base_orders = 25 if date.weekday() >= 5 else 15
    # Seasonal bump (summer + festival)
    if date.month in [3, 4, 5, 10, 11]:
        base_orders = int(base_orders * 1.3)
    # Slight growth trend over year
    trend_factor = 1 + (day_offset / 365) * 0.2
    n_orders = int(base_orders * trend_factor * np.random.uniform(0.7, 1.3))

    for _ in range(n_orders):
        product = random.choice(PRODUCTS)
        qty     = random.choices([1, 2, 3, 4, 5], weights=[45, 30, 15, 7, 3])[0]
        price   = PRICES[product] * np.random.uniform(0.95, 1.05)
        total   = round(price * qty, 2)

        records.append({
            "Date":        date.strftime("%Y-%m-%d"),
            "Product":     product,
            "Category":    CATEGORIES[product],
            "Quantity":    qty,
            "Unit Price":  round(price, 2),
            "Total Sales": total,
        })

df = pd.DataFrame(records)
df.to_excel("sample_sales_data.xlsx", index=False)
print(f"✅ Generated {len(df):,} sales records → sample_sales_data.xlsx")
print(f"   Date range : {df['Date'].min()} to {df['Date'].max()}")
print(f"   Total sales: ₹{df['Total Sales'].sum():,.0f}")
