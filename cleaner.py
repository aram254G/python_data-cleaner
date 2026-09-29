
import pandas as pd

# Load customer data
df = pd.read_csv("messy_customers.csv")

# Clean customer names
df["name"] = (
    df["name"]
    .str.strip()
    .str.split()
    .str.join(" ")
    .str.title()
)

# Normalize email addresses
df["email"] = df["email"].str.strip().str.lower()

# Remove duplicate emails
df = df.drop_duplicates(subset=["email"])

# Save the cleaned data
df.to_csv("cleaned_customers.csv", index=False)

print("Cleaning completed successfully!")
print(df)
