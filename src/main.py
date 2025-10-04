# src/main.py
import os, sys, json, argparse, traceback
import pandas as pd
from src.load_data import load_all
from src.calculate import run_model

def resolve_mysql_url(cfg):
    url = os.getenv("MYSQL_CONNECTION") or cfg.get("mysql_connection")
    if not url:
        print("MYSQL_CONNECTION not provided.", file=sys.stderr)
        sys.exit(2)
    #debuging
    print("1111111111111")
    print(url)
    print("1111111111111")
    return url
#reads customer_csv, takes the latest value in the 'date'
def resolve_calc_date(args, cfg):
    if args.calc_date:
        return pd.to_datetime(args.calc_date).date().isoformat()
    # auto-detect from customer.csv
    df = pd.read_csv(cfg["customer_csv"], parse_dates=["date"])
    return df["date"].max().date().isoformat()
#script runner
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", default="config.json")
    ap.add_argument("--calc-date", help="YYYY-MM-DD (optional)")
    args = ap.parse_args()

    with open(args.config) as f:
        cfg = json.load(f)

    cfg["mysql_connection"] = resolve_mysql_url(cfg)
    cfg["calc_date"] = resolve_calc_date(args, cfg)

    print(f"[RUN] Pipeline start for {cfg['calc_date']}")
    load_all(cfg)

    try:
        run_model(cfg)
        print("[RUN] Done.")
    except Exception:
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
