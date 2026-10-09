
import pandas as pd
import numpy as np

np.random.seed(42)

# -----------------------------
# Create realistic retail data
# -----------------------------

n = 5000

categories = [
    "Beverages", "Food", "Furniture",
    "Patisserie", "Butchers",
    "Stationery", "Electronics"
]

items = {
    "Beverages": ["Coffee", "Tea", "Juice", "Soda", "Water"],
    "Food": ["Bread", "Rice", "Pasta", "Cereal", "Cooking Oil"],
    "Furniture": ["Chair", "Table", "Desk", "Shelf", "Cabinet"],
    "Patisserie": ["Cake", "Croissant", "Muffin", "Doughnut", "Pie"],
    "Butchers": ["Beef", "Chicken", "Pork", "Sausage", "Lamb"],
    "Stationery": ["Notebook", "Pen", "Marker", "Folder", "Stapler"],
    "Electronics": ["Mouse", "Keyboard", "Headphones", "USB Cable", "Charger"]
}

prices = {
    "Beverages": [2.5, 3.5, 4, 2, 1.5],
    "Food": [3, 5.5, 4.5, 6, 8],
    "Furniture": [35, 80, 120, 55, 95],
    "Patisserie": [18, 5, 4.5, 3.5, 12],
    "Butchers": [14, 9, 12, 7.5, 16],
    "Stationery": [4, 1.5, 2.5, 3, 6],
    "Electronics": [18, 35, 22, 8, 25]
}

rows = []

for _ in range(n):

    category = np.random.choice(categories)

    item_number = np.random.randint(5)

    item = items[category][item_number]

    price = prices[category][item_number]

    quantity = np.random.randint(1, 11)

    total = round(price * quantity, 2)

    rows.append([
        f"TXN_{np.random.randint(1000000, 9999999)}",
        f"CUST_{np.random.randint(1, 501):03d}",
        category,
        item,
        price,
        quantity,
        total,
        np.random.choice([
            "Cash",
            "Credit Card",
            "Digital Wallet",
            "Mobile Money"
        ]),
        np.random.choice([
            "In-store",
            "Online"
        ]),
        pd.Timestamp("2022-01-01")
        + pd.Timedelta(days=int(np.random.randint(1095))),
        np.random.choice(
            [True, False, np.nan],
            p=[0.18, 0.57, 0.25]
        )
    ])


df = pd.DataFrame(
    rows,
    columns=[
        "Transaction ID",
        "Customer ID",
        "Category",
        "Item",
        "Price Per Unit",
        "Quantity",
        "Total Spent",
        "Payment Method",
        "Location",
        "Transaction Date",
        "Discount Applied"
    ]
)


# -----------------------------
# ADD DATA QUALITY PROBLEMS
# -----------------------------

# Missing values

for column, count in [
    ("Item", 100),
    ("Price Per Unit", 75),
    ("Quantity", 60),
    ("Payment Method", 125),
    ("Location", 90)
]:

    indexes = np.random.choice(
        df.index,
        count,
        replace=False
    )

    df.loc[indexes, column] = np.nan


# Inconsistent category formatting

indexes = np.random.choice(
    df.index,
    100,
    replace=False
)

for index in indexes:

    if pd.notna(df.loc[index, "Category"]):

        df.loc[index, "Category"] = (
            " "
            + str(df.loc[index, "Category"]).lower()
            + " "
        )


# Inconsistent payment formatting

indexes = np.random.choice(
    df.index,
    80,
    replace=False
)

for index in indexes:

    if pd.notna(df.loc[index, "Payment Method"]):

        df.loc[index, "Payment Method"] = (
            str(df.loc[index, "Payment Method"]).upper()
        )


# Incorrect totals

indexes = np.random.choice(
    df.index,
    75,
    replace=False
)

df.loc[indexes, "Total Spent"] = (
    df.loc[indexes, "Price Per Unit"]
    * df.loc[indexes, "Quantity"]
    * 1.5
).round(2)


# Duplicate records

duplicates = df.sample(
    35,
    random_state=7
)

df = pd.concat(
    [df, duplicates],
    ignore_index=True
)


# Shuffle the data

df = df.sample(
    frac=1,
    random_state=42
).reset_index(drop=True)


# -----------------------------
# SAVE RAW DATA
# -----------------------------

df.to_csv(
    "retail_store_sales_dirty.csv",
    index=False
)

print("Raw dataset created successfully!")
print("Rows:", len(df))
print("Columns:", len(df.columns))
