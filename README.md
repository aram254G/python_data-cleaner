Retail Sales Data Cleaning with Python

A Python and Pandas project that cleans messy retail sales data, validates transaction totals, standardizes inconsistent values, and generates an audit report of data quality issues.

The Problem

Raw business data can contain duplicate transactions, missing values, inconsistent text formatting, and incorrect calculations. These problems can affect reporting and decision-making.

This project demonstrates a repeatable workflow for identifying and correcting data quality problems while preserving records that require further review.

What the Script Does

- Removes duplicate rows to reduce duplicate records.
- Standardizes text fields such as categories, payment methods, and locations.
- Handles missing prices using available item-price evidence where it is sufficiently consistent.
- Validates quantities and flags missing or invalid values for review.
- Checks transaction totals against price per unit multiplied by quantity.
- Corrects verifiable totals when the calculated amount differs from the recorded amount.
- Handles discount values consistently while preserving unknown values.
- Validates transaction dates and records invalid or missing dates.
- Generates an issue report documenting cleaning decisions and unresolved problems.

Tools Used

- Python
- Pandas
- CSV data processing

Validation Results

The demonstration dataset contained 5,035 rows before cleaning.

Quality check| Result
Rows loaded| 5,035
Duplicate rows removed| 35
Rows retained| 5,000
Duplicate rows remaining| 0
Transactions with verifiable totals| 4,939
Incorrect totals among verifiable transactions| 0
Missing quantities requiring review| 60
Missing prices remaining| 1
Issue records generated| 1,433

The cleaned dataset contains 2,883 transactions with "False" discount values, 916 with "True", and 1,201 with unknown discount values.

These results are from a validation run on the demonstration dataset. Unknown values are preserved rather than filled with unsupported assumptions.

Output Files

"cleaned_retail_sales.csv"

Contains the cleaned retail sales data for further analysis, reporting, or import into another system.

"cleaning_issues.csv"

Contains an audit trail of detected issues and cleaning decisions, including removed duplicates, corrected totals, and values that could not safely be recovered.

How to Run

1. Install Python and Pandas.

pip install pandas

2. Place "cleaner.py" and "retail_store_sales_dirty.csv" in the same directory, run python messy.py to generate the sample dataset, then python cleaner.py to clean it.
3. Run the script.

python cleaner.py

4. Review the generated files:

cleaned_retail_sales.csv
cleaning_issues.csv

The script checks the input data, applies the cleaning rules, and prints a summary of the results.

Data Quality Principles

This project follows three principles:

1. Correct what can be verified.
2. Preserve uncertainty instead of guessing.
3. Record cleaning decisions so results can be reviewed.

For example, a missing quantity is not inferred from a transaction total alone because the total itself may be incorrect. Such records remain flagged for verification against a trusted source.

Possible Applications

This workflow can serve as a starting point for:

- Cleaning retail transaction exports.
- Preparing CSV files for analysis.
- Identifying duplicate records.
- Validating calculated fields.
- Producing data quality reports for business review.

Real-world datasets may require additional business-specific validation rules.

Project Files

python_data-cleaner/
├── cleaner.py
├── messy.py
├── retail_store_sales_dirty.csv
├── cleaned_retail_sales.csv
├── cleaning_issues.csv
└── README.md

Note: Include only the files you intend to publish. The input generator "messy.py" is optional, and generated CSV files can be omitted from version control if you document how to reproduce them.

Summary

This project demonstrates practical Python data cleaning, validation, error handling, and audit reporting on a retail sales dataset. Its goal is not to hide every data problem, but to produce cleaner data and make unresolved issues visible.
