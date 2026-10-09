
from pathlib import Path
import pandas as pd

INPUT_FILE = Path("retail_store_sales_dirty.csv")
OUTPUT_FILE = Path("cleaned_retail_sales.csv")
ISSUES_FILE = Path("cleaning_issues.csv")

REQUIRED_COLUMNS = [
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
    "Discount Applied",
]

issues = []


def record_issue(df, mask, column, reason, original_values=None):
    """Record data problems and the actions taken."""
    mask = pd.Series(mask, index=df.index).fillna(False).astype(bool)

    for idx in df.index[mask]:
        original = (
            original_values.loc[idx]
            if original_values is not None
            else None
        )

        issues.append({
            "Source Row": df.at[idx, "Source Row"],
            "Transaction ID": df.at[idx, "Transaction ID"],
            "Column": column,
            "Original Value": original,
            "Issue": reason,
        })


def main():
    global issues
    issues = []

    print("Loading dataset...")

    if not INPUT_FILE.exists():
        raise FileNotFoundError(
            f"Input file not found: {INPUT_FILE}"
        )

    df = pd.read_csv(INPUT_FILE)

    print(f"Rows loaded: {len(df)}")
    print(f"Columns loaded: {len(df.columns)}")

    missing_columns = [
        col for col in REQUIRED_COLUMNS
        if col not in df.columns
    ]

    if missing_columns:
        raise ValueError(
            f"Required columns missing: {missing_columns}"
        )

    # Preserve original CSV row numbers for the audit trail.
    df.insert(0, "Source Row", range(2, len(df) + 2))

    # --------------------------------------------------
    # 1. Convert numeric columns safely
    # --------------------------------------------------
    numeric_columns = [
        "Price Per Unit",
        "Quantity",
        "Total Spent",
    ]

    for column in numeric_columns:
        original = df[column].copy()
        converted = pd.to_numeric(original, errors="coerce")

        failed = original.notna() & converted.isna()

        record_issue(
            df,
            failed,
            column,
            "Value could not be converted to a number; left unknown.",
            original,
        )

        df[column] = converted

    # --------------------------------------------------
    # 2. Remove exact duplicate transactions
    # --------------------------------------------------
    duplicate_mask = df.duplicated(
        subset=REQUIRED_COLUMNS,
        keep="first",
    )

    duplicate_count = int(duplicate_mask.sum())

    record_issue(
        df,
        duplicate_mask,
        "Entire row",
        "Exact duplicate row removed.",
    )

    df = df.loc[~duplicate_mask].copy()

    # --------------------------------------------------
    # 3. Standardize text fields
    # --------------------------------------------------
    text_columns = [
        "Transaction ID",
        "Customer ID",
        "Category",
        "Item",
        "Payment Method",
        "Location",
    ]

    for column in text_columns:
        df[column] = (
            df[column]
            .astype("string")
            .str.strip()
            .replace("", pd.NA)
        )

    # Normalize capitalization consistently.
    for column in ["Category", "Payment Method", "Location"]:
        df[column] = df[column].str.title()

    # Keep missing descriptive values explicit.
    for column in [
        "Transaction ID",
        "Customer ID",
        "Category",
        "Item",
        "Payment Method",
        "Location",
    ]:
        df[column] = df[column].fillna("Unknown")

    # --------------------------------------------------
    # 4. Recover missing prices conservatively
    # --------------------------------------------------
    invalid_price = df["Price Per Unit"].notna() & (
        df["Price Per Unit"] <= 0
    )

    record_issue(
        df,
        invalid_price,
        "Price Per Unit",
        "Price was zero or negative; marked unknown.",
        df["Price Per Unit"].copy(),
    )

    df.loc[invalid_price, "Price Per Unit"] = float("nan")

    missing_price_before = df["Price Per Unit"].isna()

    # Only recover a price when an item has exactly one
    # known positive price in the remaining dataset.
    known_prices = df.loc[
        df["Price Per Unit"].notna(),
        ["Item", "Price Per Unit"],
    ]

    price_counts = known_prices.groupby("Item")[
        "Price Per Unit"
    ].nunique()

    reliable_items = price_counts[price_counts == 1].index

    price_lookup = (
        known_prices[known_prices["Item"].isin(reliable_items)]
        .drop_duplicates("Item")
        .set_index("Item")["Price Per Unit"]
    )

    recovered_prices = df["Item"].map(price_lookup)

    recover_mask = (
        missing_price_before
        & recovered_prices.notna()
        & (df["Item"] != "Unknown")
    )

    df.loc[recover_mask, "Price Per Unit"] = recovered_prices[
        recover_mask
    ]

    recovered_price_count = int(recover_mask.sum())

    unresolved_price = df["Price Per Unit"].isna()

    record_issue(
        df,
        unresolved_price,
        "Price Per Unit",
        "Price remains unknown; reliable evidence was unavailable.",
    )

    # --------------------------------------------------
    # 5. Validate quantities without guessing
    # --------------------------------------------------
    quantity = df["Quantity"]

    valid_quantity = (
        quantity.notna()
        & (quantity >= 1)
        & (quantity <= 10)
        & (quantity % 1 == 0)
    )

    invalid_quantity = quantity.notna() & ~valid_quantity

    record_issue(
        df,
        invalid_quantity,
        "Quantity",
        "Quantity is outside the expected range or is not a whole number; left unknown.",
        quantity.copy(),
    )

    df.loc[invalid_quantity, "Quantity"] = float("nan")

    missing_quantity = df["Quantity"].isna()

    record_issue(
        df,
        missing_quantity,
        "Quantity",
        "Quantity is missing; verify against a trusted source.",
    )

    quantity_review_count = int(missing_quantity.sum())

    # --------------------------------------------------
    # 6. Validate and correct transaction totals
    # --------------------------------------------------
    price = df["Price Per Unit"]
    quantity = df["Quantity"]
    total = df["Total Spent"]

    expected_total = price * quantity

    verifiable = price.notna() & quantity.notna()

    incorrect_total = (
        verifiable
        & total.notna()
        & ~(
            (total - expected_total).abs()
            <= 0.01
        )
    )

    original_totals = total.copy()

    record_issue(
        df,
        incorrect_total,
        "Total Spent",
        "Total disagreed with price multiplied by quantity; corrected.",
        original_totals,
    )

    df.loc[incorrect_total, "Total Spent"] = expected_total[
        incorrect_total
    ]

    corrected_total_count = int(incorrect_total.sum())

    # Fill missing totals only when both inputs are known.
    missing_fillable_total = verifiable & df["Total Spent"].isna()

    record_issue(
        df,
        missing_fillable_total,
        "Total Spent",
        "Missing total calculated from known price and quantity.",
        original_totals,
    )

    df.loc[missing_fillable_total, "Total Spent"] = expected_total[
        missing_fillable_total
    ]

    unverifiable_total = (
        df["Total Spent"].notna()
        & ~verifiable
    )

    record_issue(
        df,
        unverifiable_total,
        "Total Spent",
        "Existing total could not be verified because price or quantity is unresolved.",
    )

    # --------------------------------------------------
    # 7. Normalize Discount Applied correctly
    # --------------------------------------------------
    original_discount = df["Discount Applied"].copy()

    # Numeric source values such as 0.0 and 1.0 are valid.
    # Text forms such as "yes", "no", "true", and "false"
    # are also accepted.
    discount_text = (
        original_discount
        .astype("string")
        .str.strip()
        .str.lower()
    )

    discount_numeric = pd.to_numeric(
        original_discount,
        errors="coerce",
    )

    false_values = {"0", "0.0", "false", "no", "n"}
    true_values = {"1", "1.0", "true", "yes", "y"}

    is_false = (
        discount_numeric.eq(0).fillna(False)
        | discount_text.isin(false_values)
    )

    is_true = (
        discount_numeric.eq(1).fillna(False)
        | discount_text.isin(true_values)
    )

    missing_discount = original_discount.isna()

    invalid_discount = (
        original_discount.notna()
        & ~is_false
        & ~is_true
    )

    record_issue(
        df,
        missing_discount,
        "Discount Applied",
        "Discount status is missing; no assumption made.",
        original_discount,
    )

    record_issue(
        df,
        invalid_discount,
        "Discount Applied",
        "Unrecognized discount value; left unknown.",
        original_discount,
    )

    # Nullable Boolean preserves missing values without
    # turning valid False values into missing values.
    normalized_discount = pd.Series(
        pd.NA,
        index=df.index,
        dtype="boolean",
    )

    normalized_discount.loc[is_false] = False
    normalized_discount.loc[is_true] = True

    df["Discount Applied"] = normalized_discount

    # --------------------------------------------------
    # 8. Parse transaction dates
    # --------------------------------------------------
    original_dates = df["Transaction Date"].copy()

    parsed_dates = pd.to_datetime(
        original_dates,
        errors="coerce",
    )

    invalid_dates = (
        original_dates.notna()
        & parsed_dates.isna()
    )

    missing_dates = original_dates.isna()

    record_issue(
        df,
        invalid_dates,
        "Transaction Date",
        "Invalid date; left unknown.",
        original_dates,
    )

    record_issue(
        df,
        missing_dates,
        "Transaction Date",
        "Transaction date is missing.",
        original_dates,
    )

    df["Transaction Date"] = parsed_dates

    # Use nullable integer storage for quantities.
    df["Quantity"] = df["Quantity"].astype("Int64")

    # --------------------------------------------------
    # 9. Final validation
    # --------------------------------------------------
    remaining_duplicates = int(
        df.duplicated(subset=REQUIRED_COLUMNS).sum()
    )

    missing_prices_remaining = int(
        df["Price Per Unit"].isna().sum()
    )

    missing_quantities_remaining = int(
        df["Quantity"].isna().sum()
    )

    missing_totals_remaining = int(
        df["Total Spent"].isna().sum()
    )

    invalid_dates_remaining = int(
        df["Transaction Date"].isna().sum()
    )

    verifiable_final = (
        df["Price Per Unit"].notna()
        & df["Quantity"].notna()
    )

    final_expected = (
        df["Price Per Unit"] * df["Quantity"]
    )

    incorrect_totals_remaining = int(
        (
            verifiable_final
            & df["Total Spent"].notna()
            & (
                (df["Total Spent"] - final_expected).abs()
                > 0.01
            )
        ).sum()
    )

    # --------------------------------------------------
    # 10. Save cleaned dataset and issue report
    # --------------------------------------------------
    cleaned_df = df.drop(columns=["Source Row"])

    cleaned_df.to_csv(OUTPUT_FILE, index=False)

    issues_df = pd.DataFrame(
        issues,
        columns=[
            "Source Row",
            "Transaction ID",
            "Column",
            "Original Value",
            "Issue",
        ],
    )

    issues_df.to_csv(ISSUES_FILE, index=False)

    print("\n" + "=" * 48)
    print("DATA CLEANING COMPLETED")
    print("=" * 48)
    print(f"Duplicate rows removed: {duplicate_count}")
    print(f"Missing prices recovered: {recovered_price_count}")
    print(f"Missing quantities requiring review: {quantity_review_count}")
    print(f"Incorrect totals corrected: {corrected_total_count}")
    print(f"Final rows: {len(cleaned_df)}")
    print(f"Final columns: {len(cleaned_df.columns)}")
    print(f"Duplicate rows remaining: {remaining_duplicates}")
    print(f"Missing prices remaining: {missing_prices_remaining}")
    print(f"Missing quantities remaining: {missing_quantities_remaining}")
    print(f"Missing totals remaining: {missing_totals_remaining}")
    print(f"Invalid or missing dates remaining: {invalid_dates_remaining}")
    print(
        "Incorrect totals remaining on verifiable rows: "
        f"{incorrect_totals_remaining}"
    )
    print(f"Issues recorded: {len(issues_df)}")
    print(f"Cleaned data saved to: {OUTPUT_FILE}")
    print(f"Issue report saved to: {ISSUES_FILE}")
    print("=" * 48)


if __name__ == "__main__":
    main()
