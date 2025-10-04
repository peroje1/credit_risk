from sqlalchemy import create_engine, text
import pandas as pd

_SQL_DELETE = """
DELETE FROM risk_results WHERE date = :calc_date;
"""

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
def run_model(config: dict):
    engine = create_engine(config["mysql_connection"])
    calc_date = pd.to_datetime(config["calc_date"]).strftime("%Y-%m-%d") # must use YYYY-MM-DD format
    with engine.begin() as conn:
        # we first delete old results
        conn.execute(text(_SQL_DELETE), {"calc_date": calc_date})
        # then add new results
        conn.execute(text(_SQL_INSERT), {"calc_date": calc_date})

    print(f"[CALC] Model calculation finished and results archived for {calc_date}.")
