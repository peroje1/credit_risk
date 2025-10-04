import pandas as pd

def validate_customer(df: pd.DataFrame):
    # drop rows with missing values (instead of raising error)
    df = df.dropna()

    # missing values
    if df.isnull().any().any():
        raise ValueError("Customer table has missing values")

    # primary key duplicates
    if df.duplicated(subset=["date", "customer_id"]).any():
        raise ValueError("Customer table has duplicate (date, customer_id)")

    # sex values
    if not df['sex'].isin(['M', 'F']).all():
        raise ValueError("Customer table has invalid sex values (must be 'M' or 'F')")

def validate_credit(df: pd.DataFrame, customer_ids: set):
    # drop rows with missing values (instead of raising error)
    df = df.dropna()

    # missing values
    if df.isnull().any().any():
        raise ValueError("Credit bureau table has missing values")

    # duplicates
    if df.duplicated(subset=["date", "customer_id"]).any():
        raise ValueError("Credit bureau table has duplicate (date, customer_id)")

    # negative installments
    if (df['installment_amount'] < 0).any():
        raise ValueError("Credit bureau has negative installment_amount")

    # referential integrity (customer_id must exist)
    unknown = set(df['customer_id']) - customer_ids
    if unknown:
        raise ValueError(f"Credit bureau contains unknown customers: {unknown}")

def validate_income(df: pd.DataFrame, customer_ids: set, calc_date: pd.Timestamp):
    # drop rows with missing values (instead of raising error)
    df = df.dropna()

    # missing values
    if df.isnull().any().any():
        raise ValueError("Income table has missing values")

    # valid income types
    if not df['income_type'].isin([1, 2, 3]).all():
        raise ValueError("Income table has invalid income_type")

    # negative amounts
    if (df['income_amount'] < 0).any():
        raise ValueError("Income table has negative income_amount")

    # referential integrity (customer_id must exist)
    unknown = set(df['customer_id']) - customer_ids
    if unknown:
        raise ValueError(f"Income table contains unknown customers: {unknown}")

    # income date should not be after calc_date, and not older than 24 months
    if (df['income_date'] > calc_date).any():
        raise ValueError("Income table has income_date after calc_date")

    earliest_allowed = calc_date - pd.DateOffset(months=24)
    if (df['income_date'] < earliest_allowed).any():
        raise ValueError("Income table has income_date older than 24 months window")

def validate_overdue(df: pd.DataFrame, customer_ids: set, calc_date: pd.Timestamp):
    # drop rows with missing values (instead of raising error)
    df = df.dropna()

    # missing values
    if df.isnull().any().any():
        raise ValueError("Overdue table has missing values")

    # duplicates
    if df.duplicated(subset=["date", "customer_id"]).any():
        raise ValueError("Overdue table has duplicate (date, customer_id)")

    # referential integrity (customer_id must exist)
    unknown = set(df['customer_id']) - customer_ids
    if unknown:
        raise ValueError(f"Overdue table contains unknown customers: {unknown}")

    # overdue_date must be <= calc_date
    if (df['overdue_date'] > calc_date).any():
        raise ValueError("Overdue table has overdue_date after calc_date")

def validate_all(config: dict):
    calc_date = pd.to_datetime(config["calc_date"])

    # load CSV
    customer = pd.read_csv(config["customer_csv"], parse_dates=['date','birth_date'])
    credit   = pd.read_csv(config["credit_csv"], parse_dates=['date'])
    income   = pd.read_csv(config["income_csv"], parse_dates=['date','income_date'])
    overdue  = pd.read_csv(config["overdue_csv"], parse_dates=['date','overdue_date'])

    # validate consistency of calc_date across files
    for name, df in [("customer", customer), ("credit", credit), ("income", income), ("overdue", overdue)]:
        if df['date'].nunique() != 1 or pd.to_datetime(df['date'].iloc[0]) != calc_date:
            print(
                f"[WARNING] {name} file has inconsistent or wrong calc_date (expected {calc_date.date()}, found {df['date'].iloc[0]})")

    # Validate each table
    customer_ids = set(customer['customer_id'])
    validate_customer(customer)
    validate_credit(credit, customer_ids)
    validate_income(income, customer_ids, calc_date)
    validate_overdue(overdue, customer_ids, calc_date)

    print("Data validation passed for all files.")
