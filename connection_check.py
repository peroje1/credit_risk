from sqlalchemy import create_engine, text
#localhost is only for manual running, to check docker connection use db instead
engine = create_engine("mysql+pymysql://risk_user:StrongPass123!@localhost:3306/credit_risk")

try:
    with engine.connect() as conn:
        result = conn.execute(text("SELECT 1")).fetchone()
        print("Connection successful, result:", result[0])
except Exception as e:
    print("Connection failed:", e)
