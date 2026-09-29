Python CSV Data Cleaner

A Python automation tool that transforms messy customer data into a clean, consistently formatted CSV file.

Features

- Removes unnecessary spaces from customer names.
- Standardizes name capitalization.
- Converts email addresses to lowercase.
- Removes duplicate records based on email addresses.
- Exports cleaned data to CSV.

Technologies

Python and pandas.

How to run

1. Install dependencies using "pip install -r requirements.txt".
2. Place "messy_customers.csv" in the project directory.
3. Run "python cleaner.py".
4. Find the results in "cleaned_customers.csv".

Example result

Four sample customer records are processed into three cleaned records.

Limitations

The current version expects name and email columns and does not yet handle missing values or validate email addresses.
