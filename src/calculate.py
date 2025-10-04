from sqlalchemy import create_engine, text
import pandas as pd
import os

_SQL_DELETE = """
DELETE FROM risk_results WHERE date = :calc_date;
"""

## insert calculated credit risk results for each customer on a given calc_date.
## the query joins credit_bureau, customer, income (last 3 months), and overdue data
## to compute a risk score and probability (using a logistic regression formula).
## the score is based on: gender, installment-to-income ratio, and days past due.

_SQL_INSERT = """
INSERT INTO risk_results (date, customer_id, score, probability)
SELECT 
    :calc_date AS date,
    cb.customer_id,
    (
      -5.0
      + 0.5 * IF(c.sex = 'M', 1, 0)
      + 2.5 * (
                 cb.installment_amount * 3 
                 / (CASE 
                        WHEN COALESCE(sum_inc.main_income_3m, 0) = 0 
                        THEN 3000 
                        ELSE sum_inc.main_income_3m 
                    END)
               )
      + 2.0 * LN(1 + COALESCE(dpd.days_past_due, 0))
    ) AS score,
    1 / (1 + EXP(-(
      -5.0
      + 0.5 * IF(c.sex = 'M', 1, 0)
      + 2.5 * (
                 cb.installment_amount * 3 
                 / (CASE 
                        WHEN COALESCE(sum_inc.main_income_3m, 0) = 0 
                        THEN 3000 
                        ELSE sum_inc.main_income_3m 
                    END)
               )
      + 2.0 * LN(1 + COALESCE(dpd.days_past_due, 0))
    ))) AS probability
FROM credit_bureau AS cb
JOIN customer AS c 
    ON cb.date = c.date AND cb.customer_id = c.customer_id
LEFT JOIN (
    SELECT customer_id, SUM(income_amount) AS main_income_3m
    FROM income
    WHERE date = :calc_date
      AND income_type IN (1, 2)
      AND income_date >= DATE_SUB(DATE_FORMAT(:calc_date, '%Y-%m-01'), INTERVAL 2 MONTH)
      AND income_date <= :calc_date
    GROUP BY customer_id
) AS sum_inc
    ON sum_inc.customer_id = cb.customer_id
LEFT JOIN (
    SELECT customer_id, DATEDIFF(:calc_date, overdue_date) AS days_past_due
    FROM overdue
    WHERE date = :calc_date
) AS dpd
    ON dpd.customer_id = cb.customer_id
WHERE cb.date = :calc_date;
"""

# run the model: delete old results, insert new ones, and export full results to CSV
def run_model(config: dict):
    engine = create_engine(config["mysql_connection"])
    calc_date = pd.to_datetime(config["calc_date"]).strftime("%Y-%m-%d")

    with engine.begin() as conn:
        # delete old results and insert new ones
        conn.execute(text(_SQL_DELETE), {"calc_date": calc_date})
        conn.execute(text(_SQL_INSERT), {"calc_date": calc_date})

    # export all results for this date to CSV
    os.makedirs("results", exist_ok=True)
    query = f"""
        SELECT * FROM risk_results 
        WHERE date = '{calc_date}' 
        ORDER BY probability DESC;
    """
    df = pd.read_sql(query, con=engine)
    output_path = f"results/risk_results_full_{calc_date}.csv"
    df.to_csv(output_path, index=False)

    print(f"[CALC] Model calculation finished and results exported to {output_path}.")
