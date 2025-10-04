import pandas as pd
import os
from sqlalchemy import create_engine, text

#load df into table, overwrite rows for calc_date and append new data
def _load_table(df: pd.DataFrame, table: str, engine, calc_date: str):
    df = df.copy()
    df["date"] = pd.to_datetime(calc_date)   #to use only last day of the month for calc
    with engine.begin() as conn:
        conn.execute(text(f"DELETE FROM {table} WHERE date = :d"), {"d": calc_date})
    df.to_sql(table, engine, if_exists="append", index=False)
    print(f"[LOAD] {table}: {len(df)} rows for {calc_date}")

#load all CSV files into MySQL tables for the given calc_date
def load_all(config: dict):
    MYSQL_CONNECTION = os.getenv(
        "MYSQL_CONNECTION",
        config["mysql_connection"]
    )

    engine = create_engine(MYSQL_CONNECTION)
    calc_date = config["calc_date"]

    customer = pd.read_csv(config["customer_csv"], parse_dates=["date", "birth_date"])
    credit   = pd.read_csv(config["credit_csv"],   parse_dates=["date"])
    income   = pd.read_csv(config["income_csv"],   parse_dates=["date", "income_date"])
    overdue  = pd.read_csv(config["overdue_csv"],  parse_dates=["date", "overdue_date"])

    _load_table(customer, "customer",      engine, calc_date)
    _load_table(credit,   "credit_bureau", engine, calc_date)
    _load_table(income,   "income",        engine, calc_date)
    _load_table(overdue,  "overdue",       engine, calc_date)

    print("All tables loaded.")
